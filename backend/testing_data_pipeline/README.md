# Testing Data Genre Wise & SRT Processing Pipeline

This pipeline automates the extraction, formatting, multi-threaded SRT downloading, and tab refinement for PocketFM testing datasets (`RD_Drama` and `Werewolf_Data`).

## Pipeline Workflow

1. **`keep_only_two_tabs.py`**
   - Filters the master workbook down to only `RD_Drama` and `Werewolf_Data` tabs.
   - Cleans up empty trailing rows and excessive blank sheets.

2. **`format_testing_data.py` / `filter_and_format_srt_asset.py`**
   - Applies professional dark navy headers (`#1E293B`), zebra striping (`#FFFFFF` / `#F8FAFC`), and column formatting.
   - Filters rows requiring non-blank Asset Codes (Column AC) and valid SRT URLs.

3. **`download_all_srts.py`**
   - Multi-threaded parallel downloader (25 workers) with retry logic and browser user-agent spoofing.
   - Saves SRT files named by `{asset_code}.srt` into `Downloaded_SRTs/RD_Drama/` and `Downloaded_SRTs/Werewolf_Data/`.
   - Generates `Downloaded_SRTs/download_manifest.csv` logging download status and file sizes.

4. **`compress_srts.py`**
   - Compresses all downloaded `.srt` files and manifest into `Downloaded_SRTs.zip` using Deflate Level 9 compression.

5. **`refine_testing_data.py`**
   - Extracts the exact 842 matching rows for `RD_Drama` and 616 matching rows for `Werewolf_Data` corresponding to the downloaded SRTs.
   - Restricts columns strictly from **A to AC** (Column 1 `Date created` to Column 29 `Asset Code`), removing trailing script and video link columns.
   - Generates `RD_Drama_Refined` and `Werewolf_Data_Refined` tabs in `Testing_Data_Genre_Wise.xlsx` as well as the standalone `Testing_Data_Genre_Wise_Refined.xlsx`.

6. **`sample_rows.py`**
   - Diagnostic script to inspect sample rows and preview dialogue from locally downloaded SRT files.
