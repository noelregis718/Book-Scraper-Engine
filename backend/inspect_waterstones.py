import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re

async def inspect():
    url = "https://www.waterstones.com/category/romantic-fiction/fantasy-romance/sortmode/bestselling/page/1"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print(f"Navigating to {url}")
        await page.goto(url, timeout=60000)
        
        # Give it time to bypass captcha if needed
        await page.wait_for_timeout(5000)
        
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        with open('waterstones_dump.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
            
        print("Finding book items...")
        # Common classes for books might be book-thumb, product-list, etc.
        books = soup.find_all('div', class_=re.compile(r'book|product|item', re.I))
        print(f"Found {len(books)} potential containers.")
        
        # Let's check some specific classes if possible
        for i, book in enumerate(books[:5]):
            title_el = book.find(['a', 'h2', 'h3'], class_=re.compile(r'title|name', re.I))
            author_el = book.find(['a', 'span', 'p'], class_=re.compile(r'author', re.I))
            
            t = title_el.text.strip() if title_el else 'None'
            a = author_el.text.strip() if author_el else 'None'
            print(f"[{i}] Title: {t} | Author: {a}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect())
