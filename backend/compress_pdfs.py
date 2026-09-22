import os
import fitz  # PyMuPDF

def compress_pdf(input_path, output_path):
    print(f"Compressing {input_path}...")
    try:
        doc = fitz.open(input_path)
        # garbage=4: removes unused objects, duplicate objects, etc.
        # deflate=True: compresses streams
        doc.save(output_path, garbage=4, deflate=True)
        doc.close()
        
        orig_size = os.path.getsize(input_path)
        new_size = os.path.getsize(output_path)
        print(f"Original size: {orig_size / 1024 / 1024:.2f} MB")
        print(f"Compressed size: {new_size / 1024 / 1024:.2f} MB")
        print(f"Reduction: {100 - (new_size / orig_size * 100):.2f}%\n")
    except Exception as e:
        print(f"Failed to compress {input_path}: {e}")

if __name__ == "__main__":
    pdfs = [
        "_OceanofPDF.com_In_Another_World_With_My_Smartphone_Volume_2_-_Patora_Fuyuhara.pdf",
        "_OceanofPDF.com_In_Another_World_With_My_Smartphone_Volume_3_-_Patora_Fuyuhara.pdf",
        "_OceanofPDF.com_In_Another_World_With_My_Smartphone_Volume_4_-_Patora_Fuyuhara.pdf",
        "_OceanofPDF.com_In_Another_World_With_My_Smartphone_Volume_5_-_Patora_Fuyuhara.pdf"
    ]
    
    for pdf in pdfs:
        if os.path.exists(pdf):
            output_name = f"compressed_{pdf}"
            compress_pdf(pdf, output_name)
        else:
            print(f"File not found: {pdf}")
