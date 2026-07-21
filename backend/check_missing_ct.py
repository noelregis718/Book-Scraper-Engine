import pandas as pd

def main():
    print("Loading Base List...")
    base_df = pd.read_excel('e:/Internship/PocketFM/Podium CT Wishlist (Tier 1).xlsx', sheet_name='Shortlisted for Tier 1 Selectio', engine='openpyxl')
    
    # Normalize titles for matching
    base_titles = set(base_df['Book Title'].dropna().astype(str).str.strip().str.lower())
    print(f"Found {len(base_titles)} unique titles in the Base List.")

    print("Loading Complete Catalogue...")
    catalog_df = pd.read_excel('e:/Internship/PocketFM/Podium Entertainment Complete Catalogue.xlsx', engine='openpyxl')

    # Identify CT genres (Mystery & Thriller, Horror)
    def is_ct(genre_str):
        if pd.isna(genre_str):
            return False
        g = str(genre_str).lower()
        return 'mystery & thriller' in g or 'horror' in g

    # Filter for relevant CT genres
    print("Filtering catalog for CT genres...")
    ct_catalog_df = catalog_df[catalog_df['Genre'].apply(is_ct)]
    
    # Find titles in CT catalog that are missing from base list
    missing_df = ct_catalog_df[~ct_catalog_df['Title'].astype(str).str.strip().str.lower().isin(base_titles)]

    output_path = 'e:/Internship/PocketFM/Missing_CT_From_Base_List.xlsx'
    print(f"Saving missing items to {output_path}...")
    missing_df.to_excel(output_path, index=False)

    print("\n--- Summary ---")
    print(f"Total CT items in Complete Catalogue: {len(ct_catalog_df)}")
    print(f"Items missing from Base List: {len(missing_df)}")
    print(f"Saved missing items to: {output_path}")

if __name__ == "__main__":
    main()
