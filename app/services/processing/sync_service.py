from sqlalchemy.orm import Session
from app.services.credential_service import credential_service
from app.services.connectors.notion_connector import NotionConnector
from app.services.connectors.jira_connector import JiraConnector
from app.services.connectors.email_connector import EmailConnector
from app.services.processing.rag_pipeline import rag_pipeline
from app.db.session import SessionLocal

class SyncService:
    def sync_user_data(self, user_id: int):
        """
        Orchestrates the sync process for a single user.
        Iterates through all supported providers, fetches data, and runs RAG pipeline.
        """
        print(f"Starting sync for user_id={user_id}")
        db: Session = SessionLocal()
        try:
            providers = {
                "notion": NotionConnector(),
                "jira": JiraConnector(),
                "email": EmailConnector()
            }

            for provider_name, connector in providers.items():
                credentials = credential_service.get_credentials(db, user_id, provider_name)
                if not credentials:
                    print(f"No credentials found for {provider_name}, skipping.")
                    continue
                
                print(f"Fetching data from {provider_name}...")
                try:
                    data = connector.fetch_data(credentials)
                    print(f"Fetched {len(data)} items from {provider_name}.")
                    
                    for item in data:
                        text = item.get("text")
                        source_metadata = item.get("source_metadata")
                        if text and source_metadata:
                            rag_pipeline.process_document(user_id, text, source_metadata)
                            
                except Exception as e:
                    print(f"Error syncing {provider_name}: {e}")
                    
        finally:
            db.close()
        print(f"Sync finished for user_id={user_id}")

sync_service = SyncService()
