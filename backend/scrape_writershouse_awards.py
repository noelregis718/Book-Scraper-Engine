import os
import sys
import pandas as pd
import bs4

def create_11_col_writers_house():
    local_path = r"C:\Users\noelr\.gemini\antigravity-ide\brain\9a042720-9091-4bfb-9deb-cb6334b8be99\.system_generated\steps\803\content.md"
    print(f"Reading from local cache: {local_path}")
    with open(local_path, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = bs4.BeautifulSoup(html, 'html.parser')
    
    data = []
    
    # 1. Parse Image Features
    for img in soup.select('.image-wrapper img'):
        alt_text = img.get('alt', '').strip()
        
        # Heuristic split: "Title - Author"
        title, author = "", ""
        if " - " in alt_text:
            parts = alt_text.rsplit(" - ", 1)
            title = parts[0].strip()
            author = parts[1].strip()
        elif alt_text:
            title = alt_text
            
        data.append({
            'Name of Series': title, 
            'Author Name': author, 
            'Publisher': '', 
            'GoodReads series link': '', 
            'Number of PRIMARY books in the series': '', 
            'Rating (out of 5) of Primary Book 1': '', 
            'Ratings (#) of Primary Book 1': '', 
            'Synopsis (if available)': f"FEATURED COVER: {alt_text}", 
            'Romantasy = Yes or No?': '', 
            'Romantasy Sub-Genre of series': '', 
            'Name of agent': 'Writers House'
        })

    # 2. Parse Text Lists
    for col in soup.select('.column-wrapper'):
        current_award = "Unknown"
        for child in col.children:
            if child.name == 'p' and child.strong:
                current_award = child.strong.text.strip()
            elif child.name == 'ul':
                for li in child.find_all('li'):
                    raw_text = li.get_text(strip=True)
                    author, title = "", ""
                    
                    if li.strong:
                        author = li.strong.get_text(strip=True).replace(',', '').strip()
                    if li.em:
                        title = li.em.get_text(strip=True).strip()
                    if not title and not author:
                        if "," in raw_text:
                            parts = raw_text.split(',', 1)
                            author = parts[0].strip()
                            title = parts[1].strip()
                            
                    data.append({
                        'Name of Series': title, 
                        'Author Name': author, 
                        'Publisher': '', 
                        'GoodReads series link': '', 
                        'Number of PRIMARY books in the series': '', 
                        'Rating (out of 5) of Primary Book 1': '', 
                        'Ratings (#) of Primary Book 1': '', 
                        'Synopsis (if available)': f"AWARD: {current_award} | {raw_text}", 
                        'Romantasy = Yes or No?': '', 
                        'Romantasy Sub-Genre of series': '', 
                        'Name of agent': 'Writers House'
                    })

    df = pd.DataFrame(data, columns=[
        'Name of Series', 'Author Name', 'Publisher', 'GoodReads series link', 
        'Number of PRIMARY books in the series', 'Rating (out of 5) of Primary Book 1', 
        'Ratings (#) of Primary Book 1', 'Synopsis (if available)', 
        'Romantasy = Yes or No?', 'Romantasy Sub-Genre of series', 'Name of agent'
    ])
    
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Writers_House_Adult_Awards.xlsx")
    out_path = os.path.abspath(out_path)
    
    print(f"Exporting 11-column format to {out_path}...")
    df.to_excel(out_path, index=False)
    
    sys.path.append(os.getcwd())
    try:
        from apply_jra_style import apply_styling
        apply_styling(out_path)
        print("Premium styling applied.")
    except Exception as e:
        print(f"Styling warning: {e}")
        
    print("ALL DONE!")

if __name__ == "__main__":
    create_11_col_writers_house()
