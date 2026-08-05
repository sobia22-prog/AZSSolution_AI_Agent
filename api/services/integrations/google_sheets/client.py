from __future__ import annotations

import json
import re
import urllib.parse
from typing import Any, Dict, List, Optional
import httpx
from loguru import logger

GOOGLE_OAUTH_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_DRIVE_API_FILES_URL = "https://www.googleapis.com/drive/v3/files"
GOOGLE_SHEETS_API_URL = "https://sheets.googleapis.com/v4/spreadsheets"

DEFAULT_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.readonly",
]


def extract_spreadsheet_id(input_str: str) -> str:
    """Extract Google Spreadsheet ID from a Google Drive URL or raw ID string."""
    if not input_str:
        return ""
    
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", input_str)
    if match:
        return match.group(1)
    
    return input_str.strip()


def get_google_drive_auth_url(client_id: str, redirect_uri: str, state: str) -> str:
    """Build Google OAuth2 consent URL for mounting Google Drive."""
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(DEFAULT_SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    return f"{GOOGLE_OAUTH_AUTH_URL}?{urllib.parse.urlencode(params)}"


async def exchange_code_for_tokens(
    code: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
) -> Optional[Dict[str, Any]]:
    """Exchange Google OAuth authorization code for Refresh & Access tokens."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                GOOGLE_OAUTH_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Failed to exchange Google OAuth code: {e}")
        return None


async def refresh_google_oauth_token(
    refresh_token: str,
    client_id: str,
    client_secret: str,
) -> Optional[str]:
    """Obtain a fresh OAuth access token using a stored refresh token."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                GOOGLE_OAUTH_TOKEN_URL,
                data={
                    "refresh_token": refresh_token,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "grant_type": "refresh_token",
                },
            )
            response.raise_for_status()
            data = response.json()
            return data.get("access_token")
    except Exception as e:
        logger.error(f"Failed to refresh Google OAuth token: {e}")
        return None


async def list_user_drive_sheets(access_token: str) -> List[Dict[str, Any]]:
    """List Google Sheets and Excel files from the mounted Google Drive."""
    query = (
        "mimeType='application/vnd.google-apps.spreadsheet' or "
        "mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"
    )
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.get(
                GOOGLE_DRIVE_API_FILES_URL,
                headers={"Authorization": f"Bearer {access_token}"},
                params={"q": query, "fields": "files(id, name, mimeType, webViewLink, modifiedTime)"},
            )
            res.raise_for_status()
            data = res.json()
            return data.get("files", [])
    except Exception as e:
        logger.error(f"Failed to list Google Drive files: {e}")
        return []


async def get_sheet_tabs(spreadsheet_id_or_url: str, access_token: str) -> List[str]:
    """Fetch worksheet tab names (e.g. Sheet1, Leads) from a Google Spreadsheet file."""
    spreadsheet_id = extract_spreadsheet_id(spreadsheet_id_or_url)
    if not spreadsheet_id:
        return []

    url = f"{GOOGLE_SHEETS_API_URL}/{spreadsheet_id}?fields=sheets.properties.title"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.get(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            res.raise_for_status()
            data = res.json()
            sheets = data.get("sheets", [])
            return [s.get("properties", {}).get("title", "Sheet1") for s in sheets]
    except Exception as e:
        logger.error(f"Failed to fetch spreadsheet tabs: {e}")
        return ["Sheet1"]


async def get_sheet_header_columns(
    spreadsheet_id_or_url: str,
    sheet_name: str,
    access_token: str,
) -> List[str]:
    """Fetch the header row (Row 1) column names from a worksheet tab."""
    spreadsheet_id = extract_spreadsheet_id(spreadsheet_id_or_url)
    if not spreadsheet_id:
        return []

    range_name = f"{sheet_name}!1:1" if sheet_name else "1:1"
    url = f"{GOOGLE_SHEETS_API_URL}/{spreadsheet_id}/values/{range_name}"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.get(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            res.raise_for_status()
            data = res.json()
            values = data.get("values", [])
            if values and len(values) > 0:
                return [str(col).strip() for col in values[0] if str(col).strip()]
            return []
    except Exception as e:
        logger.error(f"Failed to fetch sheet header columns: {e}")
        return []


async def append_row_to_drive_sheet(
    spreadsheet_id_or_url: str,
    sheet_name: str,
    row_values: List[Any],
    access_token: str,
) -> bool:
    """Append a row of post-call data to the mounted Google Sheet using Google Sheets API v4."""
    spreadsheet_id = extract_spreadsheet_id(spreadsheet_id_or_url)
    if not spreadsheet_id:
        logger.error("Invalid spreadsheet ID or URL provided")
        return False

    range_name = f"{sheet_name}!A1" if sheet_name else "A1"
    url = f"{GOOGLE_SHEETS_API_URL}/{spreadsheet_id}/values/{range_name}:append?valueInputOption=USER_ENTERED"

    logger.info(f"Appending row to mounted Google Sheet (ID: {spreadsheet_id}, Tab: {sheet_name})")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json={"values": [row_values]},
            )
            res.raise_for_status()
            logger.info(f"Successfully appended row to Google Sheet: HTTP {res.status_code}")
            return True
    except Exception as e:
        logger.error(f"Failed to append row to Google Sheet: {e}")
        return False
