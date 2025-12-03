import os
import google.generativeai as genai
from typing import Optional
from app.core.config import settings

class ImageProcessor:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro-vision')
        else:
            print("Warning: GEMINI_API_KEY not found. Image processing will be disabled.")
            self.model = None

    def describe_image(self, image_bytes: bytes, mime_type: str) -> Optional[str]:
        """
        Generates a text description of an image using Gemini Vision.
        """
        if not self.model:
            return None

        try:
            image_part = {
                "mime_type": mime_type,
                "data": image_bytes
            }

            prompt = "Describe this image in detail. Capture all text, data, and visual elements relevant for a knowledge base."
            
            response = self.model.generate_content([prompt, image_part])
            return response.text
        except Exception as e:
            print(f"Error describing image: {e}")
            return None

image_processor = ImageProcessor()
