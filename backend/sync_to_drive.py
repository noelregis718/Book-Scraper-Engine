import os
import shutil

def sync_local_downloads_to_mapped_drive(downloads_dir, target_dir):
    """Copies folders from downloads_dir to target_dir, skipping existing ones."""
    if not os.path.exists(downloads_dir):
        print(f"Error: Directory {downloads_dir} not found.")
        return
        
    if not os.path.exists(target_dir):
        print(f"Target directory {target_dir} does not exist. Creating it...")
        try:
            os.makedirs(target_dir)
        except Exception as e:
            print(f"Failed to create target directory: {e}")
            return

    local_folders = [f for f in os.listdir(downloads_dir) if os.path.isdir(os.path.join(downloads_dir, f))]
    print(f"Found {len(local_folders)} local folders in {downloads_dir}")

    uploaded_count = 0
    skipped_count = 0

    for i, folder_name in enumerate(local_folders, start=1):
        print(f"\n[{i}/{len(local_folders)}] Processing: {folder_name}")
        
        src_folder = os.path.join(downloads_dir, folder_name)
        dst_folder = os.path.join(target_dir, folder_name)
        
        if os.path.exists(dst_folder):
            print(f"  -> Skipping. Folder '{folder_name}' already exists in target drive.")
            skipped_count += 1
            continue
            
        print(f"  -> Copying '{folder_name}' to target drive...")
        try:
            # shutil.copytree copies the entire directory tree
            shutil.copytree(src_folder, dst_folder)
            uploaded_count += 1
            print(f"  -> Success!")
        except Exception as e:
            print(f"  -> Exception during copy for '{folder_name}': {e}")

    print("\n==================================================")
    print("SYNC COMPLETE")
    print(f"Total Folders Skipped (Already on Drive): {skipped_count}")
    print(f"Total Folders Successfully Copied: {uploaded_count}")
    print("==================================================")

if __name__ == "__main__":
    DOWNLOADS_DIR = r"e:\Internship\PocketFM\downloads"
    TARGET_DRIVE_DIR = r"E:\PocketFM Google Drive"
    
    sync_local_downloads_to_mapped_drive(DOWNLOADS_DIR, TARGET_DRIVE_DIR)
