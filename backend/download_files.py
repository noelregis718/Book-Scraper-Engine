import os
import shutil
import gdown
import requests

def download_file(url, folder, file_name_hint=None):
    if "(same file as Batch 2" in url:
        return
    print(f"Downloading {url} to {folder}")
    if "drive.google.com" in url or "docs.google.com" in url:
        try:
            # try to extract id if present
            if "id=" in url:
                file_id = url.split("id=")[1].split("&")[0]
                url_to_use = f"https://drive.google.com/uc?id={file_id}"
                gdown.download(url_to_use, f"{folder}/{file_name_hint}.pdf" if "docs.google" in url else f"{folder}/{file_name_hint}", quiet=False)
            else:
                gdown.download(url, f"{folder}/{file_name_hint}", quiet=False)
        except Exception as e:
            print(f"Failed gdown: {e}")
    else:
        try:
            resp = requests.get(url)
            # Try to get filename from URL
            file_name = url.split('/')[-1]
            if file_name_hint and not file_name:
                file_name = file_name_hint
            with open(os.path.join(folder, file_name), 'wb') as f:
                f.write(resp.content)
            print(f"Downloaded {file_name}")
        except Exception as e:
            print(f"Failed requests: {e}")

def main():
    os.makedirs('batch 2', exist_ok=True)
    os.makedirs('batch 3', exist_ok=True)
    
    # Batch 2
    with open('table.tsv', 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 3:
                name = parts[0]
                url = parts[2]
                download_file(url, 'batch 2', name)

    # Batch 3
    with open('table (1).tsv', 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 3:
                name = parts[0]
                url = parts[2]
                download_file(url, 'batch 3', name)
                
if __name__ == "__main__":
    main()
