from curl_cffi import requests
from bs4 import BeautifulSoup

url = "https://www.kensingtonbooks.com/shop/product-category/fiction/fantasy-fiction/"

print(f"Testing curl_cffi on {url}...")
try:
    response = requests.get(
        url,
        impersonate="chrome124",
        timeout=15
    )
    print(f"Status Code: {response.status_code}")
    print(f"Final URL: {response.url}")
    print(f"Length of response text: {len(response.text)}")
    
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.string if soup.title else "No Title"
    print(f"Page Title: {title}")
    
    # Check for books/products
    products = soup.find_all("li", class_="product")
    if not products:
        products = soup.select(".product")
    print(f"Products found: {len(products)}")
    
    if products:
        for idx, p in enumerate(products[:5], 1):
            title_tag = p.find(["h2", "h3", "a", "div"], class_=lambda c: c and "title" in c.lower()) or p.find("h2") or p.find("h3")
            t_text = title_tag.get_text(strip=True) if title_tag else "No Title Tag"
            link = p.find("a")
            href = link["href"] if link and "href" in link.attrs else ""
            print(f"  {idx}. {t_text} -> {href}")
    else:
        # Check if Cloudflare challenge page
        if "Just a moment" in response.text or "Turnstile" in response.text or "cf-" in response.text:
            print("Detected Cloudflare Challenge page in response text.")
            print(response.text[:500])
        else:
            print("Response preview:")
            print(response.text[:500])

except Exception as e:
    print(f"curl_cffi Error: {e}")

