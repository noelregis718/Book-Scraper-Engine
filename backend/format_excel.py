import pandas as pd
import sys

def main():
    file_path = 'books_authors.xlsx'
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        sys.exit(1)

    requested_columns = [
        "Name of Series",
        "Author Name",
        "Publisher",
        "GoodReads series link",
        "Number of PRIMARY books in the series",
        "Rating (out of 5) of Primary Book 1",
        "Ratings (#) of Primary Book 1",
        "Synopsis (if available)",
        "Romantasy = Yes or No?",
        "Romantasy Sub-Genre of series",
        "Name of agent"
    ]

    new_columns = []
    
    # We will build the new column order.
    # Put 'Book Title' right after 'Author Name' to preserve it logically
    for col in requested_columns:
        new_columns.append(col)
        if col == "Author Name":
            if "Book Title" in df.columns:
                new_columns.append("Book Title")

    # Add any other existing columns that aren't already included
    for col in df.columns:
        if col not in new_columns:
            new_columns.append(col)

    # For any new column, initialize it with empty string
    for col in new_columns:
        if col not in df.columns:
            df[col] = ""

    # Reorder
    df = df[new_columns]

    # Save
    try:
        df.to_excel(file_path, index=False)
        print("Successfully formatted the excel file!")
    except Exception as e:
        print(f"Error saving {file_path}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
