import asyncio
import re
import json
import unicodedata

def clean_text(text):
    if not text:
        return ""
    text = unicodedata.normalize('NFKD', text)
    text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_series_from_title(title):
    """Matches patterns like (Series Name #1) or (Series Name, Book 1) or [Series Name]."""
    if not title: return None
    # Look for patterns inside parentheses or brackets
    patterns = [
        r'\((.*?)(?:[\s,]+#?\d+|[\s,]+Book\s+\d+)?\)',
        r'\[(.*?)(?:[\s,]+#?\d+|[\s,]+Book\s+\d+)?\]'
    ]
    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            # Clean trailing fluff
            name = re.sub(r'[\s#,\d]+$', '', name)
            if len(name) > 2: return name
    return None

def normalize_title_for_search(title):
    if not title: return ""
    t = str(title).lower()
    
    # Remove obvious platform fluff
    t = re.sub(r'\(.*?\)', '', t) # Remove everything in parens
    t = re.sub(r'\[.*?\]', '', t) # Remove everything in brackets
    
    remove_patterns = [
        r':\s+a\s+novel.*', r':\s+a\s+read\s+with\s+jenna\s+pick.*',
        r':\s+a\s+memoir.*', r'\(deluxe\s+edition\).*',
        r'\(special\s+edition\).*', r'\'s\s+broken\s+mate',
        r'book\s+\d+.*', r'vol(ume)?\s+\d+.*',
    ]
    for pattern in remove_patterns:
        t = re.sub(pattern, '', t, flags=re.IGNORECASE)
        
    t = re.split(r'[:\-—]', t)[0] # Split at colon, dash, em-dash
    t = re.sub(r'[^\w\s]', '', t) # Remove punctuation
    return t.strip()

class GoodreadsScraper:
    def __init__(self, headless=False):
        self.headless = headless

    async def login_to_goodreads(self, page):
        """Logs into Goodreads using stored credentials."""
        print("[Goodreads] Attempting login...")
        try:
            creds_path = os.path.join(os.path.dirname(__file__), "gr_creds.json")
            if not os.path.exists(creds_path):
                print("  [Goodreads] Error: gr_creds.json not found.")
                return False
                
            with open(creds_path, 'r') as f:
                creds = json.load(f)
                
            await page.goto("https://www.goodreads.com/user/sign_in", wait_until="domcontentloaded", timeout=60000)
            
            # Check if already logged in
            if await page.query_selector('a.headerPersonalNav__link[href*="/user/show"]'):
                print("  [Goodreads] Already logged in.")
                return True

            # Login fields
            email_field = await page.query_selector('input[type="email"], input[name="user[email]"]')
            pass_field = await page.query_selector('input[type="password"], input[name="user[password]"]')
            
            if email_field and pass_field:
                await email_field.fill(creds['email'])
                await pass_field.fill(creds['password'])
                
                # Check for CAPTCHA
                if await page.query_selector('#captcha-image, .captcha'):
                    print("  [Action Required] CAPTCHA detected! Please solve it in the browser window...")
                    # Wait for the user to solve it and for the login to finish
                    await page.wait_for_selector('a.headerPersonalNav__link[href*="/user/show"]', timeout=300000)
                else:
                    await page.click('input[type="submit"], #signInSubmit')
                    # Wait to confirm login
                    try:
                        await page.wait_for_selector('a.headerPersonalNav__link[href*="/user/show"]', timeout=30000)
                    except:
                        print("  [Goodreads] Login took too long or manual intervention needed.")
            
            return True
        except Exception as e:
            print(f"  [Goodreads] Login error: {e}")
            return False

    async def search_author_books(self, context, author_name, max_books=5):
        """Searches for an author and returns titles of their first few books."""
        page = await context.new_page()
        try:
            print(f"    [Goodreads] Searching for author: {author_name}...", flush=True)
            # Use general search instead of 'people' search
            search_url = f"https://www.goodreads.com/search?q={author_name.replace(' ', '+')}"
            await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(3) # Wait for results
            
            # Look for author links in the results
            author_link = await page.query_selector('a[href*="/author/show/"]')
            if not author_link:
                 # Check for "people" results specifically if general failed
                 author_link = await page.query_selector('.authorName, .authorName__container a')

            if not author_link:
                print(f"    [Goodreads] Could not find author profile for: {author_name}", flush=True)
                return []
                
            author_url = await author_link.evaluate("el => el.href")
            print(f"    [Goodreads] Found author URL: {author_url}", flush=True)
            await page.goto(author_url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(3)
            
            # Scrape top book titles
            book_els = await page.query_selector_all('a.bookTitle, [data-testid="bookTitle"] a')
            titles = []
            for el in book_els:
                title = (await el.inner_text()).strip()
                if title and title not in titles:
                    titles.append(title)
                if len(titles) >= max_books:
                    break
            
            print(f"    [Goodreads] Found {len(titles)} books for {author_name}.", flush=True)
            return titles
        except Exception as e:
            print(f"    [Goodreads] Author search error for {author_name}: {e}", flush=True)
            return []
        finally:
            await page.close()

    async def scrape_goodreads_data(self, context, title, author, isbn10="N/A", isbn13="N/A", asin="N/A", existing_url="N/A"):
        if not title or title == "N/A":
            return {}

        page = await context.new_page()
        try:
            book_url = None
            extracted_series = extract_series_from_title(title)
            
            # --- TIER 0: Existing URL ---
            if existing_url and str(existing_url).startswith("http") and "goodreads.com" in str(existing_url):
                book_url = existing_url
            
            # --- TIER 0.5: Extracted Series ---
            if not book_url and extracted_series:
                try:
                    search_query = f"{extracted_series} {author} series goodreads"
                    search_url = f"https://www.goodreads.com/search?q={search_query.replace(' ', '+')}"
                    await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
                    series_link = await page.query_selector('a[href*="/series/"]')
                    if series_link:
                        book_url = await series_link.evaluate("el => el.href")
                except: pass
            
            # --- TIER 1: Direct ID ---
            if not book_url:
                potential_ids = [isbn13, isbn10, asin]
                for pid in potential_ids:
                    if pid and pid != "N/A":
                        try:
                            direct_url = f"https://www.goodreads.com/book/isbn/{pid}"
                            await page.goto(direct_url, wait_until="domcontentloaded", timeout=45000)
                            if "goodreads.com/book/show/" in page.url or "goodreads.com/work/" in page.url:
                                book_url = page.url
                                break
                        except: continue

            # --- TIER 2: Internal Search (Aggressive Banner & Link Capture) ---
            if not book_url:
                # Use a "Clean" title + Author for search query
                clean_query_title = normalize_title_for_search(title)
                query = f"{clean_query_title} {author}"
                try:
                    print(f"    [Goodreads] Searching for first available result: {query}...")
                    search_url = f"https://www.goodreads.com/search?q={query.replace(' ', '+')}"
                    await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
                    
                    # Wait for results to actually populate
                    await asyncio.sleep(2.5)
                    
                    # Broad Selection: Grab the first valid book link from any results container
                    first_link = await page.query_selector('a.bookTitle, [data-testid="bookTitle"] a, .bookTitle, [data-testid="bookSearchResult"] a, h3 a[href*="/book/show/"]')
                    
                    if not first_link:
                        # Check for CAPTCHA
                        if await page.query_selector('#captcha-image, .captcha, iframe[src*="captcha"]'):
                            print(f"\n    [!!! ACTION REQUIRED !!!] CAPTCHA detected for '{title}'!")
                            await page.wait_for_selector('a.bookTitle, [data-testid="bookTitle"] a, .bookTitle', timeout=1200000)
                            first_link = await page.query_selector('a.bookTitle, [data-testid="bookTitle"] a, .bookTitle, [data-testid="bookSearchResult"] a')
                        
                    if first_link:
                        book_url = await first_link.evaluate("el => el.href")
                        print(f"    [Goodreads] Success! Captured first result: {book_url}")
                except Exception as e:
                    print(f"    [Goodreads] Search error: {e}")
            
            # --- TIER 3: Brave Fallback (More Aggressive) ---
            if not book_url:
                search_queries = [
                    f'"{title}" {author} goodreads',
                    f'"{normalize_title_for_search(title)}" {author} site:goodreads.com/book',
                    f'"{title}" goodreads'
                ]
                for query in search_queries:
                    brave_url = f"https://search.brave.com/search?q={query.replace(' ', '+')}"
                    try:
                        print(f"    [Goodreads] Trying external search: {query}...")
                        await page.goto(brave_url, wait_until="domcontentloaded", timeout=30000)
                        links = await page.query_selector_all('a[href*="goodreads.com/book/show/"]')
                        if links: 
                            book_url = await links[0].evaluate("el => el.href")
                            break
                    except: continue

            if not book_url: return {}
            
            # Step 2: Book Page Extraction
            if page.url != book_url or "/series/" in page.url:
                if "/series/" in book_url or "/series/" in page.url:
                    await page.goto(book_url, wait_until="domcontentloaded", timeout=45000)
                    first_book = await page.query_selector('a.bookTitle, [data-testid="bookTitle"] a, a[href*="/book/show/"]')
                    if first_book: book_url = await first_book.evaluate("el => el.href")
                await page.goto(book_url, wait_until="domcontentloaded", timeout=60000)
            
            await asyncio.sleep(4)
            genres = []
            genre_els = await page.query_selector_all('[data-testid="genresList"] .Button__labelItem, .BookPageMetadataSection__genre a')
            for gel in genre_els:
                txt = clean_text(await gel.inner_text())
                if txt and txt not in genres: genres.append(txt)
            
            is_romantasy = "Yes" if any("romantasy" in g.lower() for g in genres) else "No"
            genre_main = genres[0] if genres else "N/A"
            genre_sub = genres[1] if len(genres) > 1 else "N/A"

            avg_rating = "N/A"
            rating_count = "N/A"
            try:
                ld_el = await page.query_selector('script[type="application/ld+json"]')
                if ld_el:
                    ld_data = json.loads(await ld_el.inner_text())
                    if isinstance(ld_data, list): ld_data = ld_data[0]
                    avg_rating = str(ld_data.get('aggregateRating', {}).get('ratingValue', 'N/A'))
                    rating_count = str(ld_data.get('aggregateRating', {}).get('ratingCount', 'N/A'))
            except: pass

            description = "N/A"
            desc_el = await page.query_selector('[data-testid="description"] .Formatted, .readable')
            if desc_el: description = clean_text(await desc_el.inner_text())

            # Series Logic
            series_url = "N/A"
            series_link = await page.query_selector('h3.Text__title3 a[href*="/series/"], [data-testid="series"] a')
            if series_link: series_url = await series_link.evaluate("el => el.href")
            
            series_data = {"Num_Primary_Books": "1", "Book1_Rating": avg_rating, "Book1_Num_Ratings": rating_count}
            if series_url != "N/A":
                try:
                    await page.goto(series_url, wait_until="domcontentloaded", timeout=60000)
                    content = await page.content()
                    m = re.search(r'(\d+)\s+primary\s+works', content, re.IGNORECASE)
                    if m: series_data["Num_Primary_Books"] = m.group(1)
                    
                    row1 = await page.query_selector('.listWithDividers__item, .seriesWork')
                    if row1:
                        rtxt = (await row1.inner_text()).lower()
                        r_match = re.search(r'([\d.]+)\s+avg\s+rating\s+[—\-]\s+([\d,]+)\s+ratings', rtxt)
                        if r_match:
                            series_data["Book1_Rating"] = r_match.group(1)
                            series_data["Book1_Num_Ratings"] = r_match.group(2).replace(',', '')
                except: pass

            author_found = "Unknown"
            author_el = await page.query_selector('[data-testid="authorName"], .authorName__container [itemprop="name"]')
            if author_el:
                author_found = clean_text(await author_el.inner_text())

            book_title_found = title # Default to search title
            title_el = await page.query_selector('[data-testid="bookTitle"], #bookTitle')
            if title_el:
                book_title_found = clean_text(await title_el.inner_text())

            return {
                "GoodReads_Series_URL": series_url,
                "GoodReads_Book_URL": page.url,
                "GoodReads_Rating": avg_rating,
                "GoodReads_Rating_Count": rating_count,
                "Genre": genre_main,
                "Sub_Genre": genre_sub,
                "Romantasy_Subgenre": is_romantasy,
                "Description": description,
                "Num_Primary_Books": series_data["Num_Primary_Books"],
                "Book1_Rating": series_data["Book1_Rating"],
                "Book1_Num_Ratings": series_data["Book1_Num_Ratings"],
                "Author_Found": author_found,
                "Book_Title": book_title_found
            }
        except Exception as e:
            print(f"  Goodreads: Error: {e}")
            return {}
        finally:
            await page.close()
