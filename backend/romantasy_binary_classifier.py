import pandas as pd
import json
import requests
import concurrent.futures
import time

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:1b"

INPUT_FILE = r"E:\Internship\PocketFM\Merged_Romantasy_Master.xlsx"

TAXONOMY = {
    "Romantasy": "Features a prominent blend of romance and fantasy (magic, paranormal, shifters, vampires, fae).",
    "Not Romantasy": "Purely contemporary romance, or pure sci-fi/fantasy with no romance focus."
}

def build_prompt(row):
    taxonomy_str = json.dumps(TAXONOMY, indent=2)
    
    # Dynamically extract all relevant non-null metadata for this book
    book_data = []
    relevant_cols = [
        'Book Title', 'Series Name', 'Author Name', 'Genre', 'Sub-Genre', 
        'Genre Tags', 'Logline', 'Synopsis', 'Keyword', 'Publisher',
        'Book1_Rating', 'Amazon Book1_Rating', 'Goodreads Rating Book 1'
    ]
    
    for col in relevant_cols:
        val = row.get(col)
        if pd.notna(val) and str(val).strip() != "":
            book_data.append(f"{col}: {str(val).strip()}")
            
    book_data_str = "\n".join(book_data)
    
    prompt = f"""You are an expert literary genre classifier specializing in the 'Romantasy' genre.

Your task is to classify the following book/series strictly into one of the following genres:
{taxonomy_str}

ABSOLUTE RULES:
1. YOU ARE STRICTLY FORBIDDEN FROM INVENTING NEW GENRES. You must output exactly "Romantasy" or "Not Romantasy".
2. If the book features a prominent blend of Romance AND Fantasy (magic, supernatural, paranormal, shifters, vampires, fae, high fantasy worlds), choose "Romantasy".
3. If the book is purely contemporary romance, or purely hard sci-fi/fantasy without a romance focus, choose "Not Romantasy".
4. YOU MUST INCLUDE THE "reasoning" KEY. DO NOT OMIT IT.
5. The reasoning MUST be a highly detailed 2-3 sentence explanation.
6. YOU MUST NOT simply repeat or copy-paste the Book Data back to me. You must WRITE AN ORIGINAL SENTENCE explaining your logic.
7. You MUST explicitly name the Series Name and Author in your reasoning.
8. You MUST mention the specific Sub-Genre and how the data points support your choice.
9. CRITICAL LOGIC CHECK: Your reasoning MUST perfectly match your chosen genre. If you choose 'Romantasy', you must explain why it has BOTH Romance and Fantasy. If you choose 'Not Romantasy', you must explain why it lacks one or both.
10. You MUST end your reasoning with the exact concluding phrase: "Therefore, this is [Your Chosen Genre]."

EXAMPLE OF CORRECT OUTPUT:
{{
  "classified_genre": "Not Romantasy",
  "reasoning": "The 'Alien Horizons' series by Jane Doe is classified as Hard Sci-Fi because there is no mention of romance in the sub-genre or synopsis. The focus is entirely on Commander Shepard's space exploration. Therefore, this is Not Romantasy."
}}

You must respond with ONLY a raw JSON object containing exactly these two keys:
"classified_genre": The exact string "Romantasy" or "Not Romantasy".
"reasoning": A detailed 2-3 sentence explanation specifically naming the series, author, and sub-genre to justify the classification.

BOOK DATA:
{book_data_str}
"""
    return prompt

def classify_row(idx, row):
    prompt = build_prompt(row)
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    
    max_retries = 5
    for attempt in range(max_retries):
        try:
            # Increased timeout to 60s to handle the larger prompt sizes
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            result_json = data.get("response", "{}")
            result = json.loads(result_json)
            
            genre = str(result.get("classified_genre", "")).strip()
            reasoning = str(result.get("reasoning", "")).strip()
            
            # STRICT VALIDATION: Must have valid genre AND detailed reasoning
            if genre not in TAXONOMY or not reasoning or len(reasoning.split()) < 15 or reasoning == "No reasoning provided.":
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue # Retry on hallucination or missing/short reasoning
                return idx, "Error", f"Invalid output (Genre: {genre}, Reasoning Length: {len(reasoning.split())} words)"
                
            # SYNC VALIDATION: The reasoning must logically support the genre by ending with the required phrase
            sync_phrase = f"Therefore, this is {genre}"
            if sync_phrase.lower() not in reasoning.lower():
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue # Retry because reasoning didn't sync with genre
                return idx, "Error", f"Reasoning out of sync. Genre was '{genre}' but reasoning was: {reasoning}"
                
            return idx, genre, reasoning
            
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2) # Wait 2 seconds before retrying
                continue # Retry on timeout/error
            return idx, "Error", f"API Call Failed after {max_retries} attempts: {str(e)}"

def main():
    print(f"Loading {INPUT_FILE}...")
    df = pd.read_excel(INPUT_FILE)
    
    if "Detailed Genre (AI)" not in df.columns:
        df["Detailed Genre (AI)"] = ""
    if "AI Reasoning" not in df.columns:
        df["AI Reasoning"] = ""

    df["Detailed Genre (AI)"] = df["Detailed Genre (AI)"].astype(object)
    df["AI Reasoning"] = df["AI Reasoning"].astype(object)

    rows_to_process = []
    
    for idx, row in df.iterrows():
        genre_val = str(row.get("Detailed Genre (AI)", "")).strip()
        reason_val = str(row.get("AI Reasoning", "")).strip()
        
        # Only process if missing or invalid
        if genre_val not in TAXONOMY or pd.isna(row.get("AI Reasoning")) or reason_val == "" or reason_val == "nan":
            rows_to_process.append((idx, row))
            
    print(f"Found {len(rows_to_process)} rows that need processing.")
    
    rows_to_process = rows_to_process[:10]
    print(f"Limiting to first {len(rows_to_process)} rows for testing...")
    
    if len(rows_to_process) == 0:
        print("Everything is perfect! Nothing to do.")
        return
        
    print("Starting classification with 4 workers...")
    
    success_count = 0
    error_count = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(classify_row, item[0], item[1]): item for item in rows_to_process}
        
        for future in concurrent.futures.as_completed(futures):
            idx, genre, reasoning = future.result()
            
            title = df.at[idx, 'Book Title'] if pd.notna(df.at[idx, 'Book Title']) else df.at[idx, 'Series Name']
            
            if genre == "Error":
                print(f"[ERROR] '{title}' -> Failed: {reasoning}")
                error_count += 1
            else:
                print(f"[SUCCESS] '{title}' -> {genre}")
                df.at[idx, "Detailed Genre (AI)"] = genre
                df.at[idx, "AI Reasoning"] = reasoning
                success_count += 1
                
    print("Saving final results...")
    try:
        df.to_excel(INPUT_FILE, index=False)
        print("\n--- FINAL EXECUTION SUMMARY ---")
        print(f"Total Rows Processed: {len(rows_to_process)}")
        print(f"Successfully Classified: {success_count}")
        print(f"Failed / Errored: {error_count}")
        print("ALL DONE!")
    except Exception as e:
        print(f"Failed to save final results: {e}")

if __name__ == "__main__":
    main()
