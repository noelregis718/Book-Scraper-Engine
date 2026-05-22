import asyncio
from playwright.async_api import async_playwright
from scraper import AmazonScraper

async def test_amazon_author():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        scraper = AmazonScraper()
        
        # Test with a known book
        url = "https://www.amazon.com/A-Court-of-Thorns-and-Roses/dp/1619634449"
        print(f"Testing Amazon for URL: {url}")
        details = await scraper.scrape_product_details_tab(context, url)
        print(f"Author found: {details.get('Author Name')}")
        print(f"Full details: {details}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_amazon_author())
