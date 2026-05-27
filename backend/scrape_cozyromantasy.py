import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

OUTPUT_FILE = r"E:\Internship\PocketFM\CozyRomantasy_Merged.xlsx"

ELEVEN_COLUMN_HEADERS = [
    "Name of Series",
    "Author Name",
    "Publisher",
    "GoodReads series link",
    "Number of PRIMARY books in the series",
    "Rating (out of 5) of Primary Book 1",
    "Ratings (#) of Primary Book 1",
    "Synopsis (if available)",
    "Romantasy = Yes or No?",
    "Romantasy Sub-Genre of series",
    "Name of agent"
]

async def main():
    print("Launching headed browser to bypass bot protection...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        print("Navigating to cozyromantasy.com...")
        await page.goto("https://www.cozyromantasy.com/")
        print("Waiting for dynamic content to render...")
        await page.wait_for_timeout(5000)
        
        texts = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('h1, h2, h3, h4, p, span'))
                 .map(el => el.innerText.trim())
                 .filter(t => t.length > 0);
        }''')
        
        await browser.close()
        
    print(f"Extracted {len(texts)} text elements. Parsing books...")
    
    books = []
    
    # We look for "Read More" as a delimiter. 
    # The title is usually a few lines before it.
    
    # Let's clean the texts by splitting by newlines and flattening, because sometimes 
    # innerText grabs a whole block with newlines.
    flat_texts = []
    for t in texts:
        for line in t.split('\n'):
            line = line.strip()
            if line:
                flat_texts.append(line)
                
    # From the earlier dump, we saw the pattern:
    # Potions & Prejudice
    # Tee Harlowe
    # Witch hates warlock. ...
    # Read More
    
    current_book_lines = []
    
    for line in flat_texts:
        if line == "Read More":
            if len(current_book_lines) >= 3:
                title = current_book_lines[0]
                author = current_book_lines[1]
                synopsis = " ".join(current_book_lines[2:])
                
                books.append({
                    "Name of Series": title,
                    "Author Name": author,
                    "Publisher": "Cozy Coven",  # Defaulting as collective name
                    "GoodReads series link": "",
                    "Number of PRIMARY books in the series": 1,
                    "Rating (out of 5) of Primary Book 1": "N/A",
                    "Ratings (#) of Primary Book 1": "N/A",
                    "Synopsis (if available)": synopsis,
                    "Romantasy = Yes or No?": "",
                    "Romantasy Sub-Genre of series": "",
                    "Name of agent": ""
                })
            current_book_lines = []
        else:
            # Skip some known menu/header fluff
            if line in ["Menu", "Home", "Free Books & Newsletters", "What's Next", "The Cozy Coven", "A Cozy Romantasy Collective", "Comfort for your soul, heat for your heart", "Notify Me"]:
                continue
            current_book_lines.append(line)

    # For the last book which might not have "Read More" after it
    if len(current_book_lines) >= 3:
        # Check if the last book looks valid
        title = current_book_lines[0]
        author = current_book_lines[1]
        synopsis = " ".join(current_book_lines[2:])
        books.append({
            "Name of Series": title,
            "Author Name": author,
            "Publisher": "Cozy Coven",
            "GoodReads series link": "",
            "Number of PRIMARY books in the series": 1,
            "Rating (out of 5) of Primary Book 1": "N/A",
            "Ratings (#) of Primary Book 1": "N/A",
            "Synopsis (if available)": synopsis,
            "Romantasy = Yes or No?": "",
            "Romantasy Sub-Genre of series": "",
            "Name of agent": ""
        })

    print(f"Parsed {len(books)} books successfully.")
    
    df = pd.DataFrame(books)
    df = df.reindex(columns=ELEVEN_COLUMN_HEADERS)
    
    print(f"Saving to {OUTPUT_FILE}...")
    df.to_excel(OUTPUT_FILE, index=False)
    
    try:
        from apply_jra_style import apply_styling
        apply_styling(OUTPUT_FILE)
        print("--- Applied styling ---")
    except Exception as e:
        print(f"Could not apply styling: {e}")
        
    print("Opening Excel file...")
    import subprocess
    subprocess.Popen(["start", OUTPUT_FILE], shell=True)
    
    # Run the classification automatically
    print("Running Romantasy sub-genre classification...")
    try:
        import classify_cozy_final
        classify_cozy_final.main()
    except Exception as e:
        print(f"Could not run classification: {e}")

if __name__ == '__main__':
    asyncio.run(main())
