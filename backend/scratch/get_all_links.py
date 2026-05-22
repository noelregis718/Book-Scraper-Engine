import re

def get_links():
    with open("lima_authors.html", "r", encoding="utf-8") as f:
        content = f.read()
    
    links = re.findall(r'href=[\"\'](.*?)[\"\']', content)
    data_urls = re.findall(r'data-url=[\"\'](.*?)[\"\']', content)
    
    all_links = set(links) | set(data_urls)
    
    print("Found Links/URLs:")
    for link in sorted(all_links):
        if link.startswith("/") or "limaagency" in link:
            print(link)

if __name__ == "__main__":
    get_links()
