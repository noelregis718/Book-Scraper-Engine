import re

html_path = r"E:\Internship\PocketFM\Authors - Kensington Publishing.html"

with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Let's use the exact pattern from parse_kensington_local.py
link_pattern = re.compile(r'<a\s+[^>]*href=["\']([^"\']*(?:/author/|/authors/)[^"\']*)["\'][^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL)
matches = link_pattern.findall(content)

author_names = []
blacklist = ["author", "authors", "home", "books", "contact", "about", "submission", "faq", "terms", "privacy", "help", "search"]

print(f"Total matches found: {len(matches)}")
valid_count = 0
for href, text in matches:
    clean_text = re.sub(r'<[^>]+>', '', text).strip()
    clean_text = " ".join(clean_text.split())
    if clean_text and len(clean_text) > 2 and len(clean_text) < 50:
        text_lower = clean_text.lower()
        if not any(b_item in text_lower for b_item in blacklist):
            if clean_text not in author_names:
                author_names.append(clean_text)
                valid_count += 1
                if valid_count <= 20:
                    print(f"{valid_count}. Author: '{clean_text}' -> Link: '{href.strip()}'")
