from typing import List, Dict, Any
from app.services.connectors.base import BaseConnector

class EmailConnector(BaseConnector):
    def fetch_data(self, credentials: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Mock implementation
        # In real world, this would use MS Graph API or Gmail API
        
        return [
            {
                "text": "Subject: Welcome to the team! Body: We are excited to have you.",
                "source_metadata": {
                    "source_app": "email",
                    "source_url": "mailto:hr@example.com"
                }
            }
        ]
