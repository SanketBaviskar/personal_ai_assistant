from typing import List

class EmbeddingService:
    def get_embedding(self, text: str) -> List[float]:
        """
        Generates a vector embedding for the given text.
        Currently returns a deterministic mock vector for development.
        """
        # Mock embedding: 384 dimensions (common for small models like all-MiniLM-L6-v2)
        # Deterministic based on text length to allow simple verification
        seed = len(text) % 100
        return [float(seed) / 100.0] * 384

embedding_service = EmbeddingService()
