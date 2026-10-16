from playwright.sync_api import sync_playwright

from browser.page_analyzer import PageAnalyzer


def test_page(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False
        )

        page = browser.new_page()

        page.goto(
            url,
            wait_until="domcontentloaded"
        )

        print("\n================================")
        print("URL:", url)
        print("================================")

        analyzer = PageAnalyzer(page)

        captcha_image = analyzer.find_captcha_image()
        captcha_input = analyzer.find_captcha_input()
        submit_button = analyzer.find_submit_button()

        print("\n=== RESULT ===")

        print(
            "Captcha image:",
            "FOUND" if captcha_image else "NOT FOUND"
        )

        print(
            "Captcha input:",
            "FOUND" if captcha_input else "NOT FOUND"
        )

        print(
            "Submit button:",
            "FOUND" if submit_button else "NOT FOUND"
        )

        print("================")

        input(
            "\nTekan Enter untuk menutup browser..."
        )

        browser.close()


if __name__ == "__main__":
    url = input(
        "Masukkan URL halaman test: "
    )

    test_page(url)