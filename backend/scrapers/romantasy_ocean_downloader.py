import os
import urllib.parse
from typing import List
from playwright.sync_api import sync_playwright
from backend.models.book_task import BookDownloadTask
import time
from concurrent.futures import ThreadPoolExecutor
import re

def sanitize_filename(name: str) -> str:
    """Removes invalid characters for Windows filenames"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '')
    return name.strip()

def score_match(text, title, author):
    text_clean = set(re.sub(r'[^\w\s]', '', text.lower()).split())
    title_clean = re.sub(r'[^\w\s]', '', title.lower()).split()
    
    if not title_clean:
        return 0
        
    title_matches = sum(1 for w in title_clean if w in text_clean)
    title_ratio = title_matches / len(title_clean)
    
    # Must match at least 60% of the title words
    if title_ratio < 0.6:
        return 0
        
    score = title_ratio * 10
    
    if author:
        author_clean = set(re.sub(r'[^\w\s]', '', author.lower()).split())
        author_matches = sum(1 for w in author_clean if len(w) > 2 and w in text_clean)
        if author_matches > 0:
            score += 5
            
    # Penalize if result has way too many extra words (likely an omnibus/box set)
    if len(text_clean) > len(title_clean) + 15:
        score -= 5
        
    return score

def download_book_sync(task: BookDownloadTask, download_dir: str):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                channel="chrome",
                args=["--disable-blink-features=AutomationControlled"]
            )
            context = browser.new_context(
                accept_downloads=True
            )
            page = context.new_page()
            
            search_query = task.title
            if getattr(task, 'author', None):
                search_query = f"{task.title} by {task.author}"
            query = urllib.parse.quote(search_query)
            search_url = f"https://oceanofpdf.com/?s={query}"
            
            for search_attempt in range(5):
                if search_attempt == 0:
                    print(f"[OceanOfPDF] [{task.title}] Searching: {search_url} (Attempt {search_attempt+1}/5)")
                    page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
                else:
                    print(f"[OceanOfPDF] [{task.title}] Waiting and retrying search page check... (Attempt {search_attempt+1}/5)")
                
                page.wait_for_timeout(5000) # Give cloudflare a chance
                
                # Look for all links
                try:
                    links_data = page.evaluate("""
                        () => {
                            const links = Array.from(document.querySelectorAll("a"));
                            return links.map(a => {
                                let textContext = a.innerText;
                                if (!textContext || textContext.trim().length < 3) {
                                    textContext = a.getAttribute('title') || a.getAttribute('aria-label') || '';
                                    if (!textContext) {
                                        let container = a.closest('h2') || a.closest('h3') || a.parentElement;
                                        textContext = container ? container.innerText : '';
                                    }
                                }
                                return {
                                    href: a.href,
                                    text: textContext ? textContext.replace(/\\n/g, ' ').trim() : ''
                                };
                            });
                        }
                    """)
                except Exception as eval_err:
                    print(f"[OceanOfPDF] [{task.title}] Cloudflare redirect detected during evaluation. Retrying...")
                    page.wait_for_timeout(2000)
                    continue
                
                best_link = None
                best_score = 0
                
                for item in links_data:
                    text = item['text']
                    href = item['href']
                    # Skip common non-book links that might accidentally match title words
                    if not href or "oceanofpdf.com" not in href or "donate" in href or "/category/" in href or "/author/" in href:
                        continue
                    
                    if len(text) > 5 and not text.lower() == "oceanofpdf":
                        score = score_match(text, task.title, getattr(task, 'author', ''))
                        if score > best_score:
                            best_score = score
                            best_link = {'href': href, 'text': text}
                                
                if not best_link:
                    if search_attempt < 4:
                        print(f"[OceanOfPDF] [{task.title}] No valid results found. Retrying in 5 seconds...")
                        page.wait_for_timeout(5000)
                        continue
                    else:
                        task.status = "failed"
                        task.error_message = "No search results found after 5 attempts."
                        print(f"[OceanOfPDF] [{task.title}] Gave up after 5 failed search attempts.")
                        browser.close()
                        return
                    
                # Click the best matched result in a NEW TAB as requested
                target_url = best_link['href']
                
                print(f"[OceanOfPDF] [{task.title}] Attempting to click correct result and bypass ads: {target_url}")
                book_page = None
                for click_attempt in range(5):
                    try:
                        with context.expect_page(timeout=15000) as new_page_info:
                            page.evaluate(f"""
                                () => {{
                                    const links = Array.from(document.querySelectorAll("a")).filter(a => a.href === '{target_url}');
                                    if (links.length > 0) {{
                                        links[0].setAttribute('target', '_blank');
                                        links[0].click();
                                    }}
                                }}
                            """)
                        popup_page = new_page_info.value
                        popup_page.wait_for_load_state("domcontentloaded")
                        
                        popup_url = popup_page.url
                        if "oceanofpdf.com" in popup_url and "donate" not in popup_url:
                            book_page = popup_page
                            print(f"[OceanOfPDF] [{task.title}] Successfully opened book page on click attempt {click_attempt+1}!")
                            break
                        else:
                            print(f"[OceanOfPDF] [{task.title}] Click {click_attempt+1} opened an ad/popup ({popup_url}). Closing and trying again...")
                            popup_page.close()
                            page.wait_for_timeout(1000)
                    except Exception as click_err:
                        print(f"[OceanOfPDF] [{task.title}] Click attempt {click_attempt+1} timed out or failed: {click_err}")
                        
                if not book_page:
                    print(f"[OceanOfPDF] [{task.title}] Failed to open book page after 5 clicks, falling back to goto...")
                    book_page = context.new_page()
                    book_page.goto(target_url, wait_until="domcontentloaded")
                    book_page.wait_for_load_state("domcontentloaded")
                
                # Check for Cloudflare challenge and wait if present
                for _ in range(15):
                    content = book_page.content().lower()
                    if "cloudflare" in content or "security verification" in content or "verify you are human" in content:
                        print(f"[OceanOfPDF] [{task.title}] Cloudflare challenge detected! Waiting 2 seconds...")
                        book_page.wait_for_timeout(2000)
                    else:
                        break
                
                # Find the PDF download form or link
                # First try the classic form
                pdf_form = book_page.locator("form[action*='Fetching_Resource.php'], form[action*='Get_Resource.php']").filter(has=book_page.locator("input[name='filename'][value$='.pdf']")).first
                
                # If classic form fails, try finding any form with a PDF button
                if pdf_form.count() == 0:
                    pdf_form = book_page.locator("form").filter(has=book_page.locator("button, input[type='submit']").filter(has_text="PDF")).first
                
                # If forms fail, try finding a direct download link
                pdf_link = None
                if pdf_form.count() == 0:
                    pdf_link = book_page.locator("a").filter(has_text="PDF").first
                    
                if pdf_form.count() == 0 and (pdf_link is None or pdf_link.count() == 0):
                    if search_attempt < 9:
                        print(f"[OceanOfPDF] [{task.title}] Could not find PDF download form or link on page. Retrying search...")
                        book_page.close()
                        continue
                    else:
                        task.status = "failed"
                        task.error_message = "Could not find PDF download form or link."
                        print(f"[OceanOfPDF] [{task.title}] Could not find PDF download form or link.")
                        browser.close()
                        return
                    
                print(f"[OceanOfPDF] [{task.title}] Found PDF download trigger, initiating download sequence...")
                download = None
                for dl_attempt in range(5):
                    print(f"[OceanOfPDF] [{task.title}] Attempting to trigger PDF download (Attempt {dl_attempt+1})...")
                    try:
                        with book_page.expect_download(timeout=15000) as download_info:
                            if pdf_form.count() > 0:
                                pdf_form.evaluate("form => { form.removeAttribute('target'); form.submit(); }")
                            else:
                                pdf_link.evaluate("a => { a.removeAttribute('target'); a.click(); }")
                                
                        download = download_info.value
                        print(f"[OceanOfPDF] [{task.title}] Download successfully triggered on attempt {dl_attempt+1}!")
                        break
                    except Exception as e:
                        print(f"[OceanOfPDF] [{task.title}] Download trigger attempt {dl_attempt+1} failed/timed out (likely an ad intercepted it).")
                        # If the ad navigated our current page away from OceanOfPDF, go back!
                        if "oceanofpdf.com" not in book_page.url:
                            print(f"[OceanOfPDF] [{task.title}] Click navigated to ad ({book_page.url}). Going back to book page...")
                            book_page.go_back(wait_until="domcontentloaded")
                            book_page.wait_for_timeout(2000)
                        
                        # Close any popups/ads that opened in new tabs
                        for p in context.pages:
                            if p != page and p != book_page:
                                try:
                                    print(f"[OceanOfPDF] [{task.title}] Closing ad popup: {p.url}")
                                    p.close()
                                except:
                                    pass
                                    
                if not download:
                    if search_attempt < 4:
                        print(f"[OceanOfPDF] [{task.title}] Failed to trigger download after 5 attempts. Retrying entire search...")
                        book_page.close()
                        continue
                    else:
                        task.status = "failed"
                        task.error_message = "Failed to trigger download after 5 attempts due to ads."
                        print(f"[OceanOfPDF] [{task.title}] Download completely failed.")
                        book_page.close()
                        break
                        
                try:
                    safe_title = sanitize_filename(task.title)
                    file_name = f"{task.number}_{safe_title}.pdf"
                    pdf_path = os.path.join(download_dir, file_name)
                    download.save_as(pdf_path)
                    
                    task.pdf_path = pdf_path
                    task.status = "downloaded"
                    task.source = "OceanOfPDF"
                    print(f"[OceanOfPDF] [{task.title}] Successfully downloaded to {pdf_path}")
                    book_page.close()
                    break # Success! break out of the 10-attempt loop
                except Exception as e:
                    if search_attempt < 4:
                        print(f"[OceanOfPDF] [{task.title}] Failed to save download: {e}. Retrying search...")
                        book_page.close()
                        continue
                    else:
                        task.status = "failed"
                        task.error_message = f"Failed to save download: {str(e)}"
                        print(f"[OceanOfPDF] [{task.title}] Download save failed: {e}")
                        book_page.close()
                        break
                    
            browser.close()
    except Exception as e:
        task.status = "failed"
        task.error_message = str(e)
        print(f"[OceanOfPDF] [{task.title}] Exception: {e}")

def process_ocean_downloads(books: List[BookDownloadTask], download_dir: str):
    """
    Downloads books from OceanOfPDF with a concurrency limit.
    """
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
        
    pending = [b for b in books if b.status == "pending"]
    if not pending:
        return
        
    with ThreadPoolExecutor(max_workers=3) as executor:
        for book in pending:
            executor.submit(download_book_sync, book, download_dir)
            time.sleep(2) # stagger launches

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        title = sys.argv[1]
    else:
        title = "The Sex Club"
    b = BookDownloadTask(title=title, number=1)
    process_ocean_downloads([b], "e:\\Internship\\PocketFM\\downloads\\test_series")
    print(f"Result: {b}")
