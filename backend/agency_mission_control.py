import asyncio
import os
import re
import pandas as pd
from playwright.async_api import async_playwright
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment, PatternFill
from datetime import datetime

# Import existing scrapers
try:
    from scraper import GoodreadsScraper, AuthorScraper, clean_text
except ImportError:
    def clean_text(text):
        return str(text).strip() if text else "N/A"
    class GoodreadsScraper: pass
    class AuthorScraper: pass

# --- CONFIGURATION ---
AGENCY_CRAWLS_FILE = r"E:\Internship\PocketFM\Agency Crawls.xlsx"
MAX_CONCURRENT_TABS = 10
AGENCY_NAME = "Knight Agency"

# --- ROMANTASY TAXONOMY (For Classification only, not filtering) ---
TAXONOMY = {
    "Royal courts / Political": ["royal", "court", "fae", "politics", "epic", "quest", "kingdom", "throne", "prince", "princess", "queen", "king", "empire"],
    "Gothic / Dark": ["horror", "curse", "dark magic", "atmospheric", "gothic", "haunting", "shadow", "macabre", "creepy", "blood", "morbid"],
    "Dark Academia": ["school", "university", "academy", "secret society", "rival", "library", "scholar", "student", "professor", "campus", "scholastic"],
    "Monster / Alien": ["monster", "alien", "inhuman", "non-human", "fated mates", "beast", "creature", "tentacle", "abominable"],
    "Shifters": ["shapeshifter", "wolf", "bear", "dragon", "leopard", "tiger", "pack", "alpha", "mate", "shifter", "werewolf", "lycan"],
    "Magical Games / Competitions": ["competition", "game", "tournament", "bargain", "deal", "trial", "forced proximity", "prize", "contest", "deadly game"],
    "Mythic / Gods": ["mortal", "god", "goddess", "divine", "trial", "prophecy", "pantheon", "myth", "mythology", "olympus", "deity"],
    "Battle / Beast Bonds": ["lethal training", "dragon bond", "beast bond", "rider", "training", "war", "soldier", "mercenary", "combat"],
    "Reincarnation / Regression": ["reincarnation", "transmigration", "regression", "past life", "second chance", "isekai", "rebirth", "reborn"],
    "Paranormal (Vampires/Demons)": ["vampire", "demon", "angel", "reaper", "ghost", "spirit", "undead", "succubus", "incubus", "paranormal"],
    "Cozy / Low Stakes": ["cozy", "low-stakes", "found family", "slow-burn", "magical bakery", "tea", "comfort", "wholesome"],
    "Urban Fantasy / Modern": ["modern world", "contemporary", "magic layered", "city", "hidden world", "masquerade", "urban", "street magic"]
}

def clean_name(name):
    """Removes platform fluff like (Audiobook), (paperback) from names."""
    if not name: return "N/A"
    return re.sub(r'\s*\(.*?\)', '', name).strip()

def identify_subgenre(synopsis, tags):
    """Matches synopsis and tags against the taxonomy."""
    text = f"{synopsis} {' '.join(tags)}".lower()
    for genre, keywords in TAXONOMY.items():
        if any(kw.lower() in text for kw in keywords):
            return genre
    return "N/A"

class AgencyMissionControl:
    def __init__(self, headless=True):
        self.headless = headless
        self.gr_scraper = GoodreadsScraper(headless=headless)
        self.author_scraper = AuthorScraper(headless=headless)
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_TABS)
        self.seen_books = set()
        self._load_existing_books()

    def _load_existing_books(self):
        """Loads already scraped books to prevent duplicates."""
        if os.path.exists(AGENCY_CRAWLS_FILE):
            try:
                df = pd.read_excel(AGENCY_CRAWLS_FILE, sheet_name=AGENCY_NAME)
                for _, row in df.iterrows():
                    key = f"{str(row['Name of Series']).strip()}|{str(row['Author Name']).strip()}".lower()
                    self.seen_books.add(key)
                print(f"  [System] Loaded {len(self.seen_books)} existing books from {AGENCY_NAME} sheet.")
            except Exception:
                pass

    async def run_mission(self, context, start_url):
        """Scrapes the entire catalog and enriches data."""
        print(f"\n>>> Starting MISSION: {AGENCY_NAME}")
        
        page = await context.new_page()
        leads = []
        
        try:
            current_url = start_url
            page_num = 1
            
            # --- PHASE 1: DISCOVERY (All Pages) ---
            print("  [Phase 1] Discovering all books from catalog...")
            while True:
                print(f"    Scanning Page {page_num}: {current_url}")
                await page.goto(current_url, wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(3)
                
                books_elements = await page.query_selector_all('.product')
                if not books_elements: break
                
                found_on_page = 0
                for el in books_elements:
                    text = await el.inner_text()
                    if " by " in text:
                        parts = text.split(" by ")
                        title = clean_name(parts[0])
                        author_and_price = parts[1].strip()
                        author = clean_name(re.split(r'\$', author_and_price)[0])
                        
                        lead_key = f"{title}|{author}".lower()
                        if lead_key not in self.seen_books:
                            leads.append({"Name of Series": title, "Author Name": author})
                            self.seen_books.add(lead_key)
                            found_on_page += 1
                
                print(f"    -> Found {found_on_page} new books. Total Discovery: {len(leads)}")
                
                # Pagination
                next_btn = await page.query_selector('.next.page-numbers, a.next')
                if next_btn:
                    next_url = await next_btn.evaluate("el => el.href")
                    if next_url and next_url != current_url:
                        current_url = next_url
                        page_num += 1
                        continue
                
                # Manual Fallback
                page_num += 1
                if "/page/" in current_url:
                    current_url = re.sub(r'/page/\d+/', f'/page/{page_num}/', current_url)
                else:
                    if "?" in current_url:
                        base, query = current_url.split("?", 1)
                        current_url = f"{base.rstrip('/')}/page/{page_num}/?{query}"
                    else:
                        current_url = f"{current_url.rstrip('/')}/page/{page_num}/"
                
                # Small check if page actually exists
                try:
                    response = await page.goto(current_url, wait_until="domcontentloaded", timeout=10000)
                    if response.status != 200: break
                except: break

            await page.close()
            if not leads:
                print("  [Notice] No new books found to scrape.")
                return

            # --- PHASE 2: ENRICHMENT & SAVING (Batches) ---
            print(f"\n  [Phase 2] Enriching {len(leads)} books in batches of {MAX_CONCURRENT_TABS}...")
            
            for i in range(0, len(leads), MAX_CONCURRENT_TABS):
                batch = leads[i : i + MAX_CONCURRENT_TABS]
                print(f"    Processing Batch {i//MAX_CONCURRENT_TABS + 1}...")
                
                tasks = [self.process_lead(context, lead, i + j + 1, len(leads)) for j, lead in enumerate(batch)]
                batch_results = await asyncio.gather(*tasks)
                
                valid_results = [r for r in batch_results if r]
                if valid_results:
                    self.save_to_excel(valid_results)
            
            print("\nMISSION COMPLETED SUCCESSFULLY.")

        except Exception as e:
            print(f"  [Critical] Mission failed: {e}")

    async def process_lead(self, context, lead, index, total):
        async with self.semaphore:
            try:
                print(f"      [{index}/{total}] Enriching: {lead['Name of Series']}...")
                gr_data = await self.gr_scraper.scrape_goodreads_data(
                    context, lead['Name of Series'], lead['Author Name']
                )
                
                if not gr_data: return None
                
                synopsis = gr_data.get("Description", "N/A")
                tags = [gr_data.get("Genre", ""), gr_data.get("Sub_Genre", "")]
                matched_genre = identify_subgenre(synopsis, tags)
                
                return {
                    "Name of Series": lead['Name of Series'],
                    "Author Name": lead['Author Name'],
                    "Publisher": gr_data.get("Publisher", "Various / Knight Agency"),
                    "GoodReads series link": gr_data.get("GoodReads_Series_URL", "N/A"),
                    "Number of PRIMARY books in the series": gr_data.get("Num_Primary_Books", "N/A"),
                    "Rating (out of 5) of Primary Book 1": gr_data.get("Book1_Rating", "N/A"),
                    "Ratings (#) of Primary Book 1": gr_data.get("Book1_Num_Ratings", "N/A"),
                    "Synopsis (if available)": synopsis[:1000] if synopsis != "N/A" else "N/A",
                    "Romantasy Sub-Genre of series": matched_genre,
                    "Name of agent": "Knight Agency Representative"
                }
            except Exception as e:
                print(f"      [Error] Failed to process {lead['Name of Series']}: {e}")
                return None

    def save_to_excel(self, data):
        """Incremental save to Excel."""
        if not data: return
        df_new = pd.DataFrame(data)
        
        try:
            if not os.path.exists(AGENCY_CRAWLS_FILE):
                with pd.ExcelWriter(AGENCY_CRAWLS_FILE, engine='openpyxl') as writer:
                    df_new.to_excel(writer, sheet_name=AGENCY_NAME, index=False)
            else:
                with pd.ExcelWriter(AGENCY_CRAWLS_FILE, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                    try:
                        existing_df = pd.read_excel(AGENCY_CRAWLS_FILE, sheet_name=AGENCY_NAME)
                        combined_df = pd.concat([existing_df, df_new], ignore_index=True).drop_duplicates(subset=['Name of Series', 'Author Name'], keep='last')
                        combined_df.to_excel(writer, sheet_name=AGENCY_NAME, index=False)
                    except:
                        df_new.to_excel(writer, sheet_name=AGENCY_NAME, index=False)
            
            self.style_excel()
        except Exception as e:
            print(f"    [Warning] Save failed: {e}")

    def style_excel(self):
        try:
            wb = load_workbook(AGENCY_CRAWLS_FILE)
            ws = wb[AGENCY_NAME]
            header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
            header_font = Font(color="FFFFFF", bold=True)
            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center")
            for col in ws.columns:
                ws.column_dimensions[col[0].column_letter].width = 40
            wb.save(AGENCY_CRAWLS_FILE)
        except: pass

async def main():
    control = AgencyMissionControl(headless=False)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0")
        
        # TARGET CATEGORY
        url = "https://knightagency.net/ourbooks/?product_cat=romantic-suspense"
        await control.run_mission(context, url)
        
        await browser.close()
        if os.name == 'nt': os.startfile(AGENCY_CRAWLS_FILE)

if __name__ == "__main__":
    asyncio.run(main())
