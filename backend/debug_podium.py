from playwright.sync_api import sync_playwright
import time

def debug_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://podiumentertainment.com/genre/horror/13", wait_until="domcontentloaded")
        
        # wait a bit for hydration
        time.sleep(5)
        
        # Click Apply if it exists
        try:
            apply_btn = page.query_selector("button:has-text('Apply')")
            if apply_btn and apply_btn.is_visible():
                apply_btn.click()
                time.sleep(3)
        except:
            pass
            
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(5)
        
        # Get all links
        links = page.query_selector_all("a")
        found = set()
        for l in links:
            href = l.get_attribute("href")
            if href:
                found.add(href)
                
        with open("debug_links.txt", "w") as f:
            for l in sorted(list(found)):
                f.write(l + "\n")
                
        browser.close()

if __name__ == "__main__":
    debug_page()
