import pandas as pd
import asyncio
from playwright.async_api import async_playwright
import urllib.parse
import re
import sys

# Ensure stdout is flushed constantly for tracking
def print_flush(text):
    print(text, flush=True)

async def clean_text(text):
    if not text: return ""
    return re.sub(r'\s+', ' ', text).strip()

async def annihilate_popups(page):
    try:
        # Aggressively remove known goodreads popups via JS
        js = """
        document.querySelectorAll('.modal, .Modal, [data-react-class="ReactComponents.LoginInterstitial"], .Overlay').forEach(el => el.remove());
        document.body.style.overflow = 'auto';
        """
        await page.evaluate(js)
    except:
        pass

async def navigate_and_click(page, query):
    url = f"https://www.goodreads.com/search?q={urllib.parse.quote(query)}"
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
    except Exception as e:
        print_flush(f"      [Nav Error] {e}")
        return False
        
    await annihilate_popups(page)
    
    if "search?q=" in page.url:
        try:
            # Wait for search results
            await page.wait_for_selector('table.tableList tr a.bookTitle', timeout=5000)
            await annihilate_popups(page)
            # Force click to bypass any transparent overlays
            await page.click('table.tableList tr a.bookTitle', force=True, timeout=5000)
            await page.wait_for_load_state("domcontentloaded", timeout=15000)
            return True
        except Exception as e:
            print_flush(f"      [Click Failed] {e}")
            return False
    return True # We were redirected to the book page directly

async def scrape_book(context, title, author):
    page = await context.new_page()
    clean_author = str(author).replace(", Authors", "").replace(" Author", "").strip()
    primary_query = f"{title} {clean_author}"
    fallback_query = title
    
    print_flush(f"  [Search] {primary_query}")
    success = await navigate_and_click(page, primary_query)
    
    if not success:
        print_flush(f"  [Fallback Search] {fallback_query}")
        success = await navigate_and_click(page, fallback_query)
        
    if not success:
        print_flush(f"  [Failed] Could not reach book page for: {title}")
        await page.close()
        return None
        
    print_flush(f"  [On Book Page] {page.url}")
    await annihilate_popups(page)
    
    # Extract data
    subgenre = ""
    genres = []
    try:
        genre_els = await page.query_selector_all('[data-testid="genresList"] .Button__labelItem, .BookPageMetadataSection__genre a')
        for gel in genre_els[:3]:
            genres.append(await clean_text(await gel.inner_text()))
        subgenre = ", ".join(genres)
    except: pass
    
    rating = ""
    rating_count = ""
    try:
        rating_el = await page.query_selector('div.RatingStatistics__rating')
        if rating_el:
            rating = await clean_text(await rating_el.inner_text())
        count_el = await page.query_selector('[data-testid="ratingsCount"]')
        if count_el:
            c_text = await clean_text(await count_el.inner_text())
            rating_count = c_text.split()[0].replace(",", "")
    except: pass
    
    pages = ""
    try:
        pages_el = await page.query_selector('[data-testid="pagesFormat"]')
        if pages_el:
            p_text = await clean_text(await pages_el.inner_text())
            pages = p_text.split()[0]
    except: pass
    
    series_url = ""
    try:
        s_el = await page.query_selector('h3.Text__title3 a[href*="/series/"], [data-testid="series"] a')
        if s_el:
            series_url = await s_el.evaluate("el => el.href")
        else:
            series_url = page.url # Fallback to book URL if no series exists
    except: 
        series_url = page.url
    
    primary_books = "1"
    if series_url and "/series/" in series_url:
        print_flush(f"  [Visiting Series Page] {series_url}")
        try:
            await page.goto(series_url, wait_until="domcontentloaded", timeout=15000)
            await annihilate_popups(page)
            content = await page.content()
            match = re.search(r'(\d+)\s+primary\s+works', content, re.IGNORECASE)
            if match:
                primary_books = match.group(1)
        except Exception as e:
            print_flush(f"      [Series Page Error] {e}")
            
    await page.close()
    
    return {
        "Subgenre": subgenre,
        "Goodreads Series URL": series_url,
        "Book 1 Rating": rating,
        "Number of Book 1 Ratings": rating_count,
        "Number of Primary Books": primary_books,
        "Number of Pages in Book 1": pages
    }

async def process_row(i, row, context, semaphore, excel_lock, df, file_path):
    async with semaphore:
        title = row["Book Title"]
        author = row["Author"]
        
        print_flush(f"\n[Task {i}] Started missing book search: {title}")
        data = await scrape_book(context, title, author)
        
        if data:
            print_flush(f"  [Task {i} Result] {data}")
            async with excel_lock:
                for key, val in data.items():
                    df.at[i, key] = val
                # Safe save
                df.to_excel(file_path, index=False, engine="openpyxl")
                print_flush(f"  [Task {i}] Missing data saved safely.")

async def main():
    file_path = "e:/Internship/PocketFM/podium_data.xlsx"
    print_flush(f"Loading Excel {file_path}...")
    df = pd.read_excel(file_path, engine="openpyxl")
    
    # Cast target columns to object to avoid dtype warnings
    target_cols = ["Subgenre", "Goodreads Series URL", "Book 1 Rating", "Number of Book 1 Ratings", "Number of Primary Books", "Number of Pages in Book 1"]
    for col in target_cols:
        if col in df.columns:
            df[col] = df[col].astype('object')
            
    semaphore = asyncio.Semaphore(8)
    excel_lock = asyncio.Lock()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )
        
        tasks = []
        start_idx = 3500
        end_idx = 4500
        
        for i in range(start_idx, min(end_idx, len(df))):
            row = df.iloc[i]
            
            # Check if Goodreads data is missing
            is_missing = pd.isna(row.get("Book 1 Rating")) or pd.isna(row.get("Goodreads Series URL")) or str(row.get("Goodreads Series URL")).strip() == ""
            
            if is_missing:
                task = asyncio.create_task(process_row(i, row, context, semaphore, excel_lock, df, file_path))
                tasks.append(task)
                
        print_flush(f"\nScanning rows {start_idx + 1} to {end_idx}...")
        print_flush(f"Found {len(tasks)} books missing Goodreads data. Booting up aggressive scraper...\n")
        
        if tasks:
            await asyncio.gather(*tasks)
            
        await browser.close()
        
    print_flush("\n[Success] Missing books gap-filled successfully!")

if __name__ == "__main__":
    asyncio.run(main())
