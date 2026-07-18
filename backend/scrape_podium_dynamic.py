from playwright.sync_api import sync_playwright
import time
import json

import sys

def get_links(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        
        time.sleep(5)
        
        links = set()
        
        last_height = page.evaluate("document.body.scrollHeight")
        attempts = 0
        while attempts < 100:
            try:
                load_more = page.query_selector("button:has-text('Load More Titles')")
                if load_more and load_more.is_visible():
                    load_more.click()
                    time.sleep(3)
            except:
                pass
                
            elements = page.query_selector_all("a[href^='/titles/']")
            for el in elements:
                href = el.get_attribute("href")
                if href and href.startswith('/titles/'):
                    links.add("https://podiumentertainment.com" + href)
                    
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(3)
            
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                time.sleep(3)
                new_height = page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    break
            last_height = new_height
            attempts += 1
            
        browser.close()
        return list(links)

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://podiumentertainment.com/genre/horror"
    print(f"Fetching links from {url} ...")
    links = get_links(url)
    with open("podium_dynamic_links.json", "w") as f:
        json.dump(links, f)
    print(f"Found {len(links)} links")
