import os
import shutil
import re
import urllib.request
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import openpyxl

def sanitize_filename(name):
    # Remove invalid Windows filename characters
    clean = re.sub(r'[\\/*?:"<>|]', '_', str(name).strip())
    return clean if clean else "unknown"

def download_single_srt(item):
    """
    Downloads a single SRT file.
    item: dict with keys: 'tab', 'row', 'show_name', 'asset_code', 'srt_url', 'target_path'
    """
    url = item['srt_url']
    target_path = item['target_path']
    alt_path = item['alt_path']

    if not url.startswith('http'):
        return {**item, 'status': 'SKIPPED_NOT_URL', 'bytes': 0, 'error': f"Non-HTTP value: {url}"}

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
                # Save to specific genre folder
                with open(target_path, 'wb') as f:
                    f.write(data)
                # Also save to root folder
                with open(alt_path, 'wb') as f:
                    f.write(data)
                return {**item, 'status': 'SUCCESS', 'bytes': len(data), 'error': None}
        except Exception as e:
            if attempt == 2:
                return {**item, 'status': 'FAILED', 'bytes': 0, 'error': str(e)}

def main():
    excel_file = 'Testing_Data_Genre_Wise.xlsx'
    base_folder = 'Downloaded_SRTs'
    os.makedirs(base_folder, exist_ok=True)
    os.makedirs(os.path.join(base_folder, 'RD_Drama'), exist_ok=True)
    os.makedirs(os.path.join(base_folder, 'Werewolf_Data'), exist_ok=True)

    # Clean up test folder if it exists
    if os.path.exists('Downloaded_SRTs_Test'):
        shutil.rmtree('Downloaded_SRTs_Test', ignore_errors=True)

    print(f"Loading {excel_file} to gather download tasks...")
    wb = openpyxl.load_workbook(excel_file, data_only=True)

    tasks = []
    seen_assets = {}

    for sname in ['RD_Drama', 'Werewolf_Data']:
        ws = wb[sname]
        for r in range(2, ws.max_row + 1):
            show_name = str(ws.cell(row=r, column=6).value or '').strip()
            asset_code_raw = str(ws.cell(row=r, column=29).value or '').strip()
            srt_url = str(ws.cell(row=r, column=35).value or '').strip()

            if not asset_code_raw:
                continue

            asset_code = sanitize_filename(asset_code_raw)
            filename = f"{asset_code}.srt"

            genre_path = os.path.join(base_folder, sname, filename)
            root_path = os.path.join(base_folder, filename)

            tasks.append({
                'tab': sname,
                'row': r,
                'show_name': show_name,
                'asset_code': asset_code,
                'srt_url': srt_url,
                'target_path': genre_path,
                'alt_path': root_path
            })

    total_tasks = len(tasks)
    http_tasks = [t for t in tasks if t['srt_url'].startswith('http')]
    print(f"Total rows gathered: {total_tasks}")
    print(f"Downloadable HTTP tasks: {len(http_tasks)}")
    print(f"Starting parallel download with 25 concurrent threads...\n")

    results = []
    success_count = 0
    failed_count = 0
    skipped_count = 0

    with ThreadPoolExecutor(max_workers=25) as executor:
        future_to_task = {executor.submit(download_single_srt, t): t for t in tasks}

        for idx, future in enumerate(as_completed(future_to_task), 1):
            res = future.result()
            results.append(res)

            if res['status'] == 'SUCCESS':
                success_count += 1
            elif res['status'] == 'FAILED':
                failed_count += 1
            else:
                skipped_count += 1

            if idx % 150 == 0 or idx == total_tasks:
                print(f"  Progress: {idx}/{total_tasks} processed (Success: {success_count}, Skipped: {skipped_count}, Failed: {failed_count})...")

    # Save manifest CSV
    manifest_file = os.path.join(base_folder, 'download_manifest.csv')
    print(f"\nWriting manifest report to {manifest_file}...")
    with open(manifest_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Tab', 'Row', 'Show Name', 'Asset Code', 'Status', 'File Size (bytes)', 'SRT URL', 'File Path', 'Error'])
        for r in sorted(results, key=lambda x: (x['tab'], x['row'])):
            writer.writerow([
                r['tab'],
                r['row'],
                r['show_name'],
                r['asset_code'],
                r['status'],
                r['bytes'],
                r['srt_url'],
                r['target_path'],
                r['error'] or ''
            ])

    print("\n==================================================================")
    print("DOWNLOAD COMPLETE!")
    print(f"Total Rows Evaluated: {total_tasks}")
    print(f"Successfully Downloaded: {success_count}")
    print(f"Skipped (non-URL / filename text): {skipped_count}")
    print(f"Failed Downloads: {failed_count}")
    print(f"All files saved in: {os.path.abspath(base_folder)}")
    print("==================================================================\n")

if __name__ == '__main__':
    main()
