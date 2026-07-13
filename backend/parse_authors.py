from bs4 import BeautifulSoup
import re

file_path = r"C:\Users\noelr\.gemini\antigravity-ide\brain\599f194b-d14c-4b84-a661-c587d7681c0a\.system_generated\steps\153\content.md"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # The file has some markdown headers, but we can just pass it to BS4
    soup = BeautifulSoup(content, 'html.parser')

    # Look for image captions, figcaptions, or portfolio titles
    # Confluence lit is a squarespace site, usually authors are in figcaption or image-title-wrapper
    elements = soup.select('.image-title-wrapper, figcaption, .summary-title, .portfolio-title, h1, h2, h3, h4, .sqs-block-html p')
    
    names = []
    for el in elements:
        text = el.get_text(strip=True)
        # Filter out random UI text and very long paragraphs
        if text and 3 < len(text) < 40:
            # We want things that look like names (Title Case, 2-3 words)
            if re.match(r'^[A-Z][A-Za-z\.\-\']+(?: [A-Z][A-Za-z\.\-\']+)*$', text):
                names.append(text)
            else:
                # Add everything just in case our regex is too strict
                names.append(f"[Maybe] {text}")
                
    # Remove duplicates while preserving order
    unique_names = list(dict.fromkeys(names))
    
    print(f"Found {len(unique_names)} potential names/titles.")
    for name in unique_names[:50]:
        print(name)

except Exception as e:
    print("Error:", e)
