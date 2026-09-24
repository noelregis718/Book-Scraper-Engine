import os
import pymupdf as fitz  # PyMuPDF
from pdf2docx import Converter

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
        return True
    except Exception as e:
        print(f"Failed to compress {input_path}: {e}")
        return False

def convert_pdf_to_docx(pdf_path, docx_path):
    print(f"Converting {pdf_path} to DOCX...")
    try:
        cv = Converter(pdf_path)
        cv.convert(docx_path)
        cv.close()
        print(f"Successfully created: {docx_path}\n")
    except Exception as e:
        print(f"Failed to convert {pdf_path}: {e}")

if __name__ == "__main__":
    pdfs = [
        "_OceanofPDF.com_Scum_villains_self_saving_system_-_MXTX.pdf",
        "_OceanofPDF.com_The_Scum_Villains_Self-Saving_System__Ren_Zha_Fanpai_Zijiu_Xitong_Novel_Vol_2_-_Mo_Xiang_Tong_Xiu.pdf",
        "_OceanofPDF.com_The_Scum_Villains_Self-Saving_System_Vol_3_-_Mo_Xiang_Tong_Xiu.pdf",
        "_OceanofPDF.com_The_Scum_Villains_Self-Saving_System__Ren_Zha_Fanpai_Zijiu_Xitong_Novel_Vol_4_-_Mo_Xiang_Tong_Xiu.pdf"
    ]
    
    for pdf in pdfs:
        if os.path.exists(pdf):
            compressed_name = f"compressed_{pdf}"
            docx_name = compressed_name.replace(".pdf", ".docx")
            
            # Step 1: Compress
            success = compress_pdf(pdf, compressed_name)
            
            # Step 2: Convert to DOCX if compression was successful
            if success:
                convert_pdf_to_docx(compressed_name, docx_name)
        else:
            print(f"File not found: {pdf}")
