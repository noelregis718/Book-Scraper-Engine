from playwright.sync_api import sync_playwright

def capture():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        query = "Wild Love Lauren Accardo"
        page.goto(f"https://www.goodreads.com/search?q={query.replace(' ', '+')}")
        page.wait_for_timeout(5000)
        page.screenshot(path='gr_search_debug.png', full_page=True)
        print("Screenshot saved to gr_search_debug.png")
        browser.close()

if __name__ == "__main__":
    capture()
