import httpx
from typing import List, Dict, Any
from app.services.connectors.base import BaseConnector

class NotionConnector(BaseConnector):
    def fetch_data(self, credentials: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Mock implementation for now as we don't have a real Notion API key to test with in this env
        # In production, this would use httpx to call https://api.notion.com/v1/search
        
        api_key = credentials.get("api_key")
        if not api_key:
            raise ValueError("Missing Notion API Key")

        # Simulating fetch
        return [
            {
                "text": "Project Plan: Q4 Goals. 1. Launch MVP. 2. Get 100 users.",
                "source_metadata": {
                    "source_app": "notion",
                    "source_url": "https://notion.so/project-plan"
                }
            },
            {
                "text": "Meeting Notes: Design Review. Action items: Fix padding on login screen.",
                "source_metadata": {
                    "source_app": "notion",
                    "source_url": "https://notion.so/meeting-notes"
                }
            }
        ]
