import os
import re

import cv2
import numpy as np

from paddleocr import TextRecognition


# ==========================================================
# GLOBAL OCR MODELS
# ==========================================================

_paddle_model = None
_easyocr_reader = None


def _get_paddle_model():
    global _paddle_model

    if _paddle_model is None:
        print("[OCR] Loading PaddleOCR model...")

        _paddle_model = TextRecognition(
            model_name="PP-OCRv5_server_rec"
        )

    return _paddle_model


def _get_easyocr_reader():
    global _easyocr_reader

    if _easyocr_reader is None:
        try:
            import easyocr

            print("[OCR] Loading EasyOCR fallback...")

            _easyocr_reader = easyocr.Reader(
                ["en"],
                gpu=False,
                verbose=False
            )

        except Exception as error:
            print(
                "[OCR] EasyOCR tidak tersedia:",
                error
            )

            return None

    return _easyocr_reader


# ==========================================================
# NORMALIZATION
# ==========================================================

def _normalize_text(text):
    if not text:
        return None

    text = str(text).strip()

    # Hapus whitespace
    text = re.sub(
        r"\s+",
        "",
        text
    )

    # Normalisasi simbol perkalian
    text = text.replace(
        "×",
        "*"
    )

    text = text.replace(
        "X",
        "*"
    )

    text = text.replace(
        "x",
        "*"
    )

    # Jangan buang operator matematika
    text = re.sub(
        r"[^A-Za-z0-9+\-*/=?]",
        "",
        text
    )

    if not text:
        return None

    return text


# ==========================================================
# UPSCALE
# ==========================================================

def _upscale(
    image,
    scale=3
):
    return cv2.resize(
        image,
        None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_CUBIC
    )


# ==========================================================
# PREPROCESSING
# ==========================================================

def _create_variants(image):
    variants = {}

    # ------------------------------------------------------
    # ORIGINAL UPSCALED
    # ------------------------------------------------------

    upscaled = _upscale(
        image,
        scale=3
    )

    variants["original"] = upscaled

    # ------------------------------------------------------
    # GRAYSCALE
    # ------------------------------------------------------

    gray = cv2.cvtColor(
        upscaled,
        cv2.COLOR_BGR2GRAY
    )

    variants["gray"] = gray

    # ------------------------------------------------------
    # CONTRAST
    # ------------------------------------------------------

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    contrast = clahe.apply(
        gray
    )

    variants["contrast"] = contrast

    # ------------------------------------------------------
    # OTSU
    # ------------------------------------------------------

    _, otsu = cv2.threshold(
        contrast,
        0,
        255,
        cv2.THRESH_BINARY
        + cv2.THRESH_OTSU
    )

    variants["otsu"] = otsu

    # ------------------------------------------------------
    # OTSU INVERTED
    # ------------------------------------------------------

    _, otsu_inverted = cv2.threshold(
        contrast,
        0,
        255,
        cv2.THRESH_BINARY_INV
        + cv2.THRESH_OTSU
    )

    variants[
        "otsu_inverted"
    ] = otsu_inverted

    # ------------------------------------------------------
    # ADAPTIVE THRESHOLD
    # ------------------------------------------------------

    adaptive = cv2.adaptiveThreshold(
        contrast,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        7
    )

    variants["adaptive"] = adaptive

    # ------------------------------------------------------
    # SHARPEN
    # ------------------------------------------------------

    sharpen_kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])

    sharpened = cv2.filter2D(
        upscaled,
        -1,
        sharpen_kernel
    )

    variants["sharpen"] = sharpened

    # ------------------------------------------------------
    # HSV
    # ------------------------------------------------------

    hsv = cv2.cvtColor(
        upscaled,
        cv2.COLOR_BGR2HSV
    )

    # ------------------------------------------------------
    # SATURATION MASK
    # ------------------------------------------------------

    saturation = hsv[:, :, 1]

    _, saturation_mask = cv2.threshold(
        saturation,
        70,
        255,
        cv2.THRESH_BINARY
    )

    saturation_clean = (
        255 - saturation_mask
    )

    variants[
        "saturation_mask"
    ] = saturation_clean

    # ------------------------------------------------------
    # BLUE MASK
    # ------------------------------------------------------

    lower_blue = np.array([
        85,
        50,
        40
    ])

    upper_blue = np.array([
        145,
        255,
        255
    ])

    blue_mask = cv2.inRange(
        hsv,
        lower_blue,
        upper_blue
    )

    blue_clean = (
        255 - blue_mask
    )

    variants[
        "blue_mask"
    ] = blue_clean

    return variants


# ==========================================================
# SAVE DEBUG VARIANTS
# ==========================================================

def _save_debug_variants(
    variants,
    output_dir
):
    os.makedirs(
        output_dir,
        exist_ok=True
    )

    for name, image in variants.items():
        output_path = os.path.join(
            output_dir,
            f"{name}.png"
        )

        cv2.imwrite(
            output_path,
            image
        )


# ==========================================================
# PADDLE OCR
# ==========================================================

def _recognize_paddle(
    image_path
):
    model = _get_paddle_model()

    candidates = []

    try:
        output = model.predict(
            input=image_path,
            batch_size=1
        )

        for result in output:
            try:
                data = result.json

                if callable(data):
                    data = data()

            except Exception:
                continue

            if not isinstance(
                data,
                dict
            ):
                continue

            result_data = data.get(
                "res",
                {}
            )

            text = result_data.get(
                "rec_text"
            )

            confidence = result_data.get(
                "rec_score",
                0.0
            )

            normalized = (
                _normalize_text(
                    text
                )
            )

            if not normalized:
                continue

            try:
                confidence = float(
                    confidence
                )

            except Exception:
                confidence = 0.0

            candidates.append({
                "text": normalized,
                "confidence": confidence,
                "engine": "paddle",
            })

    except Exception as error:
        print(
            "[OCR][Paddle] Error:",
            error
        )

    return candidates


# ==========================================================
# EASYOCR
# ==========================================================

def _recognize_easyocr(
    image_path
):
    reader = (
        _get_easyocr_reader()
    )

    if reader is None:
        return []

    candidates = []

    try:
        results = reader.readtext(
            image_path,
            detail=1,
            paragraph=False,
            allowlist=(
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                "abcdefghijklmnopqrstuvwxyz"
                "0123456789"
                "+-*/=?"
            )
        )

        for item in results:
            if len(item) < 3:
                continue

            text = item[1]
            confidence = item[2]

            normalized = (
                _normalize_text(
                    text
                )
            )

            if not normalized:
                continue

            try:
                confidence = float(
                    confidence
                )

            except Exception:
                confidence = 0.0

            candidates.append({
                "text": normalized,
                "confidence": confidence,
                "engine": "easyocr",
            })

    except Exception as error:
        print(
            "[OCR][EasyOCR] Error:",
            error
        )

    return candidates


# ==========================================================
# MATH DETECTION
# ==========================================================

def _is_math_candidate(text):
    if not text:
        return False

    return bool(
        re.search(
            r"-?\d+[\+\-\*/]-?\d+",
            text
        )
    )


# ==========================================================
# SHAPE SCORE
# ==========================================================

def _candidate_shape_score(text):
    if not text:
        return -20

    # ======================================================
    # MATH CAPTCHA
    # ======================================================

    if _is_math_candidate(text):
        score = 15

        if "=" in text:
            score += 2

        if "?" in text:
            score += 1

        return score

    # ======================================================
    # TEXT CAPTCHA
    # ======================================================

    length = len(text)

    score = 0

    if length < 4:
        return -15

    if 5 <= length <= 10:
        score += 6

    elif 4 <= length <= 12:
        score += 3

    else:
        score -= 4

    has_letter = any(
        char.isalpha()
        for char in text
    )

    has_digit = any(
        char.isdigit()
        for char in text
    )

    if (
        has_letter
        and has_digit
    ):
        score += 5

    elif has_letter:
        score += 1

    elif has_digit:
        score -= 2

    return score


# ==========================================================
# PLAUSIBILITY FILTER
# ==========================================================

def _is_plausible_candidate(text):
    if not text:
        return False

    # Math candidate tetap diperbolehkan
    if _is_math_candidate(text):
        return True

    if len(text) < 3:
        return False

    if len(text) > 20:
        return False

    return True


# ==========================================================
# CANDIDATE SELECTION
# ==========================================================

def _select_best_candidate(
    all_results
):
    if not all_results:
        return None

    grouped = {}

    # ======================================================
    # GROUP RESULTS
    # ======================================================

    for item in all_results:
        text = item["text"]

        if not _is_plausible_candidate(
            text
        ):
            continue

        key = text.lower()

        if key not in grouped:
            grouped[key] = {
                "texts": [],
                "count": 0,
                "confidence_sum": 0.0,
                "engines": set(),
                "variants": set(),
            }

        grouped[key][
            "texts"
        ].append(
            text
        )

        grouped[key][
            "count"
        ] += 1

        grouped[key][
            "confidence_sum"
        ] += item[
            "confidence"
        ]

        grouped[key][
            "engines"
        ].add(
            item["engine"]
        )

        grouped[key][
            "variants"
        ].add(
            item["variant"]
        )

    if not grouped:
        return None

    ranked = []

    # ======================================================
    # SCORE
    # ======================================================

    for _, data in grouped.items():
        text = data[
            "texts"
        ][0]

        count = data[
            "count"
        ]

        avg_confidence = (
            data[
                "confidence_sum"
            ]
            / count
        )

        score = 0

        # --------------------------------------------------
        # CONSENSUS
        # --------------------------------------------------

        score += (
            min(
                count,
                4
            )
            * 1.5
        )

        # --------------------------------------------------
        # CONFIDENCE
        # --------------------------------------------------

        score += (
            avg_confidence
            * 3.0
        )

        # --------------------------------------------------
        # SHAPE
        # --------------------------------------------------

        shape_score = (
            _candidate_shape_score(
                text
            )
        )

        score += shape_score

        # --------------------------------------------------
        # MATH BONUS
        # --------------------------------------------------

        is_math = (
            _is_math_candidate(
                text
            )
        )

        if is_math:
            score += 8

        # --------------------------------------------------
        # MULTI ENGINE
        # --------------------------------------------------

        if len(
            data["engines"]
        ) >= 2:
            score += 2.5

        # --------------------------------------------------
        # MULTI VARIANT
        # --------------------------------------------------

        variant_count = len(
            data["variants"]
        )

        if variant_count >= 2:
            score += 2

        if variant_count >= 4:
            score += 1

        # --------------------------------------------------
        # SHORT FRAGMENT PENALTY
        # --------------------------------------------------

        if (
            not is_math
            and len(text) < 4
        ):
            score -= 12

        # --------------------------------------------------
        # ALPHANUMERIC BONUS
        # --------------------------------------------------

        has_letter = any(
            char.isalpha()
            for char in text
        )

        has_digit = any(
            char.isdigit()
            for char in text
        )

        if (
            not is_math
            and has_letter
            and has_digit
        ):
            score += 2

        # --------------------------------------------------
        # NUMBER-ONLY PENALTY
        #
        # Penting agar kandidat seperti:
        # 21427 / 214427
        # kalah dari:
        # 21+42=?
        # --------------------------------------------------

        if (
            not is_math
            and text.isdigit()
        ):
            score -= 5

        # --------------------------------------------------
        # LONG NOISE PENALTY
        # --------------------------------------------------

        if (
            not is_math
            and len(text) > 12
        ):
            score -= 4

        ranked.append({
            "text": text,
            "score": score,
            "count": count,
            "confidence": avg_confidence,
            "engines": data[
                "engines"
            ],
            "variants": data[
                "variants"
            ],
            "shape_score": shape_score,
            "is_math": is_math,
        })

    if not ranked:
        return None

    ranked.sort(
        key=lambda item: (
            item["score"],
            item["confidence"]
        ),
        reverse=True
    )

    # ======================================================
    # PRINT RANKING
    # ======================================================

    print(
        "\n================================"
    )

    print(
        "      OCR CANDIDATE RANKING"
    )

    print(
        "================================"
    )

    for index, candidate in enumerate(
        ranked[:10],
        start=1
    ):
        captcha_kind = (
            "MATH"
            if candidate["is_math"]
            else "TEXT"
        )

        print(
            f"{index}. "
            f"{candidate['text']} "
            f"| type={captcha_kind} "
            f"| score={candidate['score']:.2f} "
            f"| votes={candidate['count']} "
            f"| conf={candidate['confidence']:.3f} "
            f"| shape={candidate['shape_score']:.2f}"
        )

        print(
            "   engines:",
            ", ".join(
                sorted(
                    candidate["engines"]
                )
            )
        )

        print(
            "   variants:",
            ", ".join(
                sorted(
                    candidate["variants"]
                )
            )
        )

    best = ranked[0]

    print(
        "\n[OCR] Best candidate:"
    )

    print(
        f"Text       : {best['text']}"
    )

    print(
        f"Type       : "
        f"{'MATH' if best['is_math'] else 'TEXT'}"
    )

    print(
        f"Score      : {best['score']:.2f}"
    )

    print(
        f"Confidence : {best['confidence']:.3f}"
    )

    print(
        f"Votes      : {best['count']}"
    )

    return best["text"]


# ==========================================================
# MAIN SOLVER
# ==========================================================

def solve_with_paddle(
    image_path,
    save_debug=True,
    use_easyocr=True
):
    print(
        "\n================================"
    )

    print(
        "      MULTI-VARIANT OCR"
    )

    print(
        "================================"
    )

    # ======================================================
    # READ IMAGE
    # ======================================================

    image = cv2.imread(
        image_path
    )

    if image is None:
        print(
            "[OCR] Gambar tidak dapat dibaca:"
        )

        print(
            image_path
        )

        return None

    print(
        "[OCR] Image shape:",
        image.shape
    )

    # ======================================================
    # PREPROCESSING
    # ======================================================

    variants = (
        _create_variants(
            image
        )
    )

    # ======================================================
    # DEBUG
    # ======================================================

    if save_debug:
        debug_dir = os.path.join(
            "outputs",
            "captcha_images",
            "debug"
        )

        _save_debug_variants(
            variants,
            debug_dir
        )

        print(
            "[OCR] Debug preprocessing:"
        )

        print(
            debug_dir
        )

    # ======================================================
    # TEMP DIRECTORY
    # ======================================================

    temp_dir = os.path.join(
        "outputs",
        "captcha_images",
        "ocr_temp"
    )

    os.makedirs(
        temp_dir,
        exist_ok=True
    )

    all_results = []

    # ======================================================
    # OCR ALL VARIANTS
    # ======================================================

    for (
        variant_name,
        variant_image
    ) in variants.items():

        temp_path = os.path.join(
            temp_dir,
            f"{variant_name}.png"
        )

        cv2.imwrite(
            temp_path,
            variant_image
        )

        print(
            f"\n[OCR] Variant: "
            f"{variant_name}"
        )

        # --------------------------------------------------
        # PADDLE
        # --------------------------------------------------

        paddle_results = (
            _recognize_paddle(
                temp_path
            )
        )

        for result in paddle_results:
            result[
                "variant"
            ] = variant_name

            all_results.append(
                result
            )

            print(
                "[Paddle]",
                result["text"],
                f"conf={result['confidence']:.3f}"
            )

        # --------------------------------------------------
        # EASYOCR
        # --------------------------------------------------

        if use_easyocr:
            easy_results = (
                _recognize_easyocr(
                    temp_path
                )
            )

            for result in easy_results:
                result[
                    "variant"
                ] = variant_name

                all_results.append(
                    result
                )

                print(
                    "[EasyOCR]",
                    result["text"],
                    f"conf={result['confidence']:.3f}"
                )

    # ======================================================
    # NO RESULTS
    # ======================================================

    if not all_results:
        print(
            "[OCR] Tidak ada kandidat OCR."
        )

        return None

    # ======================================================
    # SELECT BEST
    # ======================================================

    best = (
        _select_best_candidate(
            all_results
        )
    )

    print(
        "\n================================"
    )

    print(
        "        FINAL OCR RESULT"
    )

    print(
        "================================"
    )

    print(
        "Selected:",
        best
    )

    return best