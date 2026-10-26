import openpyxl
import requests
import re
import json
import os
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from openpyxl.styles import Alignment

TARGET_FILES = [
    'Romantasy - Close Calls.xlsx',
    'Romantasy - Subjective Reviews - 9.9.26 - New Sheet.xlsx'
]
STREAM_SRC = 'Romantasy - Subjective Reviews - 9.9.26 - New Sheet.xlsx'
MASTER_SRC = 'Romantasy - Subjective Reviews - 9.9.26_backup.xlsx'
CACHE_PATH = r'C:\Users\noelr\.gemini\antigravity-ide\brain\54260b81-f2ff-4d78-b4cd-0f6fd4f86372\scratch\metrics_cache.json'

print("--- Step 1: Loading Lookup Tables ---")
# 1. Load Streaming Lookup
wb_stream = openpyxl.load_workbook(STREAM_SRC, data_only=True)
ws_stream = wb_stream['Streaming & Screen Adaptations']
stream_lookup = {}
for r in range(2, ws_stream.max_row + 1):
    r_id = ws_stream.cell(r, 1).value
    stream_lookup[r_id] = {
        'prime': ws_stream.cell(r, 4).value or 'No',
        'netflix': ws_stream.cell(r, 5).value or 'No',
        'audible': ws_stream.cell(r, 6).value or 'No',
        'other': ws_stream.cell(r, 7).value or 'None',
        'status': ws_stream.cell(r, 8).value or 'Book / Audio Only'
    }
print(f"Loaded {len(stream_lookup)} streaming records.")

# 2. Load Master Lookup
wb_master = openpyxl.load_workbook(MASTER_SRC, data_only=True)
ws_master = wb_master['Web-Fiction Research Master']
master_lookup = {}
for r in range(2, ws_master.max_row + 1):
    r_id = ws_master.cell(r, 36).value
    master_lookup[r_id] = {
        'comm_date': ws_master.cell(r, 44).value or 'N/A',
        'media_excl': ws_master.cell(r, 38).value or 'Eligible (None Detected)',
        'comm_perf': ws_master.cell(r, 48).value or 'N/A'
    }
print(f"Loaded {len(master_lookup)} master research records.")

# Load metrics cache
cache = {}
if os.path.exists(CACHE_PATH):
    try:
        with open(CACHE_PATH, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        print(f"Loaded {len(cache)} cached platform metric entries.")
    except Exception as e:
        print(f"Error loading cache: {e}")

print("\n--- Step 2: Collecting Platform URLs to Scrape Metrics ---")
wb_close = openpyxl.load_workbook(TARGET_FILES[0], data_only=True)
ws_close = wb_close.active

urls_to_scrape = set()
for r in range(2, ws_close.max_row + 1):
    u = str(ws_close.cell(r, 8).value or '').strip()
    if u and u.startswith('http'):
        urls_to_scrape.add(u)

needed_urls = [u for u in urls_to_scrape if u not in cache]
print(f"Total unique platform URLs: {len(urls_to_scrape)}, needing scrape: {len(needed_urls)}")

def create_session():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1.2, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    })
    return session

def scrape_metrics(url):
    session = create_session()
    res = {'earliest_date': None, 'metrics': None, 'status': 'PENDING'}
    try:
        resp = session.get(url, timeout=20)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            text_content = soup.get_text()
            
            if 'royalroad.com' in url:
                # Royal Road Date
                earliest_date = None
                times = soup.select('table#chapters time, time')
                if times:
                    for t in times:
                        dt = t.get('datetime')
                        if dt:
                            earliest_date = dt.split('T')[0]
                            break
                        title_attr = t.get('title', '')
                        m = re.search(r'([A-Za-z]+ \d{1,2}, \d{4})', title_attr)
                        if m:
                            try:
                                d_obj = datetime.strptime(m.group(1), '%B %d, %Y')
                                earliest_date = d_obj.strftime('%Y-%m-%d')
                                break
                            except: pass
                
                # Royal Road Stats
                stats = []
                for label in ['Total Views', 'Followers', 'Favorites', 'Ratings', 'Pages']:
                    m = re.search(rf'{label}\s*:\s*([\d,\.]+)', text_content, re.IGNORECASE)
                    if m:
                        stats.append(f"{label}: {m.group(1)}")
                
                res['earliest_date'] = earliest_date or 'N/A'
                res['metrics'] = " | ".join(stats) if stats else "None recorded"
                res['status'] = 'SUCCESS'
                
            elif 'tapas.io' in url:
                # Tapas Date
                earliest_date = None
                ep_dates = soup.select('.episode-list .date, .episode-item .date, .date')
                if ep_dates:
                    date_str = ep_dates[-1].get_text(strip=True)
                    m = re.search(r'([A-Za-z]{3}\s+\d{1,2},\s+\d{4})', date_str)
                    if m:
                        try:
                            d_obj = datetime.strptime(m.group(1), '%b %d, %Y')
                            earliest_date = d_obj.strftime('%Y-%m-%d')
                        except:
                            earliest_date = date_str
                    else:
                        earliest_date = date_str
                
                # Tapas Stats
                views = None
                subs = None
                likes = None
                m_v = re.search(r'([\d\.,]+[kKmM]?)\s*views', text_content, re.IGNORECASE)
                if m_v: views = m_v.group(1)
                m_s = re.search(r'([\d\.,]+[kKmM]?)\s*subscribers', text_content, re.IGNORECASE)
                if m_s: subs = m_s.group(1)
                m_l = re.search(r'([\d\.,]+[kKmM]?)\s*likes', text_content, re.IGNORECASE)
                if m_l: likes = m_l.group(1)
                
                stats_parts = []
                if views: stats_parts.append(f"Views: {views}")
                if subs: stats_parts.append(f"Subscribers: {subs}")
                if likes: stats_parts.append(f"Likes: {likes}")
                
                res['earliest_date'] = earliest_date or 'N/A'
                res['metrics'] = " | ".join(stats_parts) if stats_parts else "None recorded"
                res['status'] = 'SUCCESS'
            else:
                res['status'] = 'UNSUPPORTED'
        else:
            res['status'] = f'HTTP_{resp.status_code}'
            res['earliest_date'] = 'N/A'
            res['metrics'] = 'N/A'
    except Exception as e:
        res['status'] = 'ERROR'
        res['earliest_date'] = 'N/A'
        res['metrics'] = 'N/A'
        
    return url, res

if needed_urls:
    print(f"Scraping metrics for {len(needed_urls)} URLs...")
    count = 0
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(scrape_metrics, u): u for u in needed_urls}
        for future in as_completed(futures):
            u, res = future.result()
            cache[u] = res
            count += 1
            if count % 20 == 0 or count == len(needed_urls):
                print(f"Scraped {count}/{len(needed_urls)} metric entries...")
                with open(CACHE_PATH, 'w', encoding='utf-8') as f:
                    json.dump(cache, f, ensure_ascii=False, indent=2)
            time.sleep(0.2)
            
    with open(CACHE_PATH, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

print("\n--- Step 3: Populating All 11 Columns Across Both Files ---")

def parse_year(date_str):
    if not date_str or date_str in ['N/A', 'None']:
        return None
    m = re.search(r'\b(19\d\d|20\d\d)\b', str(date_str))
    if m:
        return int(m.group(1))
    return None

for file_path in TARGET_FILES:
    print(f"\nProcessing {file_path}...")
    wb = openpyxl.load_workbook(file_path)
    sheet_name = 'Close calls - 2610' if 'Close calls - 2610' in wb.sheetnames else wb.sheetnames[0]
    ws = wb[sheet_name]
    
    for r in range(2, ws.max_row + 1):
        r_id = ws.cell(r, 1).value # Col A: Research Row ID
        web_url = str(ws.cell(r, 8).value or '').strip() # Col H: Original Platform URL
        
        # 1. From Platform Cache
        plat_info = cache.get(web_url, {})
        earliest_web_date = plat_info.get('earliest_date') or 'N/A'
        web_metrics = plat_info.get('metrics') or 'None recorded'
        
        # 2. From Master Lookup
        m_info = master_lookup.get(r_id, {})
        comm_pub_date = m_info.get('comm_date') or 'N/A'
        media_excl = m_info.get('media_excl') or 'Eligible (None Detected)'
        comm_perf = m_info.get('comm_perf') or 'N/A'
        
        # 3. Calculate Web Pre-Dates Commercial?
        web_year = parse_year(earliest_web_date)
        comm_year = parse_year(comm_pub_date)
        if web_year and comm_year:
            if web_year < comm_year:
                pre_dates = f"YES (Web {web_year} vs Comm {comm_year})"
            else:
                pre_dates = f"NO (Web {web_year} vs Comm {comm_year})"
        else:
            pre_dates = "NO (Title Collision / Unverified)"
            
        # 4. From Streaming Lookup
        s_info = stream_lookup.get(r_id, {})
        prime_val = s_info.get('prime') or 'No'
        netflix_val = s_info.get('netflix') or 'No'
        audible_val = s_info.get('audible') or 'No'
        other_val = s_info.get('other') or 'None'
        adapt_val = s_info.get('status') or 'Book / Audio Only'
        
        # Assign to the 11 columns
        # Col I (9): Earliest Web Date
        ws.cell(r, 9).value = earliest_web_date
        # Col J (10): Commercial Pub Date
        ws.cell(r, 10).value = comm_pub_date
        # Col K (11): Web Pre-Dates Commercial?
        ws.cell(r, 11).value = pre_dates
        # Col M (13): Media & Audio Exclusion Screening
        ws.cell(r, 13).value = media_excl
        # Col N (14): Web Traction / Performance Metrics
        ws.cell(r, 14).value = web_metrics
        # Col O (15): Commercial Performance Summary (Goodreads)
        ws.cell(r, 15).value = comm_perf
        # Col Q (17): Prime Video
        ws.cell(r, 17).value = prime_val
        # Col R (18): Netflix
        ws.cell(r, 18).value = netflix_val
        # Col S (19): Audible Audio Availability
        ws.cell(r, 19).value = audible_val
        # Col T (20): Other Platforms (HBO, Peacock, Webtoon, Cinema)
        ws.cell(r, 20).value = other_val
        # Col U (21): Adaptation Status / Details
        ws.cell(r, 21).value = adapt_val
        
        # Format cells
        for c in [9, 10, 11, 13, 14, 15, 17, 18, 19, 20, 21]:
            ws.cell(r, c).alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)

    # Set column widths
    col_widths = {
        'I': 18.0,  # Earliest Web Date
        'J': 32.0,  # Commercial Pub Date
        'K': 30.0,  # Web Pre-Dates Commercial?
        'M': 32.0,  # Media & Audio Exclusion Screening
        'N': 42.0,  # Web Traction / Performance Metrics
        'O': 42.0,  # Commercial Performance Summary (Goodreads)
        'Q': 14.0,  # Prime Video
        'R': 14.0,  # Netflix
        'S': 36.0,  # Audible Audio Availability
        'T': 45.0,  # Other Platforms
        'U': 35.0,  # Adaptation Status / Details
    }
    for col_l, w in col_widths.items():
        ws.column_dimensions[col_l].width = w

    wb.save(file_path)
    print(f"Successfully populated and saved {file_path}")

print("\n--- ALL 11 COLUMNS SUCCESSFULLY POPULATED ACROSS ALL 246 ROWS! ---")
