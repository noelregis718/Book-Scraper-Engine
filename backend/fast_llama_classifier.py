import pandas as pd
import json
import requests
import os
import concurrent.futures

# Ollama settings
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:1b" # Blazing fast 1B model to maximize speed
MAX_WORKERS = 1 # Reduced to 1 worker for maximum safety
SAVE_INTERVAL = 50 # Saves the Excel file every 50 rows so you don't lose data

EXCEL_FILE = r"E:\Internship\PocketFM\Amazon A-Z Crawl List.xlsx"
SHEET_NAME = "Sheet1"

TAXONOMY = [
    "Fantasy",
    "Romantasy",
    "Romance Drama"
]

import time

def query_ollama(prompt):
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.0
        }
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=300)
            if response.status_code == 200:
                data = response.json()
                try:
                    return json.loads(data['response'])
                except json.JSONDecodeError:
                    pass # Try again
            
            # If we get here, either status wasn't 200 or JSON failed to decode
            print(f"API Error: Status {response.status_code if 'response' in locals() else 'Unknown'} or JSON decode failed.")
            time.sleep(2) 
        except Exception as e:
            print(f"Connection/Timeout Error: {e}")
            time.sleep(2)
            
    return None

def build_prompt(row):
    taxonomy_str = ", ".join(f'"{t}"' for t in TAXONOMY)
    prompt = f"""CRITICAL INSTRUCTION: You are a STRICT classification bot.
    
You MUST classify the following book into exactly ONE of these taxonomy genres:
[{taxonomy_str}]

ABSOLUTE RULES:
1. YOU ARE STRICTLY FORBIDDEN FROM INVENTING NEW GENRES. 
2. If the book is a "Biography", "True Crime", "Mystery", or anything else not in the list, YOU MUST FORCE IT into one of the 3 allowed genres based on the closest thematic fit (e.g., choose 'Romance Drama' for True Crime or Biography).
3. If your "classified_genre" is not literally one of the 3 options, it will cause a critical system failure.
4. YOU MUST INCLUDE THE "reasoning" KEY. DO NOT OMIT IT.

EXAMPLE OUTPUT FORMAT:
{{
  "classified_genre": "Fantasy",
  "reasoning": "This book features magic and a fictional world, which perfectly aligns with the Fantasy genre."
}}

You must respond with ONLY a raw JSON object containing exactly these two keys:
"classified_genre": The exact string from the taxonomy list above. It MUST match exactly.
"reasoning": A powerful, highly accurate, and directly to-the-point explanation (1-2 sentences) of exactly why this book fits the chosen genre.

BOOK DATA:
Title: {row.get('Book Title', '')}
Series: {row.get('Series', '')} (Books in Series: {row.get('Books in Series', '')})
Author: {row.get('Author', '')}
Publisher: {row.get('Publisher', '')}
Categories: {row.get('Genre', '')} > {row.get('Sub-Genre', '')} > {row.get('Sub-Sub-Genre', '')}
Browse Category: {row.get('Browse Category', '')}
Amazon Rating: {row.get('Star Rating', '')} stars from {row.get('Ratings Count', '')} reviews
ASIN/URL: {row.get('ASIN', '')} - {row.get('Amazon URL', '')}
Description: {str(row.get('Product Description', ''))[:1500]}
"""
    return prompt

def process_row(idx, row):
    print(f"Processing row {idx + 1}: {row.get('Book Title')}...")
    prompt = build_prompt(row)
    
    max_attempts = 3
    for attempt in range(max_attempts):
        res = query_ollama(prompt)
        
        if res:
            genre = res.get("classified_genre", "Error")
            # Python Validation: Physically block any genre that isn't in our taxonomy
            if genre not in TAXONOMY:
                if attempt < max_attempts - 1:
                    continue # Ask the AI again immediately!
                return idx, "Error", f"AI hallucinated invalid genre: {genre}"
                
            reasoning = str(res.get("reasoning", "")).strip()
            if not reasoning:
                if attempt < max_attempts - 1:
                    continue # Ask the AI again immediately!
                return idx, "Error", "AI failed to provide reasoning"
                
            return idx, genre, reasoning
            
    return idx, "Error", "Ollama API Failure"

def main():
    print(f"Loading {EXCEL_FILE}...")
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
    except Exception as e:
        print(f"Failed to load excel: {e}")
        return

    # Prepare columns
    if "Detailed Genre (AI)" not in df.columns:
        df["Detailed Genre (AI)"] = ""
    if "AI Reasoning" not in df.columns:
        df["AI Reasoning"] = ""

    # Find rows to process
    rows_to_process = []
    
    # --- ORIGINAL AUTOMATED LOGIC ---
    for idx, row in df.iterrows():
        # Only process if it hasn't been assigned a valid genre yet, or if it errored out previously
        genre_val = str(row.get("Detailed Genre (AI)", "")).strip()
        # This line guarantees that ANY row marked as 'Error' will be picked up and tried again!
        if pd.isna(row.get("Detailed Genre (AI)")) or genre_val == "" or genre_val == "Error":
            rows_to_process.append((idx, row))
            
    print(f"Found {len(rows_to_process)} rows remaining (including Errored rows) to process.")
    
    # Process ALL remaining rows in one massive batch!
    # print(f"Executing massive batch run for all {len(rows_to_process)} rows using Llama 3.2...")
    
    rows_to_process = rows_to_process[:500]
    print(f"Limiting to first {len(rows_to_process)} rows for Llama 3.2 test...")
    
    processed_count = 0
    success_count = 0
    error_count = 0
    
    # Process concurrently!
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_row, idx, row): idx for idx, row in rows_to_process}
        
        for future in concurrent.futures.as_completed(futures):
            idx, genre, reasoning = future.result()
            
            # Grab the title for the print log
            title = str(df.at[idx, 'Book Title'])
            
            df.at[idx, "Detailed Genre (AI)"] = genre
            df.at[idx, "AI Reasoning"] = reasoning
            
            if genre == "Error":
                print(f"[ERROR] '{title}' -> FAILED: {reasoning}")
                error_count += 1
            else:
                print(f"[SUCCESS] '{title}' -> {genre}")
                success_count += 1
                
            processed_count += 1
            if processed_count % SAVE_INTERVAL == 0:
                print(f"--- Processed {processed_count} rows. Saving checkpoint... ---")
                try:
                    df.to_excel(EXCEL_FILE, index=False)
                except Exception as e:
                    print(f"Could not save checkpoint: {e}")
                
    # Final save
    print("Saving final results...")
    try:
        df.to_excel(EXCEL_FILE, index=False)
        print("\n--- FINAL EXECUTION SUMMARY ---")
        print(f"Total Rows Processed: {processed_count}")
        print(f"Successfully Classified: {success_count}")
        print(f"Failed / Errored: {error_count}")
        print("-------------------------------")
        print("ALL DONE!")
    except Exception as e:
        print(f"Failed to save final results: {e}")

if __name__ == "__main__":
    main()
