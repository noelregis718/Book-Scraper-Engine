correct_block = """            book_url = existing_url if (existing_url and existing_url != "N/A" and str(existing_url).startswith("http")) else None
            
            # Skip search if we already have a valid book_url
            if book_url:
                print(f"    [Goodreads] Using existing URL: {book_url}")
                
            if not book_url:
                # --- TIER 1: Internal Search (Title + Author Only) ---
                # Use a "Clean" title + Author for search query
                clean_query_title = normalize_title_for_search(title)
                query = f"{clean_query_title} {author}"
                try:
                    print(f"    [Goodreads] Searching: {query}...")
                    # Set headers for the search too
                    await page.set_extra_http_headers({
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    })
                    search_url = f"https://www.goodreads.com/search?q={query.replace(' ', '+')}"
                    await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
                    
                    # Wait for results to actually populate
                    await asyncio.sleep(2.5)
                    
                    # Broad Selection: Grab the first valid book link from any results container
                    first_link = await page.query_selector('a.bookTitle, [data-testid="bookTitle"] a, .bookTitle, [data-testid="bookSearchResult"] a, h3 a[href*="/book/show/"]')
                    
                    if not first_link:
                        # Check for CAPTCHA
                        if await page.query_selector('#captcha-image, .captcha, iframe[src*="captcha"]'):
                            print(f"\\n    [!!! ACTION REQUIRED !!!] CAPTCHA detected for '{title}'! (30s timeout)")
                            try:
                                await page.wait_for_selector('a.bookTitle, [data-testid="bookTitle"] a, .bookTitle', timeout=30000)
                                first_link = await page.query_selector('a.bookTitle, [data-testid="bookTitle"] a, .bookTitle, [data-testid="bookSearchResult"] a')
                            except:
                                print(f"    [Timeout] CAPTCHA not solved in 30s. Falling back to Tier 2...")
                                book_url = None
                                
                    if first_link and not book_url:
                        book_url = await first_link.evaluate("el => el.href")
                        print(f"    [Goodreads] Success! Captured result: {book_url}")
                except Exception as e:
                    print(f"    [Goodreads] Search error: {e}")
                
                # --- TIER 2: External Fallback (Title + Author Only) ---
                if not book_url:
                    search_queries = [
                        f'"{clean_query_title}" {author} goodreads',
                        f'"{title}" {author} site:goodreads.com/book'
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
"""

with open("goodreads_scraper.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
# We need to replace the block from "book_url = existing_url if..." to "if not book_url: return {}"
# The easiest way is to find the indices
start_str = '            book_url = existing_url if'
end_str = '            if not book_url: return {}'

start_idx = content.find(start_str)
end_idx = content.find(end_str) + len(end_str) + 1

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + correct_block + content[end_idx:]
    with open("goodreads_scraper.py", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Replaced block successfully.")
else:
    print("Could not find start or end block.")
