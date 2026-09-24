import os
import zipfile
import tempfile
import shutil
from pathlib import Path
from PIL import Image
from docx import Document
from docx.shared import Inches

def compress_and_convert_cbz_to_docx(cbz_path, output_docx_path=None):
    if not os.path.exists(cbz_path):
        print(f"Error: Could not find file {cbz_path}")
        return

    if output_docx_path is None:
        output_docx_path = os.path.splitext(cbz_path)[0] + ".docx"

    print(f"Opening CBZ file: {cbz_path}")
    
    # Create a temporary directory to extract and compress images
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # 1. Extract CBZ (which is just a ZIP archive)
            with zipfile.ZipFile(cbz_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            print("Extracted images from CBZ.")

            # 2. Gather and sort the images (CBZ relies on alphabetical sorting)
            valid_extensions = {".jpg", ".jpeg", ".png", ".webp"}
            image_paths = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if Path(file).suffix.lower() in valid_extensions:
                        image_paths.append(os.path.join(root, file))
            
            # Sort alphabetically so pages stay in correct order
            image_paths.sort()

            if not image_paths:
                print("No valid images found in the CBZ file.")
                return

            print(f"Found {len(image_paths)} images. Starting compression and conversion...")

            # 3. Create the Word Document
            doc = Document()

            for i, img_path in enumerate(image_paths):
                # Compress the image
                try:
                    with Image.open(img_path) as img:
                        # Convert to RGB (in case it's RGBA/PNG) to save as JPEG
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # Resize aggressively (max width 800px) to compress as much as possible
                        max_width = 800
                        if img.width > max_width:
                            ratio = max_width / img.width
                            new_size = (max_width, int(img.height * ratio))
                            img = img.resize(new_size, Image.Resampling.LANCZOS)
                        
                        # Save compressed version to a temp file
                        compressed_path = os.path.join(temp_dir, f"compressed_{i}.jpg")
                        img.save(compressed_path, format="JPEG", quality=60, optimize=True)
                        
                        # Insert into Word Document
                        doc.add_picture(compressed_path, width=Inches(6.0)) # 6 inches fits nicely on a standard page
                        
                        if i % 10 == 0 and i > 0:
                            print(f"Processed {i}/{len(image_paths)} pages...")
                            
                except Exception as e:
                    print(f"Failed to process image {img_path}: {e}")

            # 4. Save the Document
            print(f"Saving final Word Document to {output_docx_path}...")
            doc.save(output_docx_path)
            print("Done! Compression and conversion successful.")

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    import sys
    # If run from command line with a file argument
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
        compress_and_convert_cbz_to_docx(target_file)
    else:
        print("Usage: python convert_cbz.py \"path/to/your_file.cbz\"")
        print("You can also hardcode the path in the script below if you prefer.")
        
        # Hardcode your path here if you prefer to just run the script:
        # compress_and_convert_cbz_to_docx(r"C:\path\to\your\file.cbz")
