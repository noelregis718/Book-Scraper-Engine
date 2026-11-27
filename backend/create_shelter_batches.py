import os
import sys
import json
import re
import zipfile
import docx
from docx.oxml.ns import qn

WORKSPACE = r"E:\Internship\PocketFM"
MANIFEST_FILE = os.path.join(WORKSPACE, "shelter_episodes_manifest.json")
OUTPUT_DIR = os.path.join(WORKSPACE, "downloaded_shelter_episodes")

def sort_key_for_item(item):
    rev_ep = item.get('rev_ep', '')
    m = re.search(r'(\d+(?:\.\d+)?)', str(rev_ep))
    if m:
        return float(m.group(1))
    return 99999.0

def extract_title_and_clean_paragraphs(sub_doc, rev_ep, fallback_title):
    raw_paras = [p for p in sub_doc.paragraphs if p.text.strip()]
    if not raw_paras:
        title = fallback_title or ""
        return title, []

    first_text = raw_paras[0].text.strip()
    m = re.match(r'^(?:(?:corrected\s+)?ep(?:isode)?\s*\d+\s*[-:–—]\s*|\d+\s*[-:–—]\s*)(.+)$', first_text, re.IGNORECASE)
    if m:
        extracted_title = m.group(1).strip()
        body_paras = raw_paras[1:]
        if not fallback_title or fallback_title.lower().startswith("corrected ep"):
            title = extracted_title
        else:
            title = fallback_title
    else:
        m2 = re.match(r'^(?:(?:corrected\s+)?ep(?:isode)?\s*\d+)$', first_text, re.IGNORECASE)
        if m2:
            body_paras = raw_paras[1:]
            title = fallback_title if not fallback_title.lower().startswith("corrected ep") else ""
        else:
            body_paras = raw_paras
            title = fallback_title if not fallback_title.lower().startswith("corrected ep") else ""

    if title:
        m3 = re.match(r'^(?:(?:corrected\s+)?ep(?:isode)?\s*\d+\s*[-:–—]\s*|\d+\s*[-:–—]\s*)(.+)$', title, re.IGNORECASE)
        if m3:
            title = m3.group(1).strip()

    filtered_paras = []
    for p in body_paras:
        t = p.text.strip()
        if re.match(r'^(?:ep(?:isode)?\s*\d+|corrected\s+ep)', t, re.IGNORECASE) and len(t) < 80:
            continue
        filtered_paras.append(p)

    return title, filtered_paras

def build_batch_doc(items, output_filepath, batch_title):
    print(f"\nBuilding '{batch_title}' -> {os.path.basename(output_filepath)}")
    doc = docx.Document()

    h1_style = doc.styles['Heading 1']
    h1_style.font.name = 'Arial'
    rPr_h1 = h1_style._element.get_or_add_rPr()
    rFonts_h1 = rPr_h1.get_or_add_rFonts()
    rFonts_h1.set(qn('w:ascii'), 'Arial')
    rFonts_h1.set(qn('w:hAnsi'), 'Arial')
    rFonts_h1.set(qn('w:cs'), 'Arial')

    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Arial'
    rPr_normal = normal_style._element.get_or_add_rPr()
    rFonts_normal = rPr_normal.get_or_add_rFonts()
    rFonts_normal.set(qn('w:ascii'), 'Arial')
    rFonts_normal.set(qn('w:hAnsi'), 'Arial')
    rFonts_normal.set(qn('w:cs'), 'Arial')

    merged_count = 0
    total_words = 0

    for idx, item in enumerate(items, 1):
        filename = item['safe_filename']
        filepath = os.path.join(OUTPUT_DIR, filename)

        if not os.path.exists(filepath) or os.path.getsize(filepath) < 1000:
            print(f"  [{idx:3d}/{len(items)}] MISSING/CORRUPT: {filename}")
            continue

        try:
            sub_doc = docx.Document(filepath)
        except Exception as e:
            print(f"  [{idx:3d}/{len(items)}] ERROR: {filename}: {e}")
            continue

        rev_ep = item['rev_ep']
        fallback_title = item.get('title', '')
        clean_title, body_paras = extract_title_and_clean_paragraphs(sub_doc, rev_ep, fallback_title)

        clean_heading = f"Ep {rev_ep} - {clean_title}" if clean_title else f"Ep {rev_ep}"

        p_head = doc.add_paragraph(clean_heading, style=h1_style)
        for r in p_head.runs:
            r.font.name = 'Arial'

        ep_words = 0
        for p in body_paras:
            text = p.text.strip()
            if not text:
                continue

            new_p = doc.add_paragraph(text, style=normal_style)
            for r in new_p.runs:
                r.font.name = 'Arial'
            ep_words += len(text.split())

        doc.add_paragraph("", style=normal_style)
        merged_count += 1
        total_words += ep_words

    doc.save(output_filepath)
    print(f"  Done: {merged_count}/{len(items)} episodes merged ({total_words:,} words) -> {os.path.getsize(output_filepath):,} bytes")
    return merged_count, total_words

def main():
    with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    sorted_items = sorted(manifest, key=sort_key_for_item)
    total = len(sorted_items)
    print(f"Total episodes in manifest: {total}")

    batch1_items = sorted_items[:100]
    batch2_items = sorted_items[100:200]
    batch3_items = sorted_items[200:214]

    ep1_start = batch1_items[0]['rev_ep']
    ep1_end = batch1_items[-1]['rev_ep']
    ep2_start = batch2_items[0]['rev_ep']
    ep2_end = batch2_items[-1]['rev_ep']
    ep3_start = batch3_items[0]['rev_ep']
    ep3_end = batch3_items[-1]['rev_ep']

    b1_filename = f"The Last Shelter - Batch 1 (Ep {ep1_start} - Ep {ep1_end}, 100 Episodes).docx"
    b2_filename = f"The Last Shelter - Batch 2 (Ep {ep2_start} - Ep {ep2_end}, 100 Episodes).docx"
    b3_filename = f"The Last Shelter - Batch 3 (Ep {ep3_start} - Ep {ep3_end}, 14 Episodes).docx"

    b1_path = os.path.join(WORKSPACE, b1_filename)
    b2_path = os.path.join(WORKSPACE, b2_filename)
    b3_path = os.path.join(WORKSPACE, b3_filename)

    build_batch_doc(batch1_items, b1_path, "Batch 1 (100 Episodes)")
    build_batch_doc(batch2_items, b2_path, "Batch 2 (100 Episodes)")
    build_batch_doc(batch3_items, b3_path, "Batch 3 (14 Episodes)")

    # Zip the 3 batch docx files into the main folder
    zip_filename = "The Last Shelter - All Episodes in 3 Batches (100-100-14).zip"
    zip_path = os.path.join(WORKSPACE, zip_filename)

    print(f"\nCompressing 3 batches into zip archive: {zip_filename}")
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.write(b1_path, arcname=b1_filename)
        zf.write(b2_path, arcname=b2_filename)
        zf.write(b3_path, arcname=b3_filename)

    print(f"Zip created successfully: {os.path.getsize(zip_path):,} bytes")
    print(f"Archive contents:")
    with zipfile.ZipFile(zip_path, 'r') as zf:
        for info in zf.infolist():
            print(f"  - {info.filename}: {info.file_size:,} bytes")

if __name__ == '__main__':
    main()
