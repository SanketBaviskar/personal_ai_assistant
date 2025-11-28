from typing import List
import re

class ChunkerService:
    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> List[str]:
        """
        Splits text into chunks of approximately `chunk_size` characters,
        with `overlap` characters between chunks.
        Uses a simple recursive strategy: Paragraphs -> Sentences -> Words (implicitly by char count).
        """
        if not text:
            return []

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + self.chunk_size
            
            # If we are not at the end of the text, try to find a natural break point
            if end < text_len:
                # Look for the last period, newline, or space within the overlap window
                # to avoid splitting words or sentences in the middle if possible.
                # Search backwards from 'end'
                lookback_window = text[max(start, end - self.overlap):end]
                
                # Priority 1: Newlines (Paragraphs)
                match = re.search(r'\n+', lookback_window[::-1]) # Reverse search
                if match:
                    break_point = len(lookback_window) - match.start()
                    end = max(start, end - self.overlap) + break_point
                else:
                    # Priority 2: Periods (Sentences)
                    match = re.search(r'\.\s+', lookback_window[::-1])
                    if match:
                        break_point = len(lookback_window) - match.start()
                        end = max(start, end - self.overlap) + break_point
                    else:
                        # Priority 3: Spaces (Words)
                        match = re.search(r'\s+', lookback_window[::-1])
                        if match:
                            break_point = len(lookback_window) - match.start()
                            end = max(start, end - self.overlap) + break_point
            
            # Ensure we make progress
            if end <= start:
                end = start + self.chunk_size

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move start forward, subtracting overlap
            start = end - self.overlap
            
            # Safety check to prevent infinite loops if overlap >= chunk_size (configuration error)
            if start >= end:
                 start = end

        return chunks

chunker = ChunkerService()
