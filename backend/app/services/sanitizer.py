import re

class Sanitizer:
    EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    PHONE_REGEX = r"\+?(\d{1,3})?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})"

    @staticmethod
    def clean_text(text: str) -> str:
        """Removes excessive whitespace and non-printable characters."""
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @classmethod
    def mask_pii(cls, text: str) -> str:
        """Masks emails and phone numbers in the text."""
        text = re.sub(cls.EMAIL_REGEX, "[EMAIL]", text)
        text = re.sub(cls.PHONE_REGEX, "[PHONE]", text)
        return text

sanitizer = Sanitizer()
