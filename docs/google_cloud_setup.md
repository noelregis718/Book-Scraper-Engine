# Google Cloud Setup Guide for PocketFM Automations

This guide explains how to create a Google Cloud Service Account. This is required so our Python script can securely run in the background 24/7 and automatically read/write email drafts to the PocketFM Google Sheet without any human interaction.

## Step 1: Create the Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and make sure you are logged in with your **PocketFM email address**.
2. Click the project dropdown at the very top left (next to the Google Cloud logo), and click **New Project**.
3. Name the project `PocketFM-Automations` and click **Create**.
4. Wait a few seconds, then click the dropdown again and make sure `PocketFM-Automations` is selected as your active project.

## Step 2: Enable the Google Sheets API
1. In the search bar at the top of the page, type **Google Sheets API**.
2. Click on the first result.
3. Click the blue **Enable** button.

## Step 3: Create the Service Account (The "Robot")
1. On the left-hand sidebar, click on **Credentials** (under *APIs & Services*).
2. Click **+ CREATE CREDENTIALS** at the top of the page, and select **Service Account**.
3. Name the account something descriptive, like `email-drafter-bot`.
4. Click **Create and Continue**.
5. You do not need to assign any special roles. Just scroll down and click **Done**.

## Step 4: Generate the JSON Key
1. In your Credentials list, you will now see your newly created Service Account under the "Service Accounts" section.
2. Click on the email address of that Service Account (e.g., `email-drafter-bot@pocketfm-automations.iam.gserviceaccount.com`).
3. Click on the **KEYS** tab at the top.
4. Click **ADD KEY** -> **Create new key**.
5. Ensure **JSON** is selected, and click **Create**. 
6. A file will immediately download to your computer.

## Step 5: Final Configuration (Crucial!)
1. Rename the downloaded file to exactly `credentials.json`.
2. Move this file into the `e:\Internship\PocketFM\backend` directory.
3. Go back to your Google Cloud tab and **copy the email address** of the Service Account you just made.
4. Open the PocketFM Tracker Google Sheet in your web browser.
5. Click the big green **Share** button in the top right corner.
6. Paste the robot's email address in, give it **Editor** permissions, and click **Send**. 

*(Note: Uncheck "Notify people" before clicking send, since the robot doesn't have an inbox to check!)*

---
**Why are we doing this?**
By sharing the sheet with the Service Account email, you are officially authorizing the Python script to read the authors' data and write the ChatGPT contexts directly into the spreadsheet on your behalf.
