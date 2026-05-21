import argparse
import asyncio
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag


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
    "Name of agent",
]

AUTHOR_PREFIX_RE = re.compile(
    r"^(?:by|author|authors|written by|edited by|from)\s*:?\s+",
    re.IGNORECASE,
)
BAD_TITLE_RE = re.compile(
    r"^(?:home|books|book|titles|catalog|catalogue|fiction|nonfiction|"
    r"about|contact|submit|rights|privacy|terms|next|previous|read more|"
    r"view|learn more|menu|search)$",
    re.IGNORECASE,
)
BAD_AUTHOR_RE = re.compile(
    r"^(?:author|authors|book|books|publisher|agent|agency|read more|"
    r"view|learn more|submit|contact|rights|category|categories)$",
    re.IGNORECASE,
)

TITLE_ATTR_RE = re.compile(r"(?:^|[-_\s])(book[-_\s]*)?(title|name)(?:$|[-_\s])", re.IGNORECASE)
AUTHOR_ATTR_RE = re.compile(
    r"(?:^|[-_\s])(author|authors|byline|creator|writer|contributor)(?:$|[-_\s])",
    re.IGNORECASE,
)
CONTAINER_ATTR_RE = re.compile(
    r"(?:book|title|work|product|card|tile|item|entry|listing|result|catalog)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class BookRecord:
    title: str
    author: str
    method: str
    source_url: str


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    text = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" \t\r\n|-/")


def clean_author(value: Any) -> str:
    text = clean_text(value)
    text = AUTHOR_PREFIX_RE.sub("", text)
    text = re.sub(r"\s+(?:books?|titles?)$", "", text, flags=re.IGNORECASE)
    return clean_text(text)


def normalize_key(title: str, author: str) -> tuple[str, str]:
    def norm(value: str) -> str:
        value = value.lower()
        value = re.sub(r"[\W_]+", " ", value)
        return re.sub(r"\s+", " ", value).strip()

    return norm(title), norm(author)


def is_plausible_title(title: str) -> bool:
    title = clean_text(title)
    if not 2 <= len(title) <= 220:
        return False
    if BAD_TITLE_RE.fullmatch(title):
        return False
    if title.count(" ") > 28:
        return False
    return True


def is_plausible_author(author: str) -> bool:
    author = clean_author(author)
    if not 2 <= len(author) <= 140:
        return False
    if BAD_AUTHOR_RE.fullmatch(author):
        return False
    if author.count(" ") > 12:
        return False
    return True


def node_text(node: Tag | None) -> str:
    if not node:
        return ""
    return clean_text(node.get_text(" ", strip=True))


def attr_blob(node: Tag) -> str:
    parts: list[str] = []
    for attr in ("class", "id", "itemprop", "property", "data-testid", "aria-label"):
        value = node.get(attr)
        if isinstance(value, list):
            parts.extend(str(item) for item in value)
        elif value:
            parts.append(str(value))
    return " ".join(parts)


def add_record(
    records: list[BookRecord],
    title: Any,
    author: Any,
    method: str,
    source_url: str,
) -> None:
    clean_title = clean_text(title)
    clean_by = clean_author(author)
    if is_plausible_title(clean_title) and is_plausible_author(clean_by):
        records.append(BookRecord(clean_title, clean_by, method, source_url))


def flatten_json_ld(payload: Any) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if isinstance(payload, list):
        for item in payload:
            items.extend(flatten_json_ld(item))
    elif isinstance(payload, dict):
        items.append(payload)
        graph = payload.get("@graph")
        if isinstance(graph, list):
            items.extend(flatten_json_ld(graph))
    return items


def jsonld_type_matches(item: dict[str, Any], expected: str) -> bool:
    item_type = item.get("@type")
    if isinstance(item_type, list):
        return any(str(value).lower() == expected.lower() for value in item_type)
    return str(item_type).lower() == expected.lower()


def extract_author_from_json(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return clean_text(value.get("name") or value.get("givenName") or "")
    if isinstance(value, list):
        authors = [extract_author_from_json(item) for item in value]
        return ", ".join(author for author in authors if author)
    return ""


def extract_json_ld(soup: BeautifulSoup, source_url: str) -> list[BookRecord]:
    records: list[BookRecord] = []
    for script in soup.find_all("script", type=lambda value: value and "ld+json" in value):
        raw = script.string or script.get_text()
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        for item in flatten_json_ld(payload):
            if not jsonld_type_matches(item, "Book"):
                continue
            title = item.get("name") or item.get("headline")
            author = extract_author_from_json(item.get("author") or item.get("creator"))
            add_record(records, title, author, "json-ld", source_url)
    return records


def find_first_by_attr_pattern(root: Tag, pattern: re.Pattern[str]) -> Tag | None:
    for node in root.find_all(True):
        if pattern.search(attr_blob(node)):
            text = node_text(node)
            if text:
                return node
    return None


def find_best_title_node(container: Tag) -> Tag | None:
    selectors = [
        '[itemprop="name"]',
        '[property="name"]',
        'a[href*="book"]',
        'a[href*="title"]',
        "h1",
        "h2",
        "h3",
        "h4",
    ]
    for selector in selectors:
        for node in container.select(selector):
            if is_plausible_title(node_text(node)):
                return node
    return find_first_by_attr_pattern(container, TITLE_ATTR_RE)


def find_best_author_node(container: Tag) -> Tag | None:
    selectors = [
        '[itemprop="author"]',
        '[rel="author"]',
        'a[href*="author"]',
        'a[href*="authors"]',
    ]
    for selector in selectors:
        for node in container.select(selector):
            if is_plausible_author(node_text(node)):
                return node
    return find_first_by_attr_pattern(container, AUTHOR_ATTR_RE)


def extract_microdata_cards(soup: BeautifulSoup, source_url: str) -> list[BookRecord]:
    records: list[BookRecord] = []
    for container in soup.select('[itemscope][itemtype*="Book"], [typeof*="Book"]'):
        title_node = container.select_one('[itemprop="name"], [property="name"]')
        author_node = container.select_one('[itemprop="author"], [property="author"], [rel="author"]')
        add_record(records, node_text(title_node), node_text(author_node), "microdata", source_url)
    return records


def extract_custom_selectors(
    soup: BeautifulSoup,
    source_url: str,
    item_selector: str | None,
    title_selector: str | None,
    author_selector: str | None,
) -> list[BookRecord]:
    if not title_selector or not author_selector:
        return []

    records: list[BookRecord] = []
    if item_selector:
        for item in soup.select(item_selector):
            title_node = item.select_one(title_selector)
            author_node = item.select_one(author_selector)
            add_record(records, node_text(title_node), node_text(author_node), "custom-selectors", source_url)
        return records

    title_nodes = soup.select(title_selector)
    author_nodes = soup.select(author_selector)
    for title_node, author_node in zip(title_nodes, author_nodes):
        add_record(records, node_text(title_node), node_text(author_node), "custom-selectors", source_url)
    return records


def extract_dom_cards(soup: BeautifulSoup, source_url: str) -> list[BookRecord]:
    records: list[BookRecord] = []
    containers: list[Tag] = []
    for node in soup.find_all(["article", "li", "section", "div"]):
        blob = attr_blob(node)
        text = node_text(node)
        if not text or len(text) > 1800:
            continue
        if CONTAINER_ATTR_RE.search(blob):
            containers.append(node)

    for container in containers:
        title_node = find_best_title_node(container)
        author_node = find_best_author_node(container)
        add_record(records, node_text(title_node), node_text(author_node), "dom-card", source_url)

    return records


def extract_title_by_author_lines(soup: BeautifulSoup, source_url: str) -> list[BookRecord]:
    records: list[BookRecord] = []
    blocks = soup.find_all(["article", "li", "p", "div"])
    by_patterns = [
        re.compile(r"^(?P<title>.+?)\s+by\s+(?P<author>[A-Z][A-Za-z .'\-&,]+)$"),
        re.compile(r"^(?P<title>.+?)\s+-\s+(?P<author>[A-Z][A-Za-z .'\-&,]+)$"),
    ]

    for block in blocks:
        text = node_text(block)
        if not text or len(text) > 260:
            continue
        for pattern in by_patterns:
            match = pattern.match(text)
            if match:
                add_record(
                    records,
                    match.group("title"),
                    match.group("author"),
                    "text-pattern",
                    source_url,
                )
                break

    for block in soup.find_all(["article", "li", "div"]):
        lines = [
            clean_text(part)
            for part in block.get_text("\n", strip=True).splitlines()
            if clean_text(part)
        ]
        if not 2 <= len(lines) <= 8:
            continue
        for index, line in enumerate(lines[:-1]):
            next_line = lines[index + 1]
            if AUTHOR_PREFIX_RE.match(next_line):
                add_record(records, line, next_line, "adjacent-lines", source_url)

    return records


def extract_meta_pair(soup: BeautifulSoup, source_url: str) -> list[BookRecord]:
    records: list[BookRecord] = []
    title_meta = soup.select_one(
        'meta[property="og:title"], meta[name="twitter:title"], meta[name="title"]'
    )
    author_meta = soup.select_one(
        'meta[name="author"], meta[property="book:author"], meta[name="citation_author"]'
    )
    if title_meta and author_meta:
        add_record(
            records,
            title_meta.get("content"),
            author_meta.get("content"),
            "metadata",
            source_url,
        )
    return records


def dedupe_records(records: list[BookRecord], keep_duplicates: bool) -> list[BookRecord]:
    if keep_duplicates:
        return records
    seen: set[tuple[str, str]] = set()
    unique: list[BookRecord] = []
    for record in records:
        key = normalize_key(record.title, record.author)
        if key in seen:
            continue
        seen.add(key)
        unique.append(record)
    return unique


def parse_books_from_html(
    html: str,
    source_url: str,
    item_selector: str | None = None,
    title_selector: str | None = None,
    author_selector: str | None = None,
    keep_duplicates: bool = False,
) -> list[BookRecord]:
    soup = BeautifulSoup(html, "html.parser")

    records: list[BookRecord] = []
    records.extend(
        extract_custom_selectors(
            soup,
            source_url,
            item_selector=item_selector,
            title_selector=title_selector,
            author_selector=author_selector,
        )
    )
    records.extend(extract_json_ld(soup, source_url))

    for unwanted in soup(["script", "style", "noscript", "svg"]):
        unwanted.decompose()

    records.extend(extract_microdata_cards(soup, source_url))
    records.extend(extract_meta_pair(soup, source_url))
    records.extend(extract_dom_cards(soup, source_url))
    records.extend(extract_title_by_author_lines(soup, source_url))

    return dedupe_records(records, keep_duplicates=keep_duplicates)


def fetch_static_html(url: str, timeout: int) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.text


async def fetch_rendered_html(url: str, timeout: int) -> str:
    from playwright.async_api import async_playwright

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            )
        )
        await page.goto(url, wait_until="networkidle", timeout=timeout * 1000)
        html = await page.content()
        await browser.close()
        return html


def find_next_url(html: str, current_url: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    link = soup.select_one('link[rel~="next"], a[rel~="next"]')
    if link and link.get("href"):
        return urljoin(current_url, link["href"])

    for anchor in soup.find_all("a", href=True):
        label = clean_text(anchor.get_text(" ", strip=True)).lower()
        blob = attr_blob(anchor).lower()
        if label in {"next", "next page", "older", "more"} or "next" in blob:
            return urljoin(current_url, anchor["href"])
    return None


def scrape_url_pages(args: argparse.Namespace) -> list[BookRecord]:
    records: list[BookRecord] = []
    visited: set[str] = set()
    current_url = args.url

    for page_number in range(1, args.max_pages + 1):
        if not current_url or current_url in visited:
            break
        visited.add(current_url)

        print(f"[scrape] Fetching page {page_number}: {current_url}")
        if args.rendered:
            html = asyncio.run(fetch_rendered_html(current_url, timeout=args.timeout))
        else:
            html = fetch_static_html(current_url, timeout=args.timeout)

        page_records = parse_books_from_html(
            html,
            current_url,
            item_selector=args.item_selector,
            title_selector=args.title_selector,
            author_selector=args.author_selector,
            keep_duplicates=args.keep_duplicates,
        )
        print(f"[scrape] Found {len(page_records)} title/author pairs on this page")
        records.extend(page_records)

        if args.max_pages <= page_number:
            break
        current_url = find_next_url(html, current_url)

    return dedupe_records(records, keep_duplicates=args.keep_duplicates)


def records_to_dataframe(records: list[BookRecord], simple: bool) -> pd.DataFrame:
    if simple:
        return pd.DataFrame(
            [{"Book Title": record.title, "Author Name": record.author} for record in records],
            columns=["Book Title", "Author Name"],
        )

    rows = []
    for record in records:
        row = {header: "" for header in ELEVEN_COLUMN_HEADERS}
        row["Name of Series"] = record.title
        row["Author Name"] = record.author
        rows.append(row)
    return pd.DataFrame(rows, columns=ELEVEN_COLUMN_HEADERS)


def output_path_from_args(args: argparse.Namespace) -> Path:
    if args.output:
        return Path(args.output)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.url:
        host = urlparse(args.url).netloc.replace("www.", "").replace(".", "_") or "site"
    else:
        host = "html_file"
    return Path("outputs") / f"scraped_books_{host}_{stamp}.xlsx"


def write_output(df: pd.DataFrame, args: argparse.Namespace) -> Path:
    output_path = output_path_from_args(args)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.append_to:
        if args.simple:
            raise ValueError("--append-to is only supported with the default 11-column format")

        append_path = Path(args.append_to)
        existing = pd.read_excel(append_path, sheet_name=args.sheet_name, dtype=str).fillna("")
        missing = [header for header in ELEVEN_COLUMN_HEADERS if header not in existing.columns]
        if missing:
            raise ValueError(f"Append target is missing expected 11-column headers: {missing}")

        existing = existing[ELEVEN_COLUMN_HEADERS]
        df = pd.concat([existing, df], ignore_index=True)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        sheet_name = args.sheet_name if not args.simple else "Scraped Books"
        df.to_excel(writer, index=False, sheet_name=sheet_name)

        worksheet = writer.sheets[sheet_name]
        worksheet.freeze_panes = "A2"
        worksheet.auto_filter.ref = worksheet.dimensions

        widths = {
            "A": 34,
            "B": 26,
            "C": 22,
            "D": 34,
            "E": 20,
            "F": 18,
            "G": 18,
            "H": 48,
            "I": 18,
            "J": 26,
            "K": 24,
        }
        for column, width in widths.items():
            worksheet.column_dimensions[column].width = width

    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape book names and author names from a website page into Excel."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--url", help="Website URL to scrape.")
    source.add_argument("--html-file", help="Local HTML file to parse instead of fetching a URL.")

    parser.add_argument("--output", help="Output XLSX path. Defaults to outputs/scraped_books_<site>_<time>.xlsx")
    parser.add_argument("--simple", action="store_true", help="Write only Book Title and Author Name columns.")
    parser.add_argument("--append-to", help="Existing 11-column workbook to append scraped rows into.")
    parser.add_argument("--sheet-name", default="Combined Titles", help="Worksheet name for the output/append target.")
    parser.add_argument("--max-pages", type=int, default=1, help="Follow simple next-page links up to this many pages.")
    parser.add_argument("--timeout", type=int, default=30, help="Fetch timeout in seconds.")
    parser.add_argument("--rendered", action="store_true", help="Use Playwright for JavaScript-rendered pages.")
    parser.add_argument("--keep-duplicates", action="store_true", help="Keep exact duplicate title/author pairs.")
    parser.add_argument("--item-selector", help="Optional CSS selector for each book container.")
    parser.add_argument("--title-selector", help="Optional CSS selector for the book title inside each item.")
    parser.add_argument("--author-selector", help="Optional CSS selector for the author inside each item.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.html_file:
        path = Path(args.html_file)
        html = path.read_text(encoding="utf-8")
        records = parse_books_from_html(
            html,
            str(path),
            item_selector=args.item_selector,
            title_selector=args.title_selector,
            author_selector=args.author_selector,
            keep_duplicates=args.keep_duplicates,
        )
    else:
        records = scrape_url_pages(args)

    df = records_to_dataframe(records, simple=args.simple)
    output_path = write_output(df, args)

    print(f"[done] Rows written: {len(df)}")
    print(f"[done] Output: {output_path.resolve()}")


if __name__ == "__main__":
    main()
