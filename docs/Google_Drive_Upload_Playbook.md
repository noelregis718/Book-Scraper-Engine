# Google Drive Bulk Upload & Link Extraction Playbook

This document outlines the automated process we use to bulk upload hundreds of documents to the company Google Drive and extract their shareable links straight back into the main tracker spreadsheet.

## 🚀 The Core Philosophy
Instead of dealing with complex Google Cloud Console setups, API limitations, and OAuth tokens, this process utilizes **Browser Automation (Selenium/Playwright)** hooked directly into a persistent browser profile.

This essentially creates a "ghost assistant" that takes control of your browser, already logged into your company Google Drive, and manually drags-and-drops files just like a human would—but at lightning speed.

---

## 🛠️ How It Works (Step-by-Step)

### 1. The Persistent Browser Profile
When the Python upload script (e.g., `backend/upload_and_link.py`) is first executed, it spawns a browser attached to a specific local cache directory (like `browser_profile_main`). 
- **Why this matters:** Because it uses this profile, any cookies and active logins are saved permanently. You only have to log into your company Google ID *once*. On all future runs, the script bypasses login screens entirely and goes straight to the Drive.

### 2. The Bulk Upload Sequence
Once authenticated, the script navigates to the target Google Drive folder URL. 
- It scans the local payload directory (e.g., `Final_212_Completed_Payload`).
- It iterates through every single file and folder.
- It injects the files directly into the Google Drive DOM (simulating a drag-and-drop file upload).
- The script actively monitors the Google Drive UI upload progress bar, waiting patiently for the exact moment the "Upload Complete" toast notification appears.

### 3. Extracting the Links
Once the upload finishes, the script does not stop. 
- It clicks on the newly uploaded file in the Drive interface.
- It triggers the "Share" menu.
- It grabs the secure, shareable URL directly from the clipboard/UI.
- It repeats this for all 200+ files instantly.

### 4. Excel Injection
Simultaneously, the script holds your tracker (e.g., `Episode Metrics - Noel New.xlsx`) in memory via the `pandas` library.
- It takes the extracted Google Drive link.
- It searches the Excel sheet for the exact matching "Show / Title".
- It drops the link securely into the "Show Link" or "Revenue Statement Drive Link" column.
- It saves the Excel file.

---

## ⚙️ Running the Process Again

If you ever receive another massive batch of 500+ files to process:
1. Ensure your local files are grouped in a single folder.
2. Run the specific upload script located in the `backend/` folder.
3. Watch as the browser opens automatically, uploads everything to your company drive, and seamlessly populates your metrics spreadsheet without you ever having to copy and paste a single link.
