import os
import zipfile

def compress_folder():
    source_dir = 'Downloaded_SRTs'
    output_zip = 'Downloaded_SRTs.zip'

    print(f"Compressing {source_dir} into {output_zip} with maximum deflate compression (level 9)...")

    total_files = 0
    total_uncompressed_bytes = 0

    with zipfile.ZipFile(output_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=os.path.dirname(source_dir))
                zipf.write(file_path, arcname=arcname)
                total_files += 1
                total_uncompressed_bytes += os.path.getsize(file_path)

    zip_size = os.path.getsize(output_zip)
    ratio = (1 - (zip_size / total_uncompressed_bytes)) * 100 if total_uncompressed_bytes > 0 else 0

    print(f"\nCompression complete!")
    print(f"Total files zipped: {total_files}")
    print(f"Original size: {total_uncompressed_bytes / (1024*1024):.2f} MB")
    print(f"Compressed zip size: {zip_size / (1024*1024):.2f} MB")
    print(f"Space saved: {ratio:.1f}%")
    print(f"Zip file location: {os.path.abspath(output_zip)}")

if __name__ == '__main__':
    compress_folder()
