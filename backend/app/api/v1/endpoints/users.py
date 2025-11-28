from typing import Any

from fastapi import APIRouter, Depends
from app.api import deps
from app.schemas import user as schemas
from app.models import user as models

router = APIRouter()

@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user
