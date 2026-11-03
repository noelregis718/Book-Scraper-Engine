import urllib.request
import json
import urllib.parse

def test_all_kensington_queries():
    queries = [
        {"publisher": "kensington", "subject": "fantasy"},
        {"publisher": "kensington", "subject": "fantasy fiction"},
        {"publisher": "kensington", "subject": "paranormal romance"},
        {"publisher": "kensington publishing", "subject": "fantasy"},
        {"publisher": "rebel base", "subject": "fantasy"},
        {"publisher": "kensington", "q": "fantasy romance"}
    ]
    
    unique_books = {}
    
    for q_params in queries:
        encoded = urllib.parse.urlencode(q_params)
        url = f"https://openlibrary.org/search.json?{encoded}&limit=100"
        print(f"Fetching: {url}")
        req = urllib.request.Request(url, headers={"User-Agent": "PocketFM-Kensington-Catalog/1.0"})
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                docs = data.get("docs", [])
                print(f"  -> Found {len(docs)} books (Total available: {data.get('numFound')})")
                for d in docs:
                    title = d.get("title", "").strip()
                    authors = d.get("author_name", [])
                    author = authors[0] if authors else "N/A"
                    key = (title.lower(), author.lower())
                    if key not in unique_books and title:
                        unique_books[key] = {
                            "title": title,
                            "author": author,
                            "publisher": "Kensington",
                            "year": d.get("first_publish_year", "N/A"),
                            "isbn": d.get("isbn", [""])[0] if d.get("isbn") else "N/A"
                        }
        except Exception as e:
            print(f"  -> Error: {e}")
            
    print(f"\n==================================================")
    print(f"TOTAL UNIQUE KENSINGTON FANTASY BOOKS: {len(unique_books)}")
    print(f"==================================================")
    
    # Show first 20 books
    for idx, (k, b) in enumerate(list(unique_books.items())[:20], 1):
        print(f"{idx}. '{b['title']}' by {b['author']} ({b['year']})")

if __name__ == "__main__":
    test_all_kensington_queries()
