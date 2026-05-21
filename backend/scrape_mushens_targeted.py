"""
Targeted recovery for the Mushens rows that the main scraper couldn't find.

Strategy:
  1. Navigate to the author's Goodreads profile page directly.
  2. List all of the author's books.
  3. Fuzzy-match the target title against the listed titles.
  4. Open the matched book page and extract metadata.

Falls back to the standard scraper if author-page strategy fails.
"""

import asyncio
import os
import re
import sys
import json
from difflib import SequenceMatcher

import pandas as pd
from playwright.async_api import async_playwright

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from goodreads_scraper import GoodreadsScraper, clean_text
from format_mushens import format_mushens

CONCURRENCY = 5


def title_similarity(a, b):
    a = re.sub(r'[^\w\s]', ' ', (a or '').lower())
    b = re.sub(r'[^\w\s]', ' ', (b or '').lower())
    a = re.sub(r'\s+', ' ', a).strip()
    b = re.sub(r'\s+', ' ', b).strip()
    return SequenceMatcher(None, a, b).ratio()


def title_keywords(title):
    """Strip filler words; return the core distinctive tokens."""
    t = (title or '').lower()
    t = re.sub(r'\bseries\b', '', t)
    t = re.sub(r'\bfeat\..*', '', t)
    t = re.sub(r'\(.*?\)', '', t)
    t = re.sub(r'[^\w\s]', ' ', t)
    fillers = {'the', 'a', 'an', 'of', 'to', 'and', 'or', 'in', 'on', 'at'}
    toks = [w for w in t.split() if w and w not in fillers]
    return toks


async def find_via_author_page(page, scraper, title, author):
    """Search by author, navigate to their profile, fuzzy-match title."""
    search_url = f"https://www.goodreads.com/search?q={author.replace(' ', '+')}"
    await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
    await asyncio.sleep(2.0)

    # Click first author result
    author_link = await page.query_selector('a.authorName, .authorName__container a, a[href*="/author/show/"]')
    if not author_link:
        return None

    author_url = await author_link.evaluate("el => el.href")
    if '/author/show/' not in author_url:
        # Might be a book link — try to walk up to the author
        return None

    await page.goto(author_url, wait_until="domcontentloaded", timeout=45000)
    await asyncio.sleep(2.0)

    # Some author pages have a "See all books" link — but the front page books are usually enough
    book_anchors = await page.query_selector_all('a.bookTitle, [data-testid="bookTitle"] a, a[href*="/book/show/"]')

    best_score = 0.0
    best_url = None
    target_keywords = set(title_keywords(title))

    for el in book_anchors:
        try:
            href = await el.evaluate("el => el.href")
            if '/book/show/' not in href:
                continue
            t = clean_text(await el.inner_text())
            if not t:
                continue
            sim = title_similarity(title, t)
            kws = set(title_keywords(t))
            # Bonus when distinctive keywords overlap
            overlap = len(target_keywords & kws) / max(1, len(target_keywords))
            score = max(sim, overlap)
            if score > best_score:
                best_score = score
                best_url = href
        except Exception:
            continue

    if best_url and best_score >= 0.55:
        return best_url
    return None


async def extract_book_data(scraper, page, book_url, original_title):
    """Navigate to book page and extract metadata using scraper internals."""
    await page.goto(book_url, wait_until="domcontentloaded", timeout=60000)
    await asyncio.sleep(0.8)

    genres = []
    genre_els = await page.query_selector_all('[data-testid="genresList"] .Button__labelItem, .BookPageMetadataSection__genre a')
    for gel in genre_els:
        txt = clean_text(await gel.inner_text())
        if txt and txt not in genres:
            genres.append(txt)

    is_romantasy = "Yes" if any("romantasy" in g.lower() for g in genres) else "No"
    genre_sub = genres[1] if len(genres) > 1 else (genres[0] if genres else "N/A")

    avg_rating = "N/A"
    rating_count = "N/A"
    try:
        ld_el = await page.query_selector('script[type="application/ld+json"]')
        if ld_el:
            ld_data = json.loads(await ld_el.inner_text())
            if isinstance(ld_data, list):
                ld_data = ld_data[0]
            avg_rating = str(ld_data.get('aggregateRating', {}).get('ratingValue', 'N/A'))
            rating_count = str(ld_data.get('aggregateRating', {}).get('ratingCount', 'N/A'))
    except Exception:
        pass

    description = "N/A"
    desc_el = await page.query_selector('[data-testid="description"] .Formatted, .readable')
    if desc_el:
        description = clean_text(await desc_el.inner_text())

    series_url = "N/A"
    series_link = await page.query_selector('h3.Text__title3 a[href*="/series/"], [data-testid="series"] a')
    if series_link:
        series_url = await series_link.evaluate("el => el.href")

    num_primary = "1"
    book1_rating = avg_rating
    book1_ratings = rating_count
    if series_url != "N/A":
        try:
            await page.goto(series_url, wait_until="domcontentloaded", timeout=60000)
            content = await page.content()
            m = re.search(r'(\d+)\s+primary\s+works', content, re.IGNORECASE)
            if m:
                num_primary = m.group(1)
            row1 = await page.query_selector('.listWithDividers__item, .seriesWork')
            if row1:
                rtxt = (await row1.inner_text()).lower()
                r_match = re.search(r'([\d.]+)\s+avg\s+rating\s+[—\-]\s+([\d,]+)\s+ratings', rtxt)
                if r_match:
                    book1_rating = r_match.group(1)
                    book1_ratings = r_match.group(2).replace(',', '')
        except Exception:
            pass

    return {
        "GoodReads_Series_URL": series_url,
        "GoodReads_Book_URL": book_url,
        "GoodReads_Rating": avg_rating,
        "GoodReads_Rating_Count": rating_count,
        "Sub_Genre": genre_sub,
        "Romantasy_Subgenre": is_romantasy,
        "Description": description,
        "Num_Primary_Books": num_primary,
        "Book1_Rating": book1_rating,
        "Book1_Num_Ratings": book1_ratings,
    }


def save_book_data(df, idx, data):
    link = data.get("GoodReads_Series_URL")
    if not link or link == "N/A":
        link = data.get("GoodReads_Book_URL", "N/A")
    df.at[idx, "GoodReads series link"]                 = link
    df.at[idx, "Number of PRIMARY books in the series"] = data.get("Num_Primary_Books", "1")
    df.at[idx, "Rating (out of 5) of Primary Book 1"]   = data.get("Book1_Rating",      data.get("GoodReads_Rating", "N/A"))
    df.at[idx, "Ratings (#) of Primary Book 1"]         = data.get("Book1_Num_Ratings", data.get("GoodReads_Rating_Count", "N/A"))
    df.at[idx, "Synopsis (if available)"]               = data.get("Description", "N/A")
    df.at[idx, "Romantasy = Yes or No?"]                = data.get("Romantasy_Subgenre", "No")
    df.at[idx, "Romantasy Sub-Genre of series"]         = data.get("Sub_Genre", "N/A")


async def process_row(context, scraper, df, idx, semaphore, excel_path, file_lock):
    async with semaphore:
        title  = str(df.at[idx, "Name of Series"]).strip()
        author = str(df.at[idx, "Author Name"]).strip()
        print(f"  [Targeted] '{title}' by {author}")

        page = await context.new_page()
        try:
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })

            # Strategy 1: author-page fuzzy match
            book_url = None
            if author and author.lower() not in ("various authors", "various authors (feat. laura purcell)"):
                # Strip "(feat. ...)" suffix when present
                clean_author = re.sub(r'\s*\(.*?\)\s*', '', author).strip()
                try:
                    book_url = await find_via_author_page(page, scraper, title, clean_author)
                except Exception as e:
                    print(f"    [Targeted] author-page error: {e}")

            # Strategy 2: title-only Goodreads search (skip 'series' filler)
            if not book_url:
                clean_title = re.sub(r'\bseries\b', '', title, flags=re.IGNORECASE).strip()
                clean_title = re.sub(r'\s+', ' ', clean_title)
                try:
                    search_url = f"https://www.goodreads.com/search?q={clean_title.replace(' ', '+')}"
                    await page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
                    await asyncio.sleep(2.0)
                    # Pick first link whose text loosely matches
                    anchors = await page.query_selector_all('a.bookTitle, [data-testid="bookTitle"] a')
                    target_kws = set(title_keywords(title))
                    for el in anchors[:10]:
                        try:
                            href = await el.evaluate("el => el.href")
                            if '/book/show/' not in href:
                                continue
                            t = clean_text(await el.inner_text())
                            kws = set(title_keywords(t))
                            if target_kws and (len(target_kws & kws) / len(target_kws)) >= 0.6:
                                book_url = href
                                break
                        except Exception:
                            continue
                except Exception as e:
                    print(f"    [Targeted] title-search error: {e}")

            if not book_url:
                print(f"  [Still Not Found] '{title}'")
                df.at[idx, "GoodReads series link"] = "N/A"
                return

            data = await extract_book_data(scraper, page, book_url, title)
            save_book_data(df, idx, data)
            print(f"  [OK] '{title}' -> {df.at[idx, 'GoodReads series link']} | Rating: {df.at[idx, 'Rating (out of 5) of Primary Book 1']}")

        except Exception as e:
            print(f"  [Error] '{title}': {e}")
            df.at[idx, "GoodReads series link"] = "N/A"
        finally:
            try:
                await page.close()
            except Exception:
                pass

            async with file_lock:
                try:
                    df.to_excel(excel_path, index=False)
                except Exception as save_err:
                    print(f"  [Save Error] {save_err}")


async def scrape_targeted(excel_path):
    df = pd.read_excel(excel_path, keep_default_na=False)

    for col in [
        "GoodReads series link",
        "Number of PRIMARY books in the series",
        "Rating (out of 5) of Primary Book 1",
        "Ratings (#) of Primary Book 1",
        "Synopsis (if available)",
        "Romantasy = Yes or No?",
        "Romantasy Sub-Genre of series",
    ]:
        if col in df.columns:
            df[col] = df[col].astype(object)

    rows_to_process = []
    for idx, row in df.iterrows():
        title = str(row.get("Name of Series", "")).strip()
        if not title or title.lower() in ["", "nan"]:
            continue
        link = str(row.get("GoodReads series link", "")).strip()
        if link == "" or link.upper() == "N/A" or link.lower() == "nan":
            rows_to_process.append(idx)

    print(f"Targeted rows to retry: {len(rows_to_process)}\n")
    if not rows_to_process:
        print("Nothing to retry.")
        return

    file_lock = asyncio.Lock()
    semaphore = asyncio.Semaphore(CONCURRENCY)
    scraper   = GoodreadsScraper(headless=False)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        print("[System] Logging in to Goodreads...")
        login_page = await context.new_page()
        await scraper.login_to_goodreads(login_page)
        await login_page.close()
        print(f"[System] Login done. Starting targeted retry with {CONCURRENCY} tabs...\n")

        tasks = [
            process_row(context, scraper, df, idx, semaphore, excel_path, file_lock)
            for idx in rows_to_process
        ]
        await asyncio.gather(*tasks)

        try:
            await browser.close()
        except Exception:
            pass

    print("\nReapplying Mushens styling...")
    format_mushens(excel_path, excel_path)
    print("Done!")


if __name__ == "__main__":
    base       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    excel_path = os.path.join(base, "Mushens_Entertainment_Bestsellers.xlsx")
    asyncio.run(scrape_targeted(excel_path))
