from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models import user as models
from app.services.credential_service import credential_service
from app.services.connectors.notion_connector import NotionConnector
from app.services.connectors.jira_connector import JiraConnector
from app.services.connectors.email_connector import EmailConnector

router = APIRouter()

@router.post("/{provider}")
def store_connector_credentials(
    provider: str,
    credentials: Dict[str, Any],
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Store credentials for a provider (notion, jira, email).
    """
    if provider not in ["notion", "jira", "email"]:
        raise HTTPException(status_code=400, detail="Invalid provider")
    
    credential_service.store_credentials(
        db=db,
        user_id=current_user.id,
        provider=provider,
        data=credentials
    )
    return {"message": f"Credentials for {provider} stored successfully"}

@router.post("/{provider}/sync")
def sync_connector_data(
    provider: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Trigger a manual sync for a provider.
    Fetches data using stored credentials.
    """
    credentials = credential_service.get_credentials(db, current_user.id, provider)
    if not credentials:
        raise HTTPException(status_code=400, detail=f"No credentials found for {provider}")

    connector = None
    if provider == "notion":
        connector = NotionConnector()
    elif provider == "jira":
        connector = JiraConnector()
    elif provider == "email":
        connector = EmailConnector()
    else:
        raise HTTPException(status_code=400, detail="Invalid provider")

    try:
        data = connector.fetch_data(credentials)
        return {"message": f"Fetched {len(data)} items from {provider}", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
