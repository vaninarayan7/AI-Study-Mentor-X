from pypdf import PdfReader

def extract_text(pdf_path_or_file):
    """
    Extracts text from a PDF file or file-like object using pypdf.
    """
    try:
        reader = PdfReader(pdf_path_or_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""
