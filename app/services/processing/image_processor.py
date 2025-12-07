from typing import Optional
import io
import easyocr
import numpy as np
from PIL import Image

class ImageProcessor:
    def __init__(self):
        # Initialize EasyOCR reader for English
        # gpu=False can be set if user has no GPU setup or issues with CAD
        # but defaulting to True/Auto is better usually. 
        # For compatibility, let's try-catch initialization or lazy load.
        self.reader = None

    def _get_reader(self):
        if not self.reader:
            print("Initializing EasyOCR model...")
            self.reader = easyocr.Reader(['en'], gpu=False) # GPU=False for wider compatibility on local
        return self.reader

    def extract_text(self, file_bytes: bytes) -> Optional[str]:
        """
        Extracts text from an image file using EasyOCR.
        """
        try:
            reader = self._get_reader()
            
            # EasyOCR expects bytes, numpy array, or file path
            # Using read_text directly on bytes
            result = reader.readtext(file_bytes, detail=0) 
            
            return " ".join(result)
        except Exception as e:
            print(f"Error extracting text from Image using EasyOCR: {e}")
            return None

image_processor = ImageProcessor()
