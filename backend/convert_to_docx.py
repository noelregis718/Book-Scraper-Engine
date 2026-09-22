import os
from pdf2docx import Converter

def convert_pdf_to_docx(pdf_path, docx_path):
    print(f"Converting {pdf_path} to DOCX...")
    try:
        cv = Converter(pdf_path)
        cv.convert(docx_path)
        cv.close()
        print(f"Successfully created: {docx_path}")
    except Exception as e:
        print(f"Failed to convert {pdf_path}: {e}")

if __name__ == "__main__":
    compressed_pdfs = [
        "compressed__OceanofPDF.com_In_Another_World_With_My_Smartphone_Volume_2_-_Patora_Fuyuhara.pdf",
        "compressed__OceanofPDF.com_In_Another_World_With_My_Smartphone_Volume_3_-_Patora_Fuyuhara.pdf",
        "compressed__OceanofPDF.com_In_Another_World_With_My_Smartphone_Volume_4_-_Patora_Fuyuhara.pdf",
        "compressed__OceanofPDF.com_In_Another_World_With_My_Smartphone_Volume_5_-_Patora_Fuyuhara.pdf"
    ]
    
    for pdf in compressed_pdfs:
        if os.path.exists(pdf):
            docx_name = pdf.replace(".pdf", ".docx")
            convert_pdf_to_docx(pdf, docx_name)
        else:
            print(f"File not found: {pdf}")
