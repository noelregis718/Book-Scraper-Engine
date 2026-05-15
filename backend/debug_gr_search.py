from playwright.sync_api import sync_playwright

def test_search():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        query = "Wild Love Lauren Accardo"
        print(f"Searching for: {query}")
        page.goto(f"https://www.goodreads.com/search?q={query.replace(' ', '+')}")
        page.wait_for_timeout(3000)
        
        results = page.query_selector_all('a.bookTitle')
        print(f"Found {len(results)} results.")
        for r in results[:5]:
            print(f"  - {r.inner_text().strip()} ({r.get_attribute('href')})")
            
        browser.close()

if __name__ == "__main__":
    test_search()
