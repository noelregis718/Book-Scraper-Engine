import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate_google_drive():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'token.json')
    credentials_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'credentials.json')

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                print(f"Error: {credentials_path} not found. Please create OAuth 2.0 Client ID credentials in Google Cloud Console, download the JSON, rename it to 'credentials.json', and place it in the backend folder.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)

def create_drive_folder(service, folder_name, parent_id):
    """Create a folder on Google Drive"""
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    
    # Check if folder already exists
    query = f"name='{folder_name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    
    if not items:
        file = service.files().create(body=file_metadata, fields='id').execute()
        return file.get('id')
    else:
        return items[0]['id']

def upload_folder_to_drive(local_folder_path, parent_drive_folder_id):
    """
    Uploads the contents of a local folder to a specific Google Drive folder.
    Creates a subfolder in Drive with the name of the local folder.
    """
    if not os.path.exists(local_folder_path):
        print(f"Local folder {local_folder_path} does not exist. Skipping upload.")
        return

    service = authenticate_google_drive()
    if not service:
        print("Failed to authenticate with Google Drive API. Cannot upload.")
        return

    folder_name = os.path.basename(local_folder_path)
    print(f"\n[Drive Upload] Preparing to upload '{folder_name}' to Google Drive...")
    
    # Create the series folder in Drive
    try:
        drive_folder_id = create_drive_folder(service, folder_name, parent_drive_folder_id)
        print(f"[Drive Upload] Created/Found Drive folder '{folder_name}' (ID: {drive_folder_id})")
    except Exception as e:
        print(f"[Drive Upload] Error creating folder in Drive: {e}")
        return

    # Upload files
    files_uploaded = 0
    for filename in os.listdir(local_folder_path):
        # We only upload relevant book files
        if not (filename.endswith('.docx') or filename.endswith('.pdf') or filename.endswith('.epub')):
            continue
            
        file_path = os.path.join(local_folder_path, filename)
        if not os.path.isfile(file_path):
            continue

        print(f"[Drive Upload] Uploading {filename}...")
        
        # Check if file already exists to avoid duplicates
        query = f"name='{filename}' and '{drive_folder_id}' in parents and trashed=false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])
        
        if items:
            print(f"[Drive Upload] File '{filename}' already exists on Drive. Skipping.")
            continue
            
        # Determine mime type
        mime_type = 'application/octet-stream'
        if filename.endswith('.docx'):
            mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif filename.endswith('.pdf'):
            mime_type = 'application/pdf'
        elif filename.endswith('.epub'):
            mime_type = 'application/epub+zip'
            
        file_metadata = {
            'name': filename,
            'parents': [drive_folder_id]
        }
        
        try:
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print(f"[Drive Upload] Successfully uploaded {filename} (ID: {file.get('id')})")
            files_uploaded += 1
        except Exception as e:
            print(f"[Drive Upload] Error uploading {filename}: {e}")
            
    print(f"[Drive Upload] Finished. Uploaded {files_uploaded} files to Google Drive.")
