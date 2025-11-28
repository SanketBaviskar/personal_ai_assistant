from typing import List, Dict, Any
from abc import ABC, abstractmethod

class BaseConnector(ABC):
    @abstractmethod
    def fetch_data(self, credentials: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetches data from the source.
        Returns a list of dictionaries, each containing:
        - text: str (The content)
        - source_metadata: dict (Must contain 'source_app' and 'source_url')
        """
        pass
