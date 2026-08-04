from __future__ import annotations

import os
from datetime import datetime, UTC
from typing import Any, Dict
from loguru import logger
from pydantic import ValidationError

from api.db import db_client
from api.services.integrations.base import IntegrationCompletionContext
from api.services.integrations.google_sheets.client import (
    append_row_to_drive_sheet,
    refresh_google_oauth_token,
)
from api.services.integrations.google_sheets.node import (
    DEFAULT_COLUMN_MAPPINGS,
    GoogleSheetsNodeData,
)
from api.tasks.run_integrations import _build_render_context
from api.utils.template_renderer import render_template


async def _resolve_access_token(
    credential_uuid: str | None,
    organization_id: int,
) -> tuple[str | None, str | None]:
    """Retrieve mounted Google Drive credentials for the organization and refresh access token."""
    try:
        credential = None
        if credential_uuid:
            credential = await db_client.get_credential_by_uuid(credential_uuid, organization_id)
        
        if not credential:
            # Fallback: look up any active credential containing a refresh token for this org
            org_credentials = await db_client.get_credentials_for_organization(organization_id)
            for c in org_credentials:
                if c.credential_data and "refresh_token" in c.credential_data:
                    credential = c
                    break

        if not credential or not credential.credential_data:
            return None, "No mounted Google Drive account found for organization"

        cred_data = credential.credential_data
        refresh_token = cred_data.get("refresh_token")
        client_id = cred_data.get("client_id") or os.getenv("GOOGLE_CLIENT_ID", "")
        client_secret = cred_data.get("client_secret") or os.getenv("GOOGLE_CLIENT_SECRET", "")

        if not refresh_token:
            return None, "Mounted credential missing refresh token"

        access_token = await refresh_google_oauth_token(refresh_token, client_id, client_secret)
        if not access_token:
            return None, "Failed to refresh Google Drive OAuth access token"

        return access_token, None
    except Exception as e:
        logger.error(f"Error resolving Google Drive access token: {e}")
        return None, str(e)


async def run_completion(
    nodes: list[dict],
    context: IntegrationCompletionContext,
) -> Dict[str, Any]:
    """Execute Google Sheets post-call export for each configured Google Sheets node in AZS Solution's AI Agent."""
    results: Dict[str, Any] = {}
    workflow_run = context.workflow_run

    if not workflow_run:
        logger.warning("No workflow_run provided in IntegrationCompletionContext")
        return results

    # Build render context for variable rendering
    render_ctx = _build_render_context(workflow_run, context.public_token)

    for node in nodes:
        node_id = node.get("id", "unknown")
        raw_data = node.get("data", {})

        try:
            gs_data = GoogleSheetsNodeData.model_validate(raw_data)
        except ValidationError as e:
            logger.warning(f"Google Sheets node #{node_id} failed validation: {e}")
            results[f"google_sheets_{node_id}"] = {"error": "validation_failed", "details": str(e)}
            continue

        if not gs_data.google_sheets_enabled:
            logger.debug(f"Google Sheets node '{gs_data.name}' (#{node_id}) is disabled, skipping")
            continue

        column_mappings = gs_data.column_mappings or DEFAULT_COLUMN_MAPPINGS

        # Render template variables for each column
        row_dict: Dict[str, Any] = {}
        row_values: list[Any] = []

        for mapping in column_mappings:
            col_name = mapping.get("column_name", "Field")
            template_val = mapping.get("value_template", "")
            rendered_val = render_template(template_val, render_ctx)
            row_dict[col_name] = rendered_val
            row_values.append(rendered_val)

        access_token, err = await _resolve_access_token(
            credential_uuid=gs_data.credential_uuid,
            organization_id=context.organization_id,
        )

        if not access_token:
            logger.warning(f"Google Sheets export skipped for node '{gs_data.name}' (#{node_id}): {err}")
            results[f"google_sheets_{node_id}"] = {"success": False, "error": err}
            continue

        logger.info(f"Executing Google Sheets export for node '{gs_data.name}' (#{node_id}) using mounted Google Drive connection")

        success = await append_row_to_drive_sheet(
            spreadsheet_id_or_url=gs_data.spreadsheet_id_or_url,
            sheet_name=gs_data.sheet_name,
            row_values=row_values,
            access_token=access_token,
        )

        results[f"google_sheets_{node_id}"] = {
            "success": success,
            "mode": "google_drive",
            "exported_columns": len(row_values),
            "executed_at": datetime.now(UTC).isoformat(),
        }

    return results
