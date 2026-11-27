import os
import sys
import json
import time
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import docx
from docx.oxml.ns import qn

WORKSPACE = r"E:\Internship\PocketFM"
MANIFEST_FILE = os.path.join(WORKSPACE, "shelter_episodes_manifest.json")
OUTPUT_DIR = os.path.join(WORKSPACE, "downloaded_shelter_episodes")
MERGED_FILE = os.path.join(WORKSPACE, "The Last Shelter - All Episodes Merged.docx")

def download_file_rclone(item):
    filename = item['safe_filename']
    filepath = os.path.join(OUTPUT_DIR, filename)
    doc_id = item['doc_id']
    
    # Skip if already exists and size > 2000 bytes
    if os.path.exists(filepath) and os.path.getsize(filepath) > 2000:
        return {'status': 'SKIPPED', 'item': item, 'size': os.path.getsize(filepath)}
        
    cmd = ['rclone', 'backend', 'copyid', 'gdrive:', doc_id, filepath]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if res.returncode == 0 and os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            return {'status': 'OK', 'item': item, 'size': os.path.getsize(filepath)}
        else:
            err = res.stderr.strip() or res.stdout.strip()
            # Clean up empty file if created
            if os.path.exists(filepath) and os.path.getsize(filepath) == 0:
                os.remove(filepath)
            return {'status': 'FAIL', 'item': item, 'msg': err[:120]}
    except Exception as e:
        return {'status': 'FAIL', 'item': item, 'msg': str(e)}

def download_all(manifest):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    total = len(manifest)
    print(f"\n" + "="*70)
    print(f"      STARTING AUTOMATED DOWNLOAD: {total} GOOGLE DOCS VIA RCLONE")
    print(f"="*70)
    print(f"Target folder: {OUTPUT_DIR}\n")
    
    completed = 0
    errors = []
    
    # Use max_workers=3 to comfortably adhere to Google Drive rate limits
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(download_file_rclone, item): item for item in manifest}
        for future in as_completed(futures):
            completed += 1
            res = future.result()
            pct = (completed / total) * 100
            name = res['item']['safe_filename']
            st = res['status']
            
            if st == 'OK':
                kb = res['size'] / 1024
                print(f"[{completed:3d}/{total}] ({pct:5.1f}%) [OK] {name} ({kb:.1f} KB)", flush=True)
            elif st == 'SKIPPED':
                kb = res['size'] / 1024
                print(f"[{completed:3d}/{total}] ({pct:5.1f}%) [CACHED] {name} ({kb:.1f} KB)", flush=True)
            else:
                msg = res.get('msg', 'Error')
                print(f"[{completed:3d}/{total}] ({pct:5.1f}%) [FAIL] {name} -> {msg}", flush=True)
                errors.append((name, msg))
                
    print("\n" + "="*70)
    print(f"[DOWNLOAD COMPLETED] {completed - len(errors)}/{total} files downloaded successfully.")
    if errors:
        print(f"[RETRY NEEDED] {len(errors)} files failed:")
        for n, m in errors[:10]:
            print(f"  * {n}: {m}")
    print("="*70 + "\n")
    return len(errors) == 0

def sort_key_for_item(item):
    rev_ep = item.get('rev_ep', '')
    m = re.search(r'(\d+(?:\.\d+)?)', str(rev_ep))
    if m:
        return float(m.group(1))
    return 99999.0

def merge_all(manifest):
    print(f"[MERGE] Starting sequential merge into:")
    print(f"  -> '{MERGED_FILE}'\n")

    sorted_items = sorted(manifest, key=sort_key_for_item)
    master_doc = docx.Document()

    # Configure Heading 1 and Normal styles to Arial
    h1_style = master_doc.styles['Heading 1']
    h1_style.font.name = 'Arial'
    rPr_h1 = h1_style._element.get_or_add_rPr()
    rFonts_h1 = rPr_h1.get_or_add_rFonts()
    rFonts_h1.set(qn('w:ascii'), 'Arial')
    rFonts_h1.set(qn('w:hAnsi'), 'Arial')
    rFonts_h1.set(qn('w:cs'), 'Arial')

    normal_style = master_doc.styles['Normal']
    normal_style.font.name = 'Arial'
    rPr_normal = normal_style._element.get_or_add_rPr()
    rFonts_normal = rPr_normal.get_or_add_rFonts()
    rFonts_normal.set(qn('w:ascii'), 'Arial')
    rFonts_normal.set(qn('w:hAnsi'), 'Arial')
    rFonts_normal.set(qn('w:cs'), 'Arial')

    episodes_merged = 0
    total_words = 0

    for idx, item in enumerate(sorted_items, 1):
        filename = item['safe_filename']
        filepath = os.path.join(OUTPUT_DIR, filename)

        if not os.path.exists(filepath) or os.path.getsize(filepath) < 1000:
            continue

        try:
            sub_doc = docx.Document(filepath)
        except Exception as e:
            print(f"[ERROR READING] '{filename}': {e}")
            continue

        rev_ep = item['rev_ep']
        title = item['title']
        clean_heading = f"Ep {rev_ep} - {title}" if title else f"Ep {rev_ep}"

        p_head = master_doc.add_paragraph(clean_heading, style=h1_style)
        for r in p_head.runs:
            r.font.name = 'Arial'

        ep_words = 0
        for p in sub_doc.paragraphs:
            text = p.text.strip()
            if not text:
                continue
            # Skip duplicated headers in body
            if text.lower().startswith("ep ") or text.lower().startswith("episode "):
                continue

            new_p = master_doc.add_paragraph(text, style=normal_style)
            for r in new_p.runs:
                r.font.name = 'Arial'
            ep_words += len(text.split())

        master_doc.add_paragraph("", style=normal_style)
        episodes_merged += 1
        total_words += ep_words
        print(f"[{idx:3d}/{len(sorted_items)}] Merged: {clean_heading} ({ep_words} words)", flush=True)

    master_doc.save(MERGED_FILE)
    print("\n" + "="*70)
    print("                      MERGE COMPLETE!")
    print("="*70)
    print(f"Master File Saved: {MERGED_FILE}")
    print(f"Total Episodes Merged: {episodes_merged}/{len(sorted_items)}")
    print(f"Total Word Count: {total_words:,} words")
    print("Heading Style: Heading 1 (Arial)")
    print("Body Style:    Normal (Arial)")
    print("="*70 + "\n")

def main():
    with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    download_all(manifest)
    merge_all(manifest)

if __name__ == '__main__':
    main()
