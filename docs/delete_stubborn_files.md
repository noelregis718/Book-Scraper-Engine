# How to Delete Stubborn Files and Folders in Windows

Sometimes when downloading files or running scrapers, a file might get saved with invalid characters, trailing spaces, or a path that exceeds Windows' normal length limits (260 characters). When this happens, Windows Explorer and standard command-line tools like PowerShell will throw errors such as:
- `The system cannot find the file specified`
- `File name too long`
- `Access Denied`

This prevents you from deleting the file, and as a result, prevents you from deleting the parent folder containing it.

## The Solution: UNC Paths

To bypass the standard Windows path parser and delete the file, you can use the **Universal Naming Convention (UNC)** path. By prefixing the absolute path with `\\?\`, you tell the Windows API to skip all standard validation checks and pass the string directly to the file system driver.

### Step-by-Step Fix (Using Python)

We have a script located at `backend/delete_stubborn.py` that utilizes this trick. 

1. **Find the absolute path** of the stubborn folder or file you want to delete (e.g., `e:\Internship\PocketFM\corrupted_folder`).
2. **Prepend the UNC prefix** `\\?\` to the path. So your target string becomes `\\?\e:\Internship\PocketFM\corrupted_folder`.
3. **Execute the system command** via Python to forcefully remove it.

### Example Code (`backend/delete_stubborn.py`)

```python
import os

# 1. Define the target path with the UNC prefix
target = r"\\?\e:\Internship\PocketFM\downloads_sep26"

# 2. Use the Windows command line 'rmdir' (for folders) or 'del' (for files)
try:
    # /S removes all directories and files in the specified directory
    # /Q operates in quiet mode (no confirmation)
    os.system(f'rmdir /S /Q "{target}"')
    print("Deleted successfully!")
except Exception as e:
    print(f"Error: {e}")
```

### Quick Command Line (CMD) Alternative

If you don't want to use Python, you can open a standard Command Prompt (`cmd.exe`) and type the following directly:

```cmd
rmdir /S /Q "\\?\e:\Internship\PocketFM\your_corrupt_folder_name"
```

*Note: Make sure to use the absolute path starting with your drive letter!*
