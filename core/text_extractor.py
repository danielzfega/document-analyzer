import pdfplumber
import docx

def extract_pdf_text(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += "\n" + page.extract_text()
    return text.strip()


def extract_docx_text(file_path: str) -> str:
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])
