import os
import json
import pytesseract
from pdf2image import convert_from_path
import multiprocessing
import urllib.parse

# Set the path to your Tesseract-OCR executable if needed:
pytesseract.pytesseract.tesseract_cmd = r"D:\Tesseract_OCR\tesseract.exe"

# Folder where the PDFs are located (update this path if needed)
pdf_folder = r"downloaded_pdfs"  # or provide the full path if not in current directory

# Output JSON file where OCR results will be stored
output_json = "ocr_output.json"

# Specify the language code: use "ara" for Arabic or "fra" for French, etc.
ocr_lang = "ara"  # Change to "fra" if processing French PDFs

def ocr_page(img):
    """Perform OCR on a single image (PDF page)"""
    return pytesseract.image_to_string(img, lang=ocr_lang)

def process_pdf(filename):
    """
    Process a single PDF: convert pages to images and perform OCR on each page in parallel.
    Returns a tuple of (filename, full_text).
    """
    pdf_path = os.path.join(pdf_folder, filename)
    print(f"Processing {filename}...")
    try:
        # Convert PDF pages to images
        images = convert_from_path(pdf_path)
        
        # Process OCR on each page in parallel.
        # You can adjust the number of processes if memory is a concern.
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            ocr_texts = pool.map(ocr_page, images)
        
        # Combine OCR results with page markers
        full_text = ""
        for page_number, text in enumerate(ocr_texts, start=1):
            full_text += f"--- Page {page_number} ---\n{text}\n"
        
        if not full_text.strip():
            print(f"Warning: No text extracted from {filename}")
        
        return filename, full_text
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return filename, f"Error: {e}"

def main():
    results = {}
    
    # Loop through all PDF files in the folder
    for filename in os.listdir(pdf_folder):
        if filename.lower().endswith(".pdf"):
            # Optionally, decode filename (if URL-encoded in any way)
            decoded_filename = urllib.parse.unquote(filename)
            fname, full_text = process_pdf(decoded_filename)
            results[fname] = full_text

    # Write results to JSON file (using UTF-8 and ensure_ascii=False to preserve characters)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"OCR processing completed. Results saved to {output_json}")

if __name__ == '__main__':
    multiprocessing.freeze_support()  # Required for Windows when using multiprocessing
    main()
