from playwright.sync_api import sync_playwright

def find_categories():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://knightagency.net/ourbooks/")
        
        # Look for category links
        categories = page.query_selector_all(".product-category a, .cat-item a")
        results = []
        for cat in categories:
            results.append({
                "name": cat.inner_text(),
                "url": cat.get_attribute("href")
            })
        
        # If no explicit categories, look at the sidebar or dropdown
        if not results:
             cats = page.query_selector_all("select.dropdown_product_cat option")
             for cat in cats:
                 results.append({
                     "name": cat.inner_text(),
                     "url": f"https://knightagency.net/ourbooks/?product_cat={cat.get_attribute('value')}"
                 })

        print(results)
        browser.close()

if __name__ == "__main__":
    find_categories()
