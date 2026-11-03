import urllib.request
import ssl
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    "https://www.kensingtonbooks.com/shop/product-category/fiction/fantasy-fiction/",
    "https://www.kensingtonbooks.com/shop/product-category/fiction/fantasy-fiction/feed/",
    "https://www.kensingtonbooks.com/wp-json/wc/store/v1/products?category=fantasy-fiction",
    "https://www.kensingtonbooks.com/wp-json/wp/v2/product_cat?search=fantasy",
    "https://www.kensingtonbooks.com/product-sitemap.xml",
    "https://www.kensingtonbooks.com/robots.txt"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9"
}

for u in urls:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            content_type = resp.headers.get('Content-Type', '')
            status = resp.status
            body_start = resp.read(300).decode('utf-8', errors='ignore')
            print(f"[{status}] {u}")
            print(f"   Content-Type: {content_type}")
            print(f"   Body snippet: {body_start[:120].strip()}...\n")
    except urllib.error.HTTPError as e:
        print(f"[HTTP {e.code}] {u} - {e.reason}")
    except Exception as e:
        print(f"[ERR] {u} - {e}")

