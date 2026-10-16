from detector.captcha_detector import CaptchaDetector


tests = [
    "W9H5K",
    "AB73Q",
    "21 + 42 = ?",
    "7+5",
    "10 x 8",
    "12 * 4",
    "20 / 5",
    "",
    "???"
]


for text in tests:
    captcha_type = CaptchaDetector.detect_from_text(
        text
    )

    print(
        f"{text!r:15} -> {captcha_type}"
    )