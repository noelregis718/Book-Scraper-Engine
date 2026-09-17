import os
import shutil

def move_folders_to_subfolder(downloads_dir, drive_root_dir, target_subfolder_name):
    target_dir = os.path.join(drive_root_dir, target_subfolder_name)
    
    if not os.path.exists(target_dir):
        print(f"Creating target folder: {target_dir}")
        os.makedirs(target_dir)

    local_folders = [f for f in os.listdir(downloads_dir) if os.path.isdir(os.path.join(downloads_dir, f))]
    
    moved_count = 0
    cleaned_up_count = 0

    for folder_name in local_folders:
        src_path = os.path.join(drive_root_dir, folder_name)
        dst_path = os.path.join(target_dir, folder_name)
        
        # Only process if we actually copied it to the root
        if os.path.exists(src_path) and os.path.isdir(src_path):
            if os.path.exists(dst_path):
                # It already exists in the Romantasy folder! We will just leave it alone since you asked not to delete anything.
                print(f"[{folder_name}] Already exists in {target_subfolder_name}. Skipping to avoid deleting anything.")
            else:
                # Move it into the Romantasy folder
                print(f"[{folder_name}] Moving into {target_subfolder_name}...")
                try:
                    shutil.move(src_path, dst_path)
                    moved_count += 1
                except Exception as e:
                    print(f"  -> Error moving {src_path}: {e}")

    print("\n==================================================")
    print("MOVE COMPLETE")
    print(f"Folders successfully moved into '{target_subfolder_name}': {moved_count}")
    print("==================================================")

if __name__ == "__main__":
    DOWNLOADS_DIR = r"e:\Internship\PocketFM\downloads"
    DRIVE_ROOT_DIR = r"E:\PocketFM Google Drive"
    TARGET_SUBFOLDER = "Romantasy"
    
    move_folders_to_subfolder(DOWNLOADS_DIR, DRIVE_ROOT_DIR, TARGET_SUBFOLDER)
