import io
from pypdf import PdfReader
from typing import Optional

class PDFProcessor:
    def extract_text(self, file_bytes: bytes) -> Optional[str]:
        """
        Extracts text from a PDF file provided as bytes.
        """
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return None

pdf_processor = PDFProcessor()
