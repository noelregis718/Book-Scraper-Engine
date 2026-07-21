import pandas as pd

def main():
    file_path = 'e:/Internship/PocketFM/Podium CT Wishlist (Tier 1).xlsx'
    print(f"Loading {file_path} (Sheet3)...")
    df = pd.read_excel(file_path, sheet_name='Sheet3', engine='openpyxl')
    
    initial_count = len(df)
    print(f"Initial series count: {initial_count}")
    
    # Filter 1: Pure Romantasy Filter
    # Instruction: "Filter out for romantasy based titles (No overlap between any other genre)"
    def is_pure_romantasy(genre):
        if pd.isna(genre):
            return False
        g = str(genre).lower()
        has_rom_fan = 'romance' in g or 'fantasy' in g
        has_other = 'mystery' in g or 'thriller' in g or 'horror' in g or 'sci-fi' in g
        # If it has romance/fantasy but NO CT genres, it's pure romantasy. We want to filter these OUT.
        return has_rom_fan and not has_other
        
    df = df[~df['Genre'].apply(is_pure_romantasy)]
    after_romantasy = len(df)
    print(f"Count after Romantasy filter (No overlap): {after_romantasy}")
    
    # Filter 2: No. of Primary Books > 4
    df['No. of Primary Books Numeric'] = pd.to_numeric(df['No. of Primary Books'], errors='coerce').fillna(0)
    df = df[df['No. of Primary Books Numeric'] > 4]
    after_books = len(df)
    print(f"Count after Books > 4 filter: {after_books}")
    
    # Filter 3: No. of Hours > 40
    df['No. of Hours Numeric'] = pd.to_numeric(df['No. of Hours'], errors='coerce').fillna(0)
    df = df[df['No. of Hours Numeric'] > 40]
    after_hours = len(df)
    print(f"Count after Hours > 40 filter: {after_hours}")
    
    # Clean up temporary columns
    df = df.drop(columns=['No. of Primary Books Numeric', 'No. of Hours Numeric'])
    
    # Save the filtered results
    out_path = 'e:/Internship/PocketFM/Filtered_Final_Shortlist.xlsx'
    df.to_excel(out_path, index=False)
    print(f"\nSuccessfully saved finalized {after_hours} series to {out_path}")

if __name__ == '__main__':
    main()
