from __future__ import annotations

import os
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger

from api.db import db_client
from api.db.models import UserModel
from api.services.auth.depends import get_user
from api.services.integrations.google_sheets.client import (
    exchange_code_for_tokens,
    get_google_drive_auth_url,
    get_sheet_header_columns,
    get_sheet_tabs,
    list_user_drive_sheets,
    refresh_google_oauth_token,
)

router = APIRouter(prefix="/integrations/google-drive", tags=["Google Drive Integration"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")


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
            credential_type="custom_header",
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


@router.get("/accounts")
async def list_mounted_accounts(
    user: UserModel = Depends(get_user),
) -> List[Dict[str, Any]]:
    """List all mounted Google Drive accounts for the organization."""
    if not user.selected_organization_id:
        raise HTTPException(status_code=400, detail="No organization selected")

    credentials = await db_client.get_credentials_for_organization(user.selected_organization_id)
    accounts = []
    for c in credentials:
        if c.credential_data and "refresh_token" in c.credential_data:
            accounts.append({
                "uuid": c.credential_uuid,
                "name": c.name,
                "created_at": c.created_at,
            })
    return accounts


async def _get_access_token_for_cred(credential_uuid: str, organization_id: int) -> str:
    credential = await db_client.get_credential_by_uuid(credential_uuid, organization_id)
    if not credential or not credential.credential_data:
        raise HTTPException(status_code=404, detail="Mounted Google Drive credential not found")

    cred_data = credential.credential_data
    refresh_token = cred_data.get("refresh_token")
    client_id = cred_data.get("client_id") or GOOGLE_CLIENT_ID
    client_secret = cred_data.get("client_secret") or GOOGLE_CLIENT_SECRET

    if not refresh_token:
        raise HTTPException(status_code=400, detail="Credential missing refresh token")

    access_token = await refresh_google_oauth_token(refresh_token, client_id, client_secret)
    if not access_token:
        raise HTTPException(status_code=401, detail="Failed to refresh Google Drive access token")

    return access_token


@router.get("/files")
async def list_drive_files(
    credential_uuid: str = Query(..., description="UUID of mounted Google Drive credential"),
    user: UserModel = Depends(get_user),
) -> Dict[str, Any]:
    """List Google Sheets and Excel files from the user's mounted Google Drive."""
    if not user.selected_organization_id:
        raise HTTPException(status_code=400, detail="No organization selected")

    access_token = await _get_access_token_for_cred(credential_uuid, user.selected_organization_id)
    files = await list_user_drive_sheets(access_token)
    return {"files": files}


@router.get("/sheets")
async def list_spreadsheet_tabs(
    credential_uuid: str = Query(..., description="UUID of mounted Google Drive credential"),
    spreadsheet_id: str = Query(..., description="Google Spreadsheet ID or URL"),
    user: UserModel = Depends(get_user),
) -> Dict[str, Any]:
    """List worksheet tabs (e.g. Sheet1, Leads) in a Google Spreadsheet."""
    if not user.selected_organization_id:
        raise HTTPException(status_code=400, detail="No organization selected")

    access_token = await _get_access_token_for_cred(credential_uuid, user.selected_organization_id)
    tabs = await get_sheet_tabs(spreadsheet_id, access_token)
    return {"sheets": tabs}


@router.get("/columns")
async def list_sheet_columns(
    credential_uuid: str = Query(..., description="UUID of mounted Google Drive credential"),
    spreadsheet_id: str = Query(..., description="Google Spreadsheet ID or URL"),
    sheet_name: str = Query("Sheet1", description="Target tab name"),
    user: UserModel = Depends(get_user),
) -> Dict[str, Any]:
    """Fetch header columns (Row 1) from a worksheet tab for visual tool variable mapping."""
    if not user.selected_organization_id:
        raise HTTPException(status_code=400, detail="No organization selected")

    access_token = await _get_access_token_for_cred(credential_uuid, user.selected_organization_id)
    columns = await get_sheet_header_columns(spreadsheet_id, sheet_name, access_token)
    return {"columns": columns}
