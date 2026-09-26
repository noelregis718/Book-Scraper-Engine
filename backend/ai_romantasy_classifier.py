import pandas as pd
from transformers import pipeline

def classify_romantasy(file_path):
    print("Loading AI Model (Warning: This will redownload the model since the cache was cleared)...")
    classifier = pipeline("zero-shot-classification", model="typeform/distilbert-base-uncased-mnli")
    
    df = pd.read_excel(file_path)
    
    labels = ["Romance Drama", "Fantasy", "not romantasy"]
    
    for index, row in df.iterrows():
        # Enforce rule: fewer than 3 books is not romantasy
        if pd.notna(row.get('Number of Books')) and row.get('Number of Books') < 3:
            df.at[index, 'AI_Classification'] = "not romantasy"
            continue
            
        synopsis = str(row.get('Synopsis', ''))
        genres = str(row.get('Genres', ''))
        keywords = str(row.get('Keywords', ''))
        
        text_to_classify = f"{synopsis} {genres} {keywords}"
        
        if len(text_to_classify.strip()) > 5:
            result = classifier(text_to_classify, labels)
            df.at[index, 'AI_Classification'] = result['labels'][0]
        else:
            df.at[index, 'AI_Classification'] = "Unknown"
            
    output_path = file_path.replace('.xlsx', '_classified.xlsx')
    df.to_excel(output_path, index=False)
    print(f"Classification complete! Saved to {output_path}")

if __name__ == "__main__":
    # Update this with the target file
    target_file = "KF Literary Scouts Series .xlsx" 
    classify_romantasy(target_file)
