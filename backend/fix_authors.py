import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from apply_jra_style import apply_styling

async def fix_authors(excel_path):
    print(f"Loading: {excel_path}")
    df = pd.read_excel(excel_path)
    
    # Cast "Author Name" to object
    if "Author Name" in df.columns:
        df["Author Name"] = df["Author Name"].astype(object)
        
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        count = 0
        for index, row in df.iterrows():
            author = str(row.get("Author Name", "")).strip().lower()
            url = str(row.get("GoodReads series link", "")).strip()
            title = str(row.get("Name of Series", "")).strip()
            
            if ("unknown" in author or "unannounced" in author):
                print(f"[{index+1}] Fixing author for '{title}'...")
                
                try:
                    target_url = url
                    # If no valid URL, search for the title
                    if not target_url or target_url in ["nan", "N/A"]:
                        query = title.replace(' ', '+')
                        search_url = f"https://www.goodreads.com/search?q={query}"
                        await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
                        await asyncio.sleep(2)
                        
                        current_url = page.url
                        if "/book/show/" in current_url:
                            target_url = current_url
                        else:
                            try:
                                first_link = await page.wait_for_selector('a.bookTitle', timeout=5000)
                                target_url = await first_link.evaluate("el => el.href")
                            except: pass
                            
                    if target_url and target_url not in ["nan", "N/A"]:
                        await page.goto(target_url, wait_until="domcontentloaded", timeout=45000)
                        await asyncio.sleep(2)
                        
                        # Try book page author selector, then series page author selector
                        author_el = await page.query_selector('span[data-testid="name"], a.authorName span[itemprop="name"], div.seriesAuthor span[itemprop="name"]')
                        if author_el:
                            new_author = await author_el.inner_text()
                            new_author = new_author.strip()
                            if new_author:
                                df.at[index, "Author Name"] = new_author
                                print(f"  -> Found author: {new_author}")
                                count += 1
                                df.to_excel(excel_path, index=False)
                                continue
                                
                    print(f"  -> Could not find author.")
                        
                except Exception as e:
                    print(f"  -> Error: {e}")
                    
        await browser.close()
        
    print(f"Fixed {count} authors!")
    apply_styling(excel_path)
    print("Styling applied.")
    import subprocess
    subprocess.Popen(["start", excel_path], shell=True)

if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target = os.path.join(base, "Tobias_All_Books_FINAL.xlsx")
    asyncio.run(fix_authors(target))
