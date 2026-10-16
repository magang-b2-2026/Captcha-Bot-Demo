class PageAnalyzer:
    def __init__(self, page):
        self.page = page

    # ==========================================================
    # HELPER
    # ==========================================================

    def _get_visible_elements(self, selectors):
        elements = []

        for selector in selectors:
            locator = self.page.locator(selector)

            try:
                count = locator.count()
            except Exception:
                continue

            for i in range(count):
                candidate = locator.nth(i)

                try:
                    if candidate.is_visible():
                        elements.append(candidate)
                except Exception:
                    continue

        return elements

    # ==========================================================
    # CAPTCHA INPUT
    # ==========================================================

    def find_captcha_input(self):
        selectors = [
            'input[name*="captcha" i]',
            'input[id*="captcha" i]',
            'input[placeholder*="captcha" i]',

            'input[name*="verification" i]',
            'input[id*="verification" i]',
            'input[placeholder*="verification" i]',

            'input[name*="verify" i]',
            'input[id*="verify" i]',

            'input[name*="vericode" i]',
            'input[id*="vericode" i]',

            'input[name*="code" i]',
            'input[id*="code" i]',
            'input[placeholder*="code" i]',

            'input[name*="answer" i]',
            'input[id*="answer" i]',
            'input[placeholder*="answer" i]',
        ]

        candidates = self._get_visible_elements(
            selectors
        )

        if not candidates:
            print(
                "[Analyzer] CAPTCHA input tidak ditemukan."
            )
            return None

        candidate = candidates[0]

        try:
            description = (
                candidate.get_attribute("name")
                or candidate.get_attribute("id")
                or candidate.get_attribute("placeholder")
                or "unknown"
            )

            print(
                "[Analyzer] CAPTCHA input ditemukan:",
                description
            )

        except Exception:
            print(
                "[Analyzer] CAPTCHA input ditemukan."
            )

        return candidate

    # ==========================================================
    # TEXT QUESTION CAPTCHA
    # ==========================================================

    def find_text_challenge(self):
        """
        Mencari pertanyaan CAPTCHA berbasis teks yang berada
        di sekitar CAPTCHA input.

        Contoh:
        "If tomorrow is Saturday, what day is today?"
        """

        captcha_input = self.find_captcha_input()

        if captcha_input is None:
            return None

        try:
            input_box = captcha_input.bounding_box()
        except Exception:
            input_box = None

        if input_box is None:
            return None

        # Elemen teks yang masuk akal sebagai challenge
        locator = self.page.locator(
            "label, p, span, div, strong, b, small, "
            "h1, h2, h3, h4, h5, h6"
        )

        try:
            count = min(
                locator.count(),
                600
            )
        except Exception:
            return None

        best_text = None
        best_score = float("-inf")

        question_keywords = [
            "what",
            "which",
            "who",
            "when",
            "where",
            "how",
            "if ",
            "today",
            "tomorrow",
            "yesterday",
            "day",
            "answer",
        ]

        # Teks seperti ini biasanya instruksi input,
        # bukan challenge pertanyaan.
        instruction_keywords = [
            "enter text",
            "enter captcha",
            "enter code",
            "from the image",
            "recognize symbols",
            "captcha example",
            "captcha demo",
        ]

        for i in range(count):
            candidate = locator.nth(i)

            try:
                if not candidate.is_visible():
                    continue

                text = (
                    candidate.inner_text()
                    or ""
                ).strip()

                # Hindari container kosong / seluruh halaman
                if len(text) < 5:
                    continue

                if len(text) > 250:
                    continue

                lower = text.lower()

                # Jangan pilih instruksi biasa
                if any(
                    keyword in lower
                    for keyword in instruction_keywords
                ):
                    continue

                try:
                    box = candidate.bounding_box()
                except Exception:
                    box = None

                if box is None:
                    continue

                candidate_center_x = (
                    box["x"]
                    + box["width"] / 2
                )

                candidate_center_y = (
                    box["y"]
                    + box["height"] / 2
                )

                input_center_x = (
                    input_box["x"]
                    + input_box["width"] / 2
                )

                input_center_y = (
                    input_box["y"]
                    + input_box["height"] / 2
                )

                horizontal_distance = abs(
                    candidate_center_x
                    - input_center_x
                )

                vertical_distance = (
                    input_box["y"]
                    - box["y"]
                )

                distance = (
                    (
                        candidate_center_x
                        - input_center_x
                    ) ** 2
                    +
                    (
                        candidate_center_y
                        - input_center_y
                    ) ** 2
                ) ** 0.5

                score = 0

                # Pertanyaan jelas
                if "?" in text:
                    score += 10

                for keyword in question_keywords:
                    if keyword in lower:
                        score += 2

                # Prioritaskan teks dekat input
                score += max(
                    0,
                    12 - distance / 50
                )

                # Biasanya challenge berada di atas input
                if (
                    vertical_distance > 0
                    and vertical_distance < 350
                ):
                    score += 6

                if horizontal_distance < 400:
                    score += 2

                # Hindari teks yang terlalu pendek dan generik
                if len(text) < 10:
                    score -= 3

                if score > best_score:
                    best_score = score
                    best_text = text

            except Exception:
                continue

        # Threshold supaya tidak sembarang teks dianggap challenge
        if (
            best_text is not None
            and best_score >= 14
        ):
            print(
                "[Analyzer] Text challenge ditemukan:"
            )

            print(
                f"[Analyzer] {best_text}"
            )

            print(
                f"[Analyzer] Text challenge score: "
                f"{best_score:.2f}"
            )

            return best_text

        print(
            "[Analyzer] Text challenge tidak ditemukan."
        )

        return None

    # ==========================================================
    # GENERIC VISUAL CANDIDATES
    # ==========================================================

    def _get_visual_candidates(self):
        candidates = []

        # ------------------------------------------------------
        # IMG
        # ------------------------------------------------------

        images = self.page.locator("img")

        try:
            count = images.count()
        except Exception:
            count = 0

        for i in range(count):
            element = images.nth(i)

            try:
                if element.is_visible():
                    candidates.append(element)
            except Exception:
                continue

        # ------------------------------------------------------
        # CANVAS
        # ------------------------------------------------------

        canvases = self.page.locator("canvas")

        try:
            count = canvases.count()
        except Exception:
            count = 0

        for i in range(count):
            element = canvases.nth(i)

            try:
                if element.is_visible():
                    candidates.append(element)
            except Exception:
                continue

        # ------------------------------------------------------
        # SVG
        # ------------------------------------------------------

        svgs = self.page.locator("svg")

        try:
            count = svgs.count()
        except Exception:
            count = 0

        for i in range(count):
            element = svgs.nth(i)

            try:
                if element.is_visible():
                    candidates.append(element)
            except Exception:
                continue

        # ------------------------------------------------------
        # CSS BACKGROUND IMAGE
        # ------------------------------------------------------

        elements = self.page.locator(
            "div, span, p, section, label"
        )

        try:
            count = min(
                elements.count(),
                500
            )
        except Exception:
            count = 0

        for i in range(count):
            element = elements.nth(i)

            try:
                if not element.is_visible():
                    continue

                background = element.evaluate(
                    """
                    el => getComputedStyle(el).backgroundImage
                    """
                )

                if (
                    background
                    and background != "none"
                    and "url(" in background
                ):
                    candidates.append(element)

            except Exception:
                continue

        return candidates

    # ==========================================================
    # INTERNAL VISUAL CAPTCHA DETECTION
    # ==========================================================

    def _find_captcha_image_once(self):
        selectors = [
            'img[alt*="captcha" i]',
            'img[src*="captcha" i]',
            'img[id*="captcha" i]',
            'img[class*="captcha" i]',

            'img[alt*="verification" i]',
            'img[src*="verification" i]',

            'canvas[id*="captcha" i]',
            'canvas[class*="captcha" i]',

            'svg[id*="captcha" i]',
            'svg[class*="captcha" i]',
        ]

        candidates = self._get_visible_elements(
            selectors
        )

        captcha_input = self.find_captcha_input()

        input_box = None

        if captcha_input is not None:
            try:
                input_box = (
                    captcha_input.bounding_box()
                )
            except Exception:
                input_box = None

        if not candidates:
            candidates = (
                self._get_visual_candidates()
            )

        if not candidates:
            return None

        print(
            f"[Analyzer] {len(candidates)} "
            f"kandidat visual ditemukan."
        )

        best_candidate = None
        best_score = float("-inf")

        for index, candidate in enumerate(
            candidates
        ):
            try:
                box = candidate.bounding_box()

                if not box:
                    continue

                width = box["width"]
                height = box["height"]

                if width < 20 or height < 10:
                    continue

                score = 0

                # --------------------------------------------------
                # SIZE
                # --------------------------------------------------

                if width >= 60:
                    score += 2

                if height >= 20:
                    score += 2

                if width <= 500:
                    score += 1

                if height <= 200:
                    score += 1

                if width > 800:
                    score -= 5

                if height > 400:
                    score -= 5

                # --------------------------------------------------
                # TAG
                # --------------------------------------------------

                try:
                    tag_name = candidate.evaluate(
                        "el => el.tagName"
                    )
                except Exception:
                    tag_name = "UNKNOWN"

                if tag_name == "IMG":
                    score += 1

                if tag_name == "CANVAS":
                    score += 3

                # --------------------------------------------------
                # ATTRIBUTES
                # --------------------------------------------------

                alt = (
                    candidate.get_attribute("alt")
                    or ""
                )

                src = (
                    candidate.get_attribute("src")
                    or ""
                )

                element_id = (
                    candidate.get_attribute("id")
                    or ""
                )

                element_class = (
                    candidate.get_attribute("class")
                    or ""
                )

                attribute_text = (
                    alt
                    + " "
                    + src
                    + " "
                    + element_id
                    + " "
                    + element_class
                ).lower()

                if "captcha" in attribute_text:
                    score += 10

                if "verification" in attribute_text:
                    score += 5

                if "verify" in attribute_text:
                    score += 3

                if "code" in attribute_text:
                    score += 2

                # Penalti logo/banner
                logo_keywords = [
                    "logo",
                    "github",
                    "linkedin",
                    "youtube",
                    "payment",
                    "browser",
                ]

                if any(
                    word in attribute_text
                    for word in logo_keywords
                ):
                    score -= 12

                # --------------------------------------------------
                # POSITION
                # --------------------------------------------------

                if input_box:
                    visual_center_x = (
                        box["x"]
                        + width / 2
                    )

                    visual_center_y = (
                        box["y"]
                        + height / 2
                    )

                    input_center_x = (
                        input_box["x"]
                        + input_box["width"] / 2
                    )

                    input_center_y = (
                        input_box["y"]
                        + input_box["height"] / 2
                    )

                    horizontal_difference = abs(
                        visual_center_x
                        - input_center_x
                    )

                    vertical_difference = (
                        input_box["y"]
                        - box["y"]
                    )

                    distance = (
                        (
                            visual_center_x
                            - input_center_x
                        ) ** 2
                        +
                        (
                            visual_center_y
                            - input_center_y
                        ) ** 2
                    ) ** 0.5

                    score += max(
                        0,
                        15 - distance / 50
                    )

                    if (
                        vertical_difference > 0
                        and vertical_difference < 300
                    ):
                        score += 6

                    if horizontal_difference < 300:
                        score += 3

                    if horizontal_difference < 150:
                        score += 2

                print(
                    f"[Analyzer] Candidate "
                    f"{index + 1}: "
                    f"tag={tag_name} "
                    f"{width:.0f}x{height:.0f} "
                    f"score={score:.2f} "
                    f"alt='{alt}' "
                    f"src='{src[:60]}'"
                )

                if score > best_score:
                    best_score = score
                    best_candidate = candidate

            except Exception:
                continue

        # Threshold supaya icon kecil random tidak dianggap CAPTCHA
        if (
            best_candidate is None
            or best_score < 15
        ):
            return None

        print(
            "[Analyzer] CAPTCHA visual terbaik dipilih."
        )

        print(
            f"[Analyzer] Best score: "
            f"{best_score:.2f}"
        )

        return best_candidate

    # ==========================================================
    # VISUAL CAPTCHA + RETRY
    # ==========================================================

    def find_captcha_image(
        self,
        max_attempts=5,
        delay=0.6
    ):
        for attempt in range(
            1,
            max_attempts + 1
        ):
            print(
                f"[Analyzer] Mencari CAPTCHA visual "
                f"(attempt {attempt}/{max_attempts})..."
            )

            candidate = (
                self._find_captcha_image_once()
            )

            if candidate is not None:
                return candidate

            if attempt < max_attempts:
                self.page.wait_for_timeout(
                    int(delay * 1000)
                )

        print(
            "[Analyzer] CAPTCHA visual tidak ditemukan."
        )

        return None

    # ==========================================================
    # SUBMIT BUTTON
    # ==========================================================

    def find_submit_button(self):
        names = [
            "Verify",
            "Check",
            "Submit",
            "Send",
            "Continue",
            "Validate",
            "Confirm",
        ]

        for name in names:
            locator = self.page.get_by_role(
                "button",
                name=name,
                exact=False
            )

            try:
                count = locator.count()
            except Exception:
                continue

            for i in range(count):
                candidate = locator.nth(i)

                try:
                    if candidate.is_visible():
                        print(
                            "[Analyzer] Submit button "
                            "ditemukan:",
                            name
                        )

                        return candidate

                except Exception:
                    continue

        # Input type submit
        submit_inputs = self.page.locator(
            'input[type="submit"]'
        )

        try:
            count = submit_inputs.count()
        except Exception:
            count = 0

        for i in range(count):
            candidate = submit_inputs.nth(i)

            try:
                if candidate.is_visible():
                    print(
                        "[Analyzer] Submit input ditemukan."
                    )

                    return candidate

            except Exception:
                continue

        print(
            "[Analyzer] Submit button tidak ditemukan."
        )

        return None