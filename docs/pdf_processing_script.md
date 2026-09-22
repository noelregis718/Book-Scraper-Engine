# PDF Compression & Conversion Tool

## Overview

The `process_pdfs.py` script is a dedicated utility designed to seamlessly compress PDF documents and subsequently convert them into editable Microsoft Word (`.docx`) formats. This tool helps optimize file sizes without significant quality loss and ensures that text content can be easily edited or integrated into other workflows.

## Features

1. **PDF Compression**: Uses the `PyMuPDF` (`fitz`) library to compress PDF streams and remove unused/duplicate objects. This process reduces the file size while maintaining readability.
2. **Format Conversion**: Uses the `pdf2docx` library to convert the newly compressed PDF into a `.docx` document, preserving layout, text, and structure as accurately as possible.
3. **Automated Chaining**: Automatically handles compression first, checks for success, and then pipelines the compressed output directly into the conversion module.
4. **Size Analytics**: Provides real-time console feedback comparing the original PDF size, the compressed size, and the calculated reduction percentage.

## Prerequisites

Before running the tool, ensure you have the required Python libraries installed:

```bash
pip install PyMuPDF pdf2docx
```

## Usage

1. Place your target PDF files in the same directory as the script. By default, the script looks for a predefined list of PDFs, but it can be easily modified to read any `.pdf` files in a directory.
2. Execute the script from your terminal:

```bash
python backend/process_pdfs.py
```

## Execution Flow

1. **Compression Phase**: 
   - Reads the original PDF.
   - Saves a new file with the `compressed_` prefix.
   - Logs the space saved.
2. **Conversion Phase**: 
   - If compression succeeds, reads the `compressed_<filename>.pdf`.
   - Generates a `compressed_<filename>.docx` file.

## Under the Hood

- **PyMuPDF (`fitz`)**: We utilize the `garbage=4` and `deflate=True` parameters during the save operation. `garbage=4` cleans up the internal structure of the PDF (removing unused objects and duplicates), while `deflate=True` enables compression on the PDF streams.
- **pdf2docx**: Parses the PDF components and reconstructs them into OpenXML format for Word.

## Troubleshooting

- **Memory/Timeout Issues during Conversion**: Highly graphical or extremely large PDFs may take longer to convert to DOCX. Let the script run.
- **Missing Files**: Ensure the target files exist in the same directory. The script gracefully skips missing files and alerts the user in the console output.
