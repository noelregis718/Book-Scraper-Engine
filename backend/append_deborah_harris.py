import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def append_books():
    books_data = [
        {"Name of Series": "Love, Sivvy", "Author Name": "R. L. Toalson"},
        {"Name of Series": "The Distance From A to Z", "Author Name": "Natalie Blitt"},
        {"Name of Series": "Your Voice Is All I Hear", "Author Name": "Leah Scheier"},
        {"Name of Series": "The Judgement of Yoyo Gold", "Author Name": "Isaac Blum"},
        {"Name of Series": "Out of the Clear Blue Sky", "Author Name": "Isaac Blum"},
        {"Name of Series": "They Watch From Below", "Author Name": "Katya de Becerra"},
        {"Name of Series": "Real Time", "Author Name": "Pnina Kass"},
        {"Name of Series": "Rebel Daughter", "Author Name": "Lori Kaufmann"},
        {"Name of Series": "The Last Words We Said", "Author Name": "Leah Scheier"},
        {"Name of Series": "Claiming My Place", "Author Name": "Planaria Price & Helen West"},
        {"Name of Series": "Lydia, Queen of Palestine", "Author Name": "Uri Orlev"}
    ]

    out_file = r'E:\Internship\PocketFM\deborah_harris_merged.xlsx'
    
    if not os.path.exists(out_file):
        print(f"File not found: {out_file}")
        return

    print("Loading excel file...")
    df = pd.read_excel(out_file)

    new_df = pd.DataFrame(books_data)

    # Make sure we don't drop any of the 11 columns
    for col in df.columns:
        if col not in new_df.columns:
            new_df[col] = ""
            
    # keep the order
    new_df = new_df[df.columns]

    print("Appending new books...")
    df = pd.concat([df, new_df], ignore_index=True)

    df.to_excel(out_file, index=False)
    print(f"Added {len(books_data)} books successfully!")

    try:
        from style_books_authors import apply_styling
        apply_styling(out_file)
    except Exception as e:
        print(f"Failed to style: {e}")

if __name__ == "__main__":
    append_books()
