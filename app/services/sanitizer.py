"""
Service for sanitizing text data.
Handles removal of PII and text cleanup.
"""
import re

class Sanitizer:
    """
    Utility class for text sanitization.
    """
    EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    PHONE_REGEX = r"\+?(\d{1,3})?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})"

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Removes excessive whitespace and non-printable characters.

        Args:
            text (str): The input text.

        Returns:
            str: The cleaned text.
        """
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @classmethod
    def mask_pii(cls, text: str) -> str:
        """
        Masks emails and phone numbers in the text.

        Args:
            text (str): The input text containing potential PII.

        Returns:
            str: The text with PII masked (e.g., [EMAIL], [PHONE]).
        """
        text = re.sub(cls.EMAIL_REGEX, "[EMAIL]", text)
        text = re.sub(cls.PHONE_REGEX, "[PHONE]", text)
        return text

sanitizer = Sanitizer()
