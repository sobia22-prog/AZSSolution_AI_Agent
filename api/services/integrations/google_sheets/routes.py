from __future__ import annotations

import os
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from loguru import logger

from api.db import db_client
from api.db.models import UserModel
from api.services.auth.depends import get_user
from api.services.integrations.google_sheets.client import (
    exchange_code_for_tokens,
    get_google_drive_auth_url,
    get_sheet_header_columns,
    get_sheet_tabs,
    list_user_drive_folders,
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

    state = f"org_{user.selected_organization_id}_usr_{user.id}"
    auth_url = get_google_drive_auth_url(client_id, redirect_uri, state)
    return {"auth_url": auth_url}


@router.get("/callback")
async def oauth_callback(
    code: str = Query(..., description="Authorization code"),
    state: str = Query(..., description="State string"),
    redirect_uri: Optional[str] = Query(None, description="Matching redirect URI"),
) -> HTMLResponse:
    """Callback endpoint to complete 1-click Google Drive mounting."""
    client_id = GOOGLE_CLIENT_ID or os.getenv("GOOGLE_CLIENT_ID", "")
    client_secret = GOOGLE_CLIENT_SECRET or os.getenv("GOOGLE_CLIENT_SECRET", "")

    # Parse org_id and user_id from state
    org_id: Optional[int] = None
    user_id: Optional[int] = None
    if state and "org_" in state and "_usr_" in state:
        try:
            parts = state.split("_usr_")
            org_id = int(parts[0].replace("org_", ""))
            user_id = int(parts[1])
        except Exception:
            pass
    elif state and state.startswith("org_"):
        try:
            org_id = int(state.replace("org_", ""))
        except Exception:
            pass

    if not org_id:
        return HTMLResponse(
            content="<h2 style='font-family:sans-serif;color:#ef4444;'>Error: Invalid state parameter</h2>",
            status_code=400,
        )

    actual_redirect_uri = redirect_uri or "https://azs-solution-ai-agent.vercel.app/api/v1/integrations/google-drive/callback"

    tokens = await exchange_code_for_tokens(code, client_id, client_secret, actual_redirect_uri)
    if not tokens or "refresh_token" not in tokens:
        return HTMLResponse(
            content="<h2 style='font-family:sans-serif;color:#ef4444;'>Error: Failed to obtain refresh token from Google OAuth</h2>",
            status_code=400,
        )

    refresh_token = tokens["refresh_token"]
    credential_name = f"Mounted Google Drive (Org #{org_id})"
    credential_data = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": tokens.get("scope"),
    }

    try:
        existing_creds = await db_client.get_credentials_for_organization(org_id)
        existing = next((c for c in existing_creds if c.name == credential_name or (c.credential_data and "refresh_token" in c.credential_data)), None)

        if existing:
            await db_client.update_credential(
                credential_uuid=existing.credential_uuid,
                organization_id=org_id,
                credential_data=credential_data,
            )
        else:
            await db_client.create_credential(
                organization_id=org_id,
                user_id=user_id,
                name=credential_name,
                description="Mounted Google Drive connection for post-call Google Sheets sync",
                credential_type="custom_header",
                credential_data=credential_data,
            )
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Google Drive Connected</title>
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; background: #f8fafc; color: #0f172a; }
                    .card { background: white; padding: 2.5rem; border-radius: 16px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.08); text-align: center; max-width: 400px; width: 90%; }
                    .icon { color: #10b981; font-size: 54px; margin-bottom: 0.75rem; font-weight: bold; }
                    h2 { margin: 0 0 0.5rem 0; color: #0f172a; font-size: 22px; }
                    p { color: #64748b; font-size: 14px; margin-bottom: 1.5rem; line-height: 1.5; }
                    button { background: #10b981; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 14px; }
                    button:hover { background: #059669; }
                </style>
            </head>
            <body>
                <div class="card">
                    <div class="icon">✓</div>
                    <h2>Google Drive Mounted!</h2>
                    <p>Your Google Drive has been successfully connected to AZS Solution's AI Agent.</p>
                    <button onclick="window.close()">Close Window</button>
                </div>
                <script>
                    if (window.opener) {
                        try {
                            window.opener.postMessage({ type: "GOOGLE_DRIVE_CONNECTED" }, "*");
                        } catch (e) {
                            console.error(e);
                        }
                    }
                    setTimeout(() => {
                        if (window.opener) {
                            window.close();
                        }
                    }, 1200);
                </script>
            </body>
            </html>
            """,
            status_code=200,
        )
    except Exception as e:
        logger.error(f"Error saving mounted Google Drive credential: {e}")
        return HTMLResponse(content=f"<h2 style='font-family:sans-serif;color:#ef4444;'>Error saving credential: {e}</h2>", status_code=500)


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


@router.get("/folders")
async def list_drive_folders(
    credential_uuid: str = Query(..., description="UUID of mounted Google Drive credential"),
    user: UserModel = Depends(get_user),
) -> Dict[str, Any]:
    """List folders in mounted Google Drive."""
    if not user.selected_organization_id:
        raise HTTPException(status_code=400, detail="No organization selected")

    cred = await db_client.get_credential_by_uuid(credential_uuid, user.selected_organization_id)
    if not cred or not cred.credential_data or "refresh_token" not in cred.credential_data:
        raise HTTPException(status_code=404, detail="Mounted Google Drive credential not found")

    refresh_token = cred.credential_data["refresh_token"]
    client_id = GOOGLE_CLIENT_ID or os.getenv("GOOGLE_CLIENT_ID", "") or cred.credential_data.get("client_id", "")
    client_secret = GOOGLE_CLIENT_SECRET or os.getenv("GOOGLE_CLIENT_SECRET", "") or cred.credential_data.get("client_secret", "")

    access_token = await refresh_google_oauth_token(refresh_token, client_id, client_secret)
    if not access_token:
        raise HTTPException(status_code=401, detail="Failed to refresh Google OAuth access token")

    folders = await list_user_drive_folders(access_token)
    return {"folders": folders}


@router.get("/files")
async def list_drive_files(
    credential_uuid: str = Query(..., description="UUID of mounted Google Drive credential"),
    folder_id: Optional[str] = Query(None, description="Optional folder ID filter"),
    user: UserModel = Depends(get_user),
) -> Dict[str, Any]:
    """List spreadsheet files in mounted Google Drive."""
    if not user.selected_organization_id:
        raise HTTPException(status_code=400, detail="No organization selected")

    cred = await db_client.get_credential_by_uuid(credential_uuid, user.selected_organization_id)
    if not cred or not cred.credential_data or "refresh_token" not in cred.credential_data:
        raise HTTPException(status_code=404, detail="Mounted Google Drive credential not found")

    refresh_token = cred.credential_data["refresh_token"]
    client_id = GOOGLE_CLIENT_ID or os.getenv("GOOGLE_CLIENT_ID", "") or cred.credential_data.get("client_id", "")
    client_secret = GOOGLE_CLIENT_SECRET or os.getenv("GOOGLE_CLIENT_SECRET", "") or cred.credential_data.get("client_secret", "")

    access_token = await refresh_google_oauth_token(refresh_token, client_id, client_secret)
    if not access_token:
        raise HTTPException(status_code=401, detail="Failed to refresh Google OAuth access token")

    files = await list_user_drive_sheets(access_token, folder_id=folder_id)
    return {"files": files}


@router.get("/sheets")
async def list_spreadsheet_tabs(
    credential_uuid: str = Query(..., description="UUID of mounted Google Drive credential"),
    spreadsheet_id: str = Query(..., description="Spreadsheet ID or URL"),
    user: UserModel = Depends(get_user),
) -> Dict[str, Any]:
    """List sheet tabs inside a spreadsheet."""
    if not user.selected_organization_id:
        raise HTTPException(status_code=400, detail="No organization selected")

    cred = await db_client.get_credential_by_uuid(credential_uuid, user.selected_organization_id)
    if not cred or not cred.credential_data or "refresh_token" not in cred.credential_data:
        raise HTTPException(status_code=404, detail="Mounted Google Drive credential not found")

    refresh_token = cred.credential_data["refresh_token"]
    client_id = GOOGLE_CLIENT_ID or os.getenv("GOOGLE_CLIENT_ID", "") or cred.credential_data.get("client_id", "")
    client_secret = GOOGLE_CLIENT_SECRET or os.getenv("GOOGLE_CLIENT_SECRET", "") or cred.credential_data.get("client_secret", "")

    access_token = await refresh_google_oauth_token(refresh_token, client_id, client_secret)
    if not access_token:
        raise HTTPException(status_code=401, detail="Failed to refresh Google OAuth access token")

    sheets = await get_sheet_tabs(spreadsheet_id, access_token)
    return {"sheets": sheets}


@router.get("/columns")
async def list_sheet_columns(
    credential_uuid: str = Query(..., description="UUID of mounted Google Drive credential"),
    spreadsheet_id: str = Query(..., description="Spreadsheet ID or URL"),
    sheet_name: str = Query("Sheet1", description="Sheet tab name"),
    user: UserModel = Depends(get_user),
) -> Dict[str, Any]:
    """Fetch header row columns from a spreadsheet tab."""
    if not user.selected_organization_id:
        raise HTTPException(status_code=400, detail="No organization selected")

    cred = await db_client.get_credential_by_uuid(credential_uuid, user.selected_organization_id)
    if not cred or not cred.credential_data or "refresh_token" not in cred.credential_data:
        raise HTTPException(status_code=404, detail="Mounted Google Drive credential not found")

    refresh_token = cred.credential_data["refresh_token"]
    client_id = GOOGLE_CLIENT_ID or os.getenv("GOOGLE_CLIENT_ID", "") or cred.credential_data.get("client_id", "")
    client_secret = GOOGLE_CLIENT_SECRET or os.getenv("GOOGLE_CLIENT_SECRET", "") or cred.credential_data.get("client_secret", "")

    access_token = await refresh_google_oauth_token(refresh_token, client_id, client_secret)
    if not access_token:
        raise HTTPException(status_code=401, detail="Failed to refresh Google OAuth access token")

    columns = await get_sheet_header_columns(spreadsheet_id, sheet_name, access_token)
    return {"columns": columns}
