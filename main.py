from playwright.sync_api import sync_playwright
import os
import re
import time

from browser.page_analyzer import PageAnalyzer
from interaction.form_handler import FormHandler

from solver.paddle_solver import solve_with_paddle
from solver.math_solver import solve_math_expression

from detector.captcha_detector import CaptchaDetector
from evaluation.metrics import MetricsLogger


# ==========================================================
# TEXT QUESTION SOLVER
# ==========================================================

def solve_text_question(question):
    """
    Rule-based solver untuk beberapa pola text CAPTCHA sederhana
    di environment demo/testing.

    Tidak mencoba menjawab pertanyaan bebas secara universal.
    """

    if not question:
        return None

    text = question.strip().lower()

    # ======================================================
    # WEEKDAYS
    # ======================================================

    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]

    # ------------------------------------------------------
    # If tomorrow is X, what day is today?
    # ------------------------------------------------------

    match = re.search(
        r"tomorrow\s+is\s+(monday|tuesday|wednesday|"
        r"thursday|friday|saturday|sunday)",
        text
    )

    if (
        match
        and "today" in text
    ):
        tomorrow = match.group(1)

        index = days.index(
            tomorrow
        )

        return days[
            (index - 1) % 7
        ].capitalize()

    # ------------------------------------------------------
    # If yesterday was X, what day is today?
    # ------------------------------------------------------

    match = re.search(
        r"yesterday\s+(?:was|is)\s+"
        r"(monday|tuesday|wednesday|thursday|"
        r"friday|saturday|sunday)",
        text
    )

    if (
        match
        and "today" in text
    ):
        yesterday = match.group(1)

        index = days.index(
            yesterday
        )

        return days[
            (index + 1) % 7
        ].capitalize()

    # ------------------------------------------------------
    # What day comes after X?
    # ------------------------------------------------------

    match = re.search(
        r"(?:after|comes after)\s+"
        r"(monday|tuesday|wednesday|thursday|"
        r"friday|saturday|sunday)",
        text
    )

    if match:
        day = match.group(1)

        index = days.index(
            day
        )

        return days[
            (index + 1) % 7
        ].capitalize()

    # ------------------------------------------------------
    # What day comes before X?
    # ------------------------------------------------------

    match = re.search(
        r"(?:before|comes before)\s+"
        r"(monday|tuesday|wednesday|thursday|"
        r"friday|saturday|sunday)",
        text
    )

    if match:
        day = match.group(1)

        index = days.index(
            day
        )

        return days[
            (index - 1) % 7
        ].capitalize()

    # ======================================================
    # SIMPLE TEXT MATH
    # ======================================================

    replacements = {
        " plus ": " + ",
        " minus ": " - ",
        " times ": " * ",
        " multiplied by ": " * ",
        " divided by ": " / ",
    }

    math_text = text

    for old, new in replacements.items():
        math_text = math_text.replace(
            old,
            new
        )

    match = re.search(
        r"(-?\d+)\s*([\+\-\*/])\s*(-?\d+)",
        math_text
    )

    if match:
        a = int(
            match.group(1)
        )

        operator = match.group(2)

        b = int(
            match.group(3)
        )

        if operator == "+":
            return a + b

        if operator == "-":
            return a - b

        if operator == "*":
            return a * b

        if operator == "/":
            if b == 0:
                return None

            result = a / b

            if result.is_integer():
                return int(result)

            return result

    return None


# ==========================================================
# RESULT VALIDATION
# ==========================================================

def detect_submission_result(page):
    try:
        body_text = (
            page.locator("body")
            .inner_text()
            .lower()
        )

    except Exception:
        return "UNKNOWN"

    failure_keywords = [
        "incorrect captcha",
        "wrong captcha",
        "captcha failed",
        "invalid captcha",
        "verification failed",
        "some errors were detected",
        "required field(s) are missing",
    ]

    success_keywords = [
        "captcha is passed",
        "success",
        "successfully",
        "thank you",
        "message has been sent",
        "correct captcha",
        "verification successful",
        "verified successfully",
    ]

    for keyword in failure_keywords:
        if keyword in body_text:
            return "FAILED"

    for keyword in success_keywords:
        if keyword in body_text:
            return "SUCCESS"

    return "UNKNOWN"


# ==========================================================
# SCREENSHOT
# ==========================================================

def capture_captcha(
    page,
    captcha_visual,
    captcha_path
):
    try:
        captcha_visual.scroll_into_view_if_needed(
            timeout=5000
        )

        page.wait_for_timeout(
            300
        )

        captcha_visual.screenshot(
            path=captcha_path,
            timeout=5000
        )

        return True

    except Exception:
        try:
            box = captcha_visual.bounding_box(
                timeout=5000
            )

        except Exception:
            box = None

        if box is None:
            return False

        if (
            box["width"] <= 0
            or box["height"] <= 0
        ):
            return False

        page.screenshot(
            path=captcha_path,
            clip={
                "x": box["x"],
                "y": box["y"],
                "width": box["width"],
                "height": box["height"],
            }
        )

        return True


# ==========================================================
# SUBMIT
# ==========================================================

def submit_form(
    page,
    submit_button
):
    try:
        submit_button.scroll_into_view_if_needed(
            timeout=3000
        )

        submit_button.click(
            timeout=5000
        )

    except Exception:
        try:
            submit_button.evaluate(
                "el => el.click()"
            )

        except Exception:
            return False

    try:
        page.wait_for_load_state(
            "domcontentloaded",
            timeout=5000
        )

    except Exception:
        pass

    page.wait_for_timeout(
        1500
    )

    return True


# ==========================================================
# MAIN
# ==========================================================

def main():
    print("\n================================")
    print("     GENERIC CAPTCHA BOT")
    print("================================")

    url = input(
        "Masukkan URL halaman test: "
    ).strip()

    if not url:
        print(
            "URL tidak boleh kosong."
        )
        return

    output_dir = (
        "outputs/captcha_images"
    )

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    captcha_path = os.path.join(
        output_dir,
        "current_captcha.png"
    )

    metrics = MetricsLogger()

    start_time = time.perf_counter()

    captcha_type = "unknown"
    ocr_text = None
    answer = None
    result = "UNKNOWN"

    challenge_text = None

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False
        )

        page = browser.new_page()

        try:
            # ==============================================
            # OPEN PAGE
            # ==============================================

            print("\n================================")
            print("          OPEN PAGE")
            print("================================")

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            print(
                "Title:",
                page.title()
            )

            page.wait_for_timeout(
                700
            )

            analyzer = PageAnalyzer(
                page
            )

            # ==============================================
            # BASIC FORM ELEMENTS
            # ==============================================

            print("\n================================")
            print("        PAGE ANALYZER")
            print("================================")

            captcha_input = (
                analyzer.find_captcha_input()
            )

            submit_button = (
                analyzer.find_submit_button()
            )

            if captcha_input is None:
                result = (
                    "CAPTCHA_INPUT_NOT_FOUND"
                )

                print(
                    "CAPTCHA input tidak ditemukan."
                )

                return

            if submit_button is None:
                result = (
                    "SUBMIT_NOT_FOUND"
                )

                print(
                    "Submit button tidak ditemukan."
                )

                return

            # ==============================================
            # DETECT TEXT QUESTION FIRST
            # ==============================================

            print(
                "\n[STEP] Mencari text challenge..."
            )

            challenge_text = (
                analyzer.find_text_challenge()
            )

            # ==================================================
            # MODE 1: TEXT QUESTION CAPTCHA
            # ==================================================

            if challenge_text:
                captcha_type = (
                    "text_question"
                )

                print(
                    "\n================================"
                )

                print(
                    "      TEXT QUESTION CAPTCHA"
                )

                print(
                    "================================"
                )

                print(
                    "Question:",
                    challenge_text
                )

                answer = solve_text_question(
                    challenge_text
                )

                if answer is None:
                    result = (
                        "TEXT_QUESTION_UNSUPPORTED"
                    )

                    print(
                        "Pertanyaan terdeteksi, "
                        "tetapi solver belum mendukung "
                        "pola tersebut."
                    )

                    return

                print(
                    "Answer:",
                    answer
                )

            # ==================================================
            # MODE 2 + 3: VISUAL CAPTCHA
            # ==================================================

            else:
                print(
                    "\n[STEP] Text challenge tidak ditemukan."
                )

                print(
                    "[STEP] Mencari visual CAPTCHA..."
                )

                captcha_visual = (
                    analyzer.find_captcha_image()
                )

                if captcha_visual is None:
                    result = (
                        "CAPTCHA_VISUAL_NOT_FOUND"
                    )

                    print(
                        "Visual CAPTCHA tidak ditemukan."
                    )

                    return

                # ----------------------------------------------
                # FORM HANDLER
                # ----------------------------------------------

                form_handler = FormHandler(
                    page
                )

                filled_fields = (
                    form_handler.fill_required_fields(
                        exclude=captcha_input
                    )
                )

                filled_fields += (
                    form_handler.fill_empty_textareas()
                )

                if filled_fields:
                    print(
                        "\nField tambahan yang diisi:"
                    )

                    for field in filled_fields:
                        print(
                            " -",
                            field
                        )

                # ----------------------------------------------
                # CAPTURE
                # ----------------------------------------------

                if not capture_captcha(
                    page,
                    captcha_visual,
                    captcha_path
                ):
                    result = (
                        "SCREENSHOT_FAILED"
                    )

                    print(
                        "Screenshot CAPTCHA gagal."
                    )

                    return

                # ----------------------------------------------
                # OCR
                # ----------------------------------------------

                print("\n================================")
                print("           OCR RESULT")
                print("================================")

                ocr_text = solve_with_paddle(
                    captcha_path
                )

                print(
                    "OCR:",
                    ocr_text
                )

                if not ocr_text:
                    result = "OCR_FAILED"
                    return

                # ----------------------------------------------
                # TYPE DETECTOR
                # ----------------------------------------------

                captcha_type = (
                    CaptchaDetector.detect_from_text(
                        ocr_text
                    )
                )

                print(
                    "Detected type:",
                    captcha_type
                )

                # ----------------------------------------------
                # IMAGE TEXT
                # ----------------------------------------------

                if (
                    captcha_type
                    == CaptchaDetector.TEXT
                ):
                    answer = ocr_text

                # ----------------------------------------------
                # IMAGE MATH
                # ----------------------------------------------

                elif (
                    captcha_type
                    == CaptchaDetector.MATH
                ):
                    answer = (
                        solve_math_expression(
                            ocr_text
                        )
                    )

                else:
                    result = (
                        "UNSUPPORTED_CAPTCHA"
                    )

                    print(
                        "Jenis CAPTCHA visual "
                        "belum dikenali."
                    )

                    return

            # ==============================================
            # FORM HANDLER FOR TEXT QUESTION
            # ==============================================

            if (
                captcha_type
                == "text_question"
            ):
                form_handler = FormHandler(
                    page
                )

                filled_fields = (
                    form_handler.fill_required_fields(
                        exclude=captcha_input
                    )
                )

                filled_fields += (
                    form_handler.fill_empty_textareas()
                )

                if filled_fields:
                    print(
                        "\nField tambahan yang diisi:"
                    )

                    for field in filled_fields:
                        print(
                            " -",
                            field
                        )

            # ==============================================
            # ANSWER VALIDATION
            # ==============================================

            if answer is None:
                result = "SOLVER_FAILED"
                return

            if (
                isinstance(answer, float)
                and answer.is_integer()
            ):
                answer = int(answer)

            # ==============================================
            # FILL
            # ==============================================

            print("\n================================")
            print("         FILL ANSWER")
            print("================================")

            captcha_input.fill(
                str(answer),
                timeout=5000
            )

            print(
                "Jawaban diisi:",
                answer
            )

            # ==============================================
            # SUBMIT
            # ==============================================

            if not submit_form(
                page,
                submit_button
            ):
                result = "SUBMIT_FAILED"
                return

            # ==============================================
            # VALIDATE
            # ==============================================

            result = (
                detect_submission_result(
                    page
                )
            )

            print("\n================================")
            print("         HASIL VALIDASI")
            print("================================")

            print(
                "Result:",
                result
            )

            print(
                "URL:",
                page.url
            )

        except Exception as error:
            result = "ERROR"

            print(
                "\nERROR:"
            )

            print(
                error
            )

        finally:
            elapsed = (
                time.perf_counter()
                - start_time
            )

            try:
                metrics.log(
                    url=url,
                    captcha_type=captcha_type,
                    ocr_result=(
                        ocr_text
                        if ocr_text
                        else challenge_text
                    ),
                    answer=answer,
                    result=result,
                    processing_time=elapsed
                )

            except Exception as error:
                print(
                    "Metrics error:",
                    error
                )

            print("\n================================")
            print("            SUMMARY")
            print("================================")

            print(
                "Captcha type:",
                captcha_type
            )

            if challenge_text:
                print(
                    "Challenge:",
                    challenge_text
                )

            print(
                "OCR:",
                ocr_text
            )

            print(
                "Answer:",
                answer
            )

            print(
                "Result:",
                result
            )

            print(
                f"Processing time: "
                f"{elapsed:.3f} detik"
            )

            print(
                "================================"
            )

            input(
                "\nTekan Enter untuk "
                "menutup browser..."
            )

            browser.close()


if __name__ == "__main__":
    main()