"""
NY Literary titles scraper
==========================
Scrapes book titles and author names from nyliterary.com category pages.

The site is protected by Incapsula, so a plain requests.get() returns a challenge
page. We use Playwright with a realistic browser fingerprint, navigate to the URL,
wait for the title list to render, then extract (title, author) pairs.

Usage:
    python backend/scrape_nyliterary.py \
        --url https://nyliterary.com//titles/historical-romance \
        --output outputs/nyliterary_historical_romance.csv

Optional: --dump-html debug_page.html  -> save the rendered HTML for inspection.
"""

import argparse
import asyncio
import csv
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def clean(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip(" \t\r\n|-/,")


def looks_like_title(text: str) -> bool:
    if not text:
        return False
    if not 2 <= len(text) <= 220:
        return False
    bad = {"home", "titles", "authors", "about", "contact", "submit", "rights",
           "privacy", "terms", "next", "previous", "menu", "search", "back",
           "more", "view all", "load more"}
    if text.lower() in bad:
        return False
    return True


def looks_like_author(text: str) -> bool:
    if not text:
        return False
    if not 2 <= len(text) <= 140:
        return False
    if text.count(" ") > 10:
        return False
    return True


STEALTH_INIT_SCRIPT = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
window.chrome = {runtime: {}};
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications'
        ? Promise.resolve({state: Notification.permission})
        : originalQuery(parameters)
);
"""


async def fetch_rendered_html(
    url: str, timeout: int, dump_html: str | None, headless: bool
) -> str:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        )
        context = await browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1366, "height": 900},
            locale="en-US",
            timezone_id="America/New_York",
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,"
                    "image/avif,image/webp,*/*;q=0.8"
                ),
            },
        )
        await context.add_init_script(STEALTH_INIT_SCRIPT)
        page = await context.new_page()

        print(f"[fetch] navigating to {url} (headless={headless})")
        await page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)

        # Incapsula sets a JS challenge; wait for it to clear and the real DOM to load.
        for attempt in range(12):
            await page.wait_for_timeout(1500)
            content = await page.content()
            if "Incapsula" not in content and "Incap" not in content[:1500]:
                break
            print(f"[fetch] Incapsula still present (attempt {attempt + 1}/12), waiting...")

        try:
            await page.wait_for_load_state("networkidle", timeout=timeout * 1000)
        except Exception:
            print("[fetch] networkidle wait timed out; continuing anyway")

        # Scroll to trigger any lazy-loaded content
        for _ in range(8):
            await page.mouse.wheel(0, 3000)
            await page.wait_for_timeout(500)

        html = await page.content()
        await browser.close()

        if dump_html:
            Path(dump_html).write_text(html, encoding="utf-8")
            print(f"[fetch] rendered HTML saved to {dump_html}")

        return html


def extract_books(html: str) -> list[tuple[str, str]]:
    """Try several extraction strategies; return de-duplicated (title, author) pairs."""
    soup = BeautifulSoup(html, "html.parser")

    # Strip noise
    for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
        tag.decompose()

    records: list[tuple[str, str]] = []

    # Strategy 1: cards with a header element + a "by ..." line or sibling author
    # NY Literary catalog pages typically render each title as a card with the
    # book title in an <h2>/<h3>/<h4>, and the author in a nearby element.
    card_selectors = [
        "article", "li", "div.title", "div.book", "div.card", "div.item",
        "div[class*='title']", "div[class*='book']", "div[class*='card']",
        "div[class*='item']", "div[class*='grid'] > div",
    ]
    seen_cards: set[int] = set()
    for selector in card_selectors:
        for card in soup.select(selector):
            if id(card) in seen_cards:
                continue
            seen_cards.add(id(card))

            heading = card.find(["h1", "h2", "h3", "h4", "h5"])
            if not heading:
                continue
            title = clean(heading.get_text(" ", strip=True))
            if not looks_like_title(title):
                continue

            author = ""
            # 1a: explicit "by ..." text in the card
            card_text = card.get_text("\n", strip=True)
            m = re.search(r"\bby\s+([A-Z][A-Za-z .'\-&,]+)", card_text)
            if m:
                author = clean(m.group(1))

            # 1b: a sibling/following element with class containing 'author'
            if not looks_like_author(author):
                author_node = card.find(attrs={"class": re.compile(r"author", re.I)})
                if author_node:
                    text = clean(author_node.get_text(" ", strip=True))
                    text = re.sub(r"^by\s+", "", text, flags=re.I)
                    author = text

            # 1c: a paragraph or span immediately after the heading
            if not looks_like_author(author):
                sibling = heading.find_next_sibling()
                if sibling:
                    text = clean(sibling.get_text(" ", strip=True))
                    text = re.sub(r"^by\s+", "", text, flags=re.I)
                    if looks_like_author(text):
                        author = text

            if looks_like_title(title) and looks_like_author(author):
                records.append((title, author))

    # Strategy 2: free-text "Title by Author" patterns anywhere in the page
    if not records:
        body_text = soup.get_text("\n", strip=True)
        for line in body_text.splitlines():
            line = clean(line)
            m = re.match(r"^(?P<title>.{2,200}?)\s+by\s+(?P<author>[A-Z][A-Za-z .'\-&,]+)$", line)
            if m:
                title = clean(m.group("title"))
                author = clean(m.group("author"))
                if looks_like_title(title) and looks_like_author(author):
                    records.append((title, author))

    # Dedup, preserving order
    seen: set[tuple[str, str]] = set()
    unique: list[tuple[str, str]] = []
    for title, author in records:
        key = (title.lower(), author.lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append((title, author))
    return unique


def write_csv(records: list[tuple[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["Book Title", "Author Name"])
        writer.writerows(records)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="Category page URL to scrape.")
    parser.add_argument("--output", help="CSV output path. Default: outputs/nyliterary_<slug>.csv")
    parser.add_argument("--timeout", type=int, default=45, help="Per-step timeout in seconds.")
    parser.add_argument("--dump-html", help="Save the rendered HTML to this path for debugging.")
    parser.add_argument(
        "--headed", action="store_true",
        help="Run the browser visibly. Often required to defeat Incapsula's bot check.",
    )
    return parser.parse_args()


def default_output_path(url: str) -> Path:
    slug = urlparse(url).path.strip("/").replace("/", "_") or "page"
    return Path("outputs") / f"nyliterary_{slug}.csv"


async def main_async() -> int:
    args = parse_args()
    output_path = Path(args.output) if args.output else default_output_path(args.url)

    html = await fetch_rendered_html(
        args.url,
        timeout=args.timeout,
        dump_html=args.dump_html,
        headless=not args.headed,
    )
    records = extract_books(html)

    print(f"[extract] {len(records)} unique (title, author) pairs found")
    for title, author in records[:10]:
        print(f"  - {title}  |  {author}")
    if len(records) > 10:
        print(f"  ... and {len(records) - 10} more")

    write_csv(records, output_path)
    print(f"[done] CSV written to {output_path.resolve()}")
    return 0 if records else 1


def main() -> None:
    sys.exit(asyncio.run(main_async()))


if __name__ == "__main__":
    main()
