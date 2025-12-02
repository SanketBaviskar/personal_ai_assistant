from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.core.config import settings
from app.schemas import user as schemas
from app.models import user as models
from app.services.user_service import user_service

router = APIRouter()

@router.post("/login/access-token", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = user_service.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/signup", response_model=schemas.User)
def create_user_signup(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
) -> Any:
    """
    Create new user without the need to be logged in
    """
    user = user_service.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    user = user_service.create(db, obj_in=user_in)
    return user

@router.post("/login/google", response_model=schemas.Token)
def login_google(
    *,
    db: Session = Depends(deps.get_db),
    google_auth: schemas.GoogleAuth,
) -> Any:
    """
    Login with Google ID Token.
    """
    from google.oauth2 import id_token
    from google.auth.transport import requests
    import os

    try:
        # Verify the token
        # CLIENT_ID should be in settings, but for now we can accept any valid token for this app
        # or strictly verify against a configured CLIENT_ID
        client_id = os.getenv("GOOGLE_CLIENT_ID") 
        id_info = id_token.verify_oauth2_token(google_auth.token, requests.Request(), client_id)

        email = id_info.get("email")
        google_sub = id_info.get("sub")
        
        if not email:
             raise HTTPException(status_code=400, detail="Invalid Google Token: No email found")

        # Check if user exists
        user = user_service.get_by_email(db, email=email)
        if not user:
            # Create user
            # We need a random password or handle password-less
            # For now, we generate a random password
            import secrets
            random_password = secrets.token_urlsafe(16)
            user_in = schemas.UserCreate(email=email, password=random_password)
            user = user_service.create(db, obj_in=user_in)
            # Update google_sub
            user.google_sub = google_sub
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update google_sub if not set
            if not user.google_sub:
                user.google_sub = google_sub
                db.add(user)
                db.commit()
                db.refresh(user)
        
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return {
            "access_token": security.create_access_token(
                user.id, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
        }

    except ValueError as e:
        # Invalid token
        raise HTTPException(status_code=400, detail=f"Invalid Google Token: {str(e)}")

@router.post("/google-drive", response_model=schemas.User)
def connect_google_drive(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    auth_data: schemas.GoogleAuthCode,
) -> Any:
    """
    Connect Google Drive by exchanging auth code for tokens.
    """
    from google_auth_oauthlib.flow import Flow
    
    try:
        # Create flow instance to exchange code
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=['https://www.googleapis.com/auth/drive.readonly'],
            redirect_uri=auth_data.redirect_uri
        )
        
        flow.fetch_token(code=auth_data.code)
        credentials = flow.credentials
        
        # Update user with tokens
        current_user.google_access_token = credentials.token
        current_user.google_refresh_token = credentials.refresh_token
        current_user.google_drive_connected = True
        
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        
        return current_user
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to connect Google Drive: {str(e)}")

