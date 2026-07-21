import pandas as pd
import asyncio
from playwright.async_api import async_playwright
import urllib.parse
import re
import bs4

def print_flush(text):
    print(text, flush=True)

async def clean_text(text):
    if not text: return ""
    return re.sub(r'\s+', ' ', text).strip()

async def annihilate_popups(page):
    try:
        js = """
        document.querySelectorAll('.modal, .Modal, [data-react-class="ReactComponents.LoginInterstitial"], .Overlay').forEach(el => el.remove());
        document.body.style.overflow = 'auto';
        """
        await page.evaluate(js)
    except:
        pass

async def login_to_goodreads(page):
    print_flush("[Login] Navigating to Goodreads Sign-In...")
    await page.goto("https://www.goodreads.com/user/sign_in", wait_until="domcontentloaded")
    
    try:
        # Click "Sign in with email"
        email_btn = page.locator('a:has-text("Sign in with email")')
        if await email_btn.is_visible():
            await email_btn.click()
            await page.wait_for_load_state("domcontentloaded")
            
        if await page.locator("#ap_email").is_visible():
            print_flush("[Login] Entering credentials...")
            await page.fill("#ap_email", "noel.regis04@gmail.com")
            await page.fill("#ap_password", "Noel@1024")
            await page.click("#signInSubmit")
            print_flush("[Login] Clicked Submit. Waiting 15 seconds in case of CAPTCHA...")
            await asyncio.sleep(15) # Wait for user to solve CAPTCHA if needed
    except Exception as e:
        print_flush(f"[Login Error] {e}")

async def scrape_via_search(context, book_name, author):
    page = await context.new_page()
    
    query = f"{book_name} {author}".strip()
    search_url = f"https://www.goodreads.com/search?q={urllib.parse.quote(query)}"
    
    print_flush(f"      [Search] {search_url}")
    try:
        await page.goto(search_url, wait_until="domcontentloaded", timeout=25000)
        await annihilate_popups(page)
    except Exception as e:
        print_flush(f"      [Nav Error] Search Page: {e}")
        await page.close()
        return None, None, None
        
    try:
        await page.wait_for_selector('table.tableList tr a.bookTitle', timeout=5000)
        await annihilate_popups(page)
        await page.click('table.tableList tr a.bookTitle', force=True, timeout=5000)
        await page.wait_for_load_state("domcontentloaded", timeout=15000)
        await annihilate_popups(page)
    except Exception as e:
        pass
        
    pages = None
    try:
        pages_el = await page.query_selector('[data-testid="pagesFormat"]')
        if pages_el:
            p_text = await clean_text(await pages_el.inner_text())
            pages = p_text.split()[0]
    except:
        pass
        
    series_url = None
    series_name_text = None
    try:
        s_el = await page.query_selector('h3.Text__title3 a[href*="/series/"], [data-testid="series"] a, a[href*="/series/"]')
        if s_el:
            series_url = await s_el.evaluate("el => el.href")
            series_name_text = await clean_text(await s_el.inner_text())
            if series_name_text:
                series_name_text = series_name_text.split(', #')[0].split(' #')[0].strip()
    except:
        pass
        
    if not series_url:
        print_flush("      [Failed] Could not find Series Link on the book page.")
        await page.close()
        return None, pages, series_name_text
        
    print_flush(f"      [Found Series URL] {series_url} (Name: {series_name_text})")
    primary_books = None
    try:
        await page.goto(series_url, wait_until="domcontentloaded", timeout=25000)
        await annihilate_popups(page)
        
        content = await page.content()
        match = re.search(r'(\d+)\s+primary\s+works', content, re.IGNORECASE)
        primary_books = match.group(1) if match else None
        
    except Exception as e:
        print_flush(f"      [Nav Error] Series Page: {e}")
        
    await page.close()
    return primary_books, pages, series_name_text

async def process_row(i, row, context, semaphore, excel_lock, df, file_path):
    async with semaphore:
        book_name = row.get("Name of books")
        author = row.get("Author Name")
        
        if pd.isna(book_name) or str(book_name).strip() == "":
            return
            
        print_flush(f"\n[Task {i}] Searching Goodreads for: {book_name} by {author}")
        primary_books, pages, series_name = await scrape_via_search(context, book_name, author)
        
        if primary_books or pages or series_name:
            print_flush(f"  [Task {i} Result] Series: {series_name} | Books: {primary_books} | Pages: {pages}")
            async with excel_lock:
                if primary_books:
                    df.at[i, "Number of PRIMARY books in the series"] = primary_books
                if pages:
                    df.at[i, "No. of pages in Book 1 count"] = pages
                if series_name:
                    df.at[i, "Series"] = series_name
                    
                df.to_excel(file_path, index=False, engine="openpyxl")
                print_flush(f"  [Task {i}] Safely saved to Excel.")
        else:
            print_flush(f"  [Task {i}] Failed to extract data.")

async def main():
    file_path = "e:/Internship/PocketFM/1852 Media.xlsx"
    print_flush(f"Loading {file_path}...")
    df = pd.read_excel(file_path, engine="openpyxl")
    
    if "Series" not in df.columns:
        df["Series"] = None
        
    df["No. of pages in Book 1 count"] = df["No. of pages in Book 1 count"].astype('object')
    df["Number of PRIMARY books in the series"] = df["Number of PRIMARY books in the series"].astype('object')
    df["Series"] = df["Series"].astype('object')
    
    semaphore = asyncio.Semaphore(5)
    excel_lock = asyncio.Lock()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )
        
        # Login Phase
        login_page = await context.new_page()
        await login_to_goodreads(login_page)
        await login_page.close()
        
        tasks = []
        for i in range(len(df)):
            row = df.iloc[i]
            
            # Check if it failed in the last run
            is_missing_pages = pd.isna(row.get("No. of pages in Book 1 count"))
            is_bad_books = str(row.get("Number of PRIMARY books in the series")) == "1" or pd.isna(row.get("Number of PRIMARY books in the series"))
            
            if is_missing_pages or is_bad_books:
                task = asyncio.create_task(process_row(i, row, context, semaphore, excel_lock, df, file_path))
                tasks.append(task)
                
        print_flush(f"Found {len(tasks)} failed items needing data. Booting up logged-in scraper...\n")
        
        if tasks:
            await asyncio.gather(*tasks)
            
        await browser.close()
        
    print_flush("\n[Success] Logged-in scraping operation completed!")

if __name__ == "__main__":
    asyncio.run(main())
