from __future__ import annotations

import os
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from loguru import logger

from api.db import db_client
from api.db.models import UserModel
from api.services.auth.depends import get_user
from api.services.integrations.google_sheets.client import (
    exchange_code_for_tokens,
    get_google_drive_auth_url,
    list_user_drive_sheets,
    refresh_google_oauth_token,
)

router = APIRouter(prefix="/integrations/google-drive", tags=["Google Drive Integration"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


@router.get("/auth-url")
async def get_auth_url(
    redirect_uri: str = Query(..., description="OAuth redirect URI"),
    user: UserModel = Depends(get_user),
) -> Dict[str, str]:
    """Generate Google OAuth2 authorization URL for mounting Google Drive in AZS Solution's AI Agent."""
    if not user.selected_organization_id:
        raise HTTPException(status_code=400, detail="No organization selected")

    client_id = GOOGLE_CLIENT_ID or os.getenv("GOOGLE_CLIENT_ID", "")
    if not client_id:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth Client ID is not configured on the server. Set GOOGLE_CLIENT_ID environment variable.",
        )

    state = f"org_{user.selected_organization_id}"
    auth_url = get_google_drive_auth_url(client_id, redirect_uri, state)
    return {"auth_url": auth_url}


@router.get("/callback")
async def oauth_callback(
    code: str = Query(..., description="Authorization code"),
    state: str = Query(..., description="State string"),
    redirect_uri: str = Query(..., description="Matching redirect URI"),
    user: UserModel = Depends(get_user),
) -> Dict[str, Any]:
    """Callback endpoint to complete 1-click Google Drive mounting."""
    if not user.selected_organization_id:
        raise HTTPException(status_code=400, detail="No organization selected")

    client_id = GOOGLE_CLIENT_ID or os.getenv("GOOGLE_CLIENT_ID", "")
    client_secret = GOOGLE_CLIENT_SECRET or os.getenv("GOOGLE_CLIENT_SECRET", "")

    tokens = await exchange_code_for_tokens(code, client_id, client_secret, redirect_uri)
    if not tokens or "refresh_token" not in tokens:
        raise HTTPException(status_code=400, detail="Failed to obtain refresh token from Google OAuth")

    refresh_token = tokens["refresh_token"]

    # Store mounted Google Drive credential in DB
    credential_name = f"Mounted Google Drive ({user.email or 'Org'})"
    credential_data = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": tokens.get("scope"),
    }

    try:
        credential = await db_client.create_credential(
            organization_id=user.selected_organization_id,
            user_id=user.id,
            name=credential_name,
            description="Mounted Google Drive connection for post-call Google Sheets sync",
            credential_type="custom_header",  # Store securely in external_credentials
            credential_data=credential_data,
        )
        return {
            "status": "success",
            "message": "Google Drive successfully mounted to AZS Solution's AI Agent!",
            "credential_uuid": credential.credential_uuid,
        }
    except Exception as e:
        logger.error(f"Error saving mounted Google Drive credential: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files")
async def list_drive_files(
    credential_uuid: str = Query(..., description="UUID of mounted Google Drive credential"),
    user: UserModel = Depends(get_user),
) -> Dict[str, Any]:
    """List Google Sheets and Excel files from the user's mounted Google Drive."""
    if not user.selected_organization_id:
        raise HTTPException(status_code=400, detail="No organization selected")

    credential = await db_client.get_credential_by_uuid(credential_uuid, user.selected_organization_id)
    if not credential:
        raise HTTPException(status_code=404, detail="Mounted Google Drive credential not found")

    cred_data = credential.credential_data or {}
    refresh_token = cred_data.get("refresh_token")
    client_id = cred_data.get("client_id") or GOOGLE_CLIENT_ID
    client_secret = cred_data.get("client_secret") or GOOGLE_CLIENT_SECRET

    if not refresh_token:
        raise HTTPException(status_code=400, detail="Credential missing refresh token")

    access_token = await refresh_google_oauth_token(refresh_token, client_id, client_secret)
    if not access_token:
        raise HTTPException(status_code=401, detail="Failed to refresh Google Drive access token")

    files = await list_user_drive_sheets(access_token)
    return {"files": files}
