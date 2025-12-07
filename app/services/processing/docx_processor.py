from typing import Optional
import io
import docx

class DocxProcessor:
    def extract_text(self, file_bytes: bytes) -> Optional[str]:
        """
        Extracts text from a .docx file provided as bytes.
        """
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            return '\n'.join(full_text)
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
            return None

docx_processor = DocxProcessor()
