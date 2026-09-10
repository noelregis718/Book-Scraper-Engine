# Romantasy AI Classification Pipeline: Complete Process Documentation

This document outlines the end-to-end process built to aggregate romantasy data and pass it through a strictly validated, local AI classification pipeline using Ollama.

## Phase 1: Data Aggregation & Cleansing

The goal of this phase was to extract specific, pre-filtered rows from massive, multi-tab Excel files and merge them perfectly into a single master sheet, bypassing Excel's hidden-row visual filters.

### 1. Target Data Sources
We identified three specific tabs across two different Excel files that had active visual filters:
1. **File 1:** `Romantasy New Keywords Scraping.xlsx`
   - Tab A: `Series only - Priority Keywords`
   - Tab B: `Cut 1 Unique Series of 12.3k Ti`
2. **File 2:** `All-Genre Licensing Tracker.xlsx`
   - Tab C: `Romantasy v2`

### 2. The Extraction Logic (`merge_filtered_sheets.py`)
Standard Python tools (`pandas`) completely ignore visual Excel filters and extract all hidden data. To bypass this, we utilized `openpyxl`:
- The script loaded the workbooks with `data_only=True` to ensure it extracted the final calculated values, completely eliminating any `#REF!` or `#NAME?` errors caused by severed formula links.
- It iterated over every single row and explicitly checked the `.hidden` attribute of the row dimensions. If a row was hidden by the user's Excel filter, the script skipped it.

### 3. Dynamic Header Alignment
Tab C (`Romantasy v2`) contained internal notes ("Vanshika V", "Molly to fill") in Row 1, pushing the actual headers to Row 2. The script was programmed to dynamically scan rows until it found recognizable column names (like `Title` or `Book Title`), standardizing them so that the datasets aligned perfectly. 

### 4. Final Output
The extracted rows (73 + 293 + 57 = 423 total rows) were vertically stacked into a new master sheet: `Merged_Romantasy_Master.xlsx`. The original files were stripped of their unnecessary tabs to maintain a clean workspace.

---

## Phase 2: AI Classification Pipeline

The goal of this phase was to feed the aggregated metadata into a local instance of `llama3.2:1b` to classify each book as **Romantasy** or **Not Romantasy**, alongside a highly detailed reasoning paragraph.

### 1. Dynamic Data Injection
Instead of hardcoding a few columns, the script (`romantasy_binary_classifier.py`) iterates through the 423 rows and dynamically extracts data from 13 high-value metadata columns:
`Book Title`, `Series Name`, `Author Name`, `Genre`, `Sub-Genre`, `Genre Tags`, `Logline`, `Synopsis`, `Keyword`, `Publisher`, `Book1_Rating`, `Amazon Book1_Rating`, and `Goodreads Rating Book 1`.

Internal tracking columns (like `Tier`, `MG`) are intentionally excluded to prevent confusing the 1 Billion parameter model.

### 2. The System Prompt
The prompt forces the AI into a highly restrictive JSON format. 

```text
You are an expert literary genre classifier specializing in the 'Romantasy' genre.

Your task is to classify the following book/series strictly into one of the following genres:
{{
  "Romantasy": "Features a prominent blend of romance and fantasy (magic, paranormal, shifters, vampires, fae).",
  "Not Romantasy": "Purely contemporary romance, or pure sci-fi/fantasy with no romance focus."
}}

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
[DYNAMIC DATA INJECTED HERE]
```

### 3. Strict Python Validation & Synchronization Checks
Because small LLMs are prone to "hallucinating" or providing out-of-sync reasoning (e.g., classifying a book as Romantasy but writing reasoning that says it is Sci-Fi), the Python script strictly validates the AI's JSON output before it is allowed to save:

1. **Genre Check:** The `classified_genre` MUST exactly match the strings `Romantasy` or `Not Romantasy`.
2. **Length Check:** The `reasoning` string MUST be longer than 15 words.
3. **Synchronization Check (Anti-Hallucination):** The Python script physically scans the reasoning string to guarantee that it ends with `Therefore, this is [Genre]`. If the reasoning conclusion contradicts the chosen genre, it is instantly rejected.

### 4. Automatic Retry Mechanism
If the AI times out (due to heavy local processing loads), hallucinates a genre, copies the input data, or fails the Synchronization Check, the script does not crash or skip the row. 

Instead, it triggers a `time.sleep()` to give the local Ollama instance a moment to breathe, and automatically retries the prompt up to **5 times**. If it fails 5 times, it explicitly records an Error rather than writing bad data to the master sheet.
