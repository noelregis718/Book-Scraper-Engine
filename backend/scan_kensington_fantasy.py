import asyncio
import os
from playwright.async_api import async_playwright

async def scan():
    url = "https://www.kensingtonbooks.com/shop/product-category/fiction/fantasy-fiction/"
    print("=" * 60)
    print("  KENSINGTON BOOKS: FANTASY FICTION SCANNER")
    print("=" * 60)
    print(f"Target URL: {url}\n")
    
    async with async_playwright() as p:
        try:
            print("[1] Launching Chrome in headed mode...")
            browser = await p.chromium.launch(
                headless=False,
                channel="chrome",
                args=["--disable-blink-features=AutomationControlled"]
            )
        except Exception as e:
            print(f"[1] Chrome channel failed ({e}), trying standard chromium...")
            browser = await p.chromium.launch(
                headless=False,
                args=["--disable-blink-features=AutomationControlled"]
            )
            
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()
        await page.add_init_script("delete navigator.__proto__.webdriver;")
        
        print("[2] Navigating to category page...")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        print("[3] Checking for Cloudflare challenge...")
        for i in range(15):
            title = await page.title()
            print(f"    - Attempt {i+1}: Title = '{title}'")
            if "just a moment" not in title.lower() and "attention required" not in title.lower():
                print("    >>> Security bypassed successfully!")
                break
            await asyncio.sleep(2)
            
        # Give extra time for JS hydration
        await asyncio.sleep(3)
        
        # Analyze products
        title = await page.title()
        print(f"\nFinal Page Title: {title}")
        
        # Inspect selectors
        info = await page.evaluate("""() => {
            const results = {};
            
            // Check common product selectors
            results.products_li = document.querySelectorAll('li.product').length;
            results.products_class = document.querySelectorAll('.product').length;
            results.products_article = document.querySelectorAll('article').length;
            
            // Sample products
            const samples = [];
            const cards = document.querySelectorAll('li.product, .product, article.product');
            cards.forEach((card, idx) => {
                if (idx < 5) {
                    const titleEl = card.querySelector('.woocommerce-loop-product__title, .product-title, h2, h3, a.title');
                    const authorEl = card.querySelector('.author, .book-author, .byline, p.author');
                    const linkEl = card.querySelector('a');
                    samples.push({
                        title: titleEl ? titleEl.innerText.trim() : 'N/A',
                        author: authorEl ? authorEl.innerText.trim() : 'N/A',
                        link: linkEl ? linkEl.href : 'N/A',
                        html_preview: card.outerHTML.substring(0, 300)
                    });
                }
            });
            results.samples = samples;
            
            // Check pagination
            const paginationEl = document.querySelector('.woocommerce-pagination, .pagination, nav.navigation');
            results.pagination_html = paginationEl ? paginationEl.outerHTML : 'None';
            
            // Count total page numbers if available
            const pageLinks = document.querySelectorAll('.page-numbers a, a.page-number, .woocommerce-pagination a');
            results.page_links = Array.from(pageLinks).map(a => ({ text: a.innerText.trim(), href: a.href }));
            
            return results;
        }""")
        
        print(f"\n--- Product Detection ---")
        print(f"li.product count: {info.get('products_li')}")
        print(f".product count:    {info.get('products_class')}")
        print(f"article count:     {info.get('products_article')}")
        
        print(f"\n--- Samples (First 5) ---")
        for s in info.get("samples", []):
            print(f"Title:  {s['title']}")
            print(f"Author: {s['author']}")
            print(f"Link:   {s['link']}")
            print(f"HTML:   {s['html_preview'][:150]}...")
            print("-" * 40)
            
        print(f"\n--- Pagination Links ---")
        for pl in info.get("page_links", []):
            print(f"Page text: {pl['text']} -> {pl['href']}")
            
        # Save complete page content
        content = await page.content()
        with open("backend/kensington_fantasy_scanned.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("\nSaved full page HTML to backend/kensington_fantasy_scanned.html")
        
        await browser.close()
        print("\n[Done] Browser closed.")

if __name__ == "__main__":
    asyncio.run(scan())

