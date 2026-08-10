import os
import tempfile
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import FileResponse, RedirectResponse
from loguru import logger

from api.db import db_client
from api.services.storage import get_storage_for_backend
from api.utils.transcript import generate_transcript_text

router = APIRouter(prefix="/public/download")


@router.get("/workflow/{token}/{artifact_type}")
async def download_workflow_artifact(
    token: str,
    artifact_type: Literal["recording", "transcript"],
    inline: bool = Query(
        default=True, description="Display inline in browser instead of download"
    ),
):
    """Download or stream a workflow recording or transcript via public access token.

    This endpoint:
    1. Validates the public access token (or numeric run ID fallback)
    2. Looks up the corresponding workflow run
    3. Serves the transcript text or streams the audio file directly
    4. Falls back to signed URL redirect if direct stream fails

    Args:
        token: The public access token (UUID format) or numeric run ID
        artifact_type: Type of artifact - "recording" or "transcript"
        inline: If true, sets Content-Disposition to inline for browser preview

    Returns:
        Response, FileResponse, or RedirectResponse
    """
    # 1. Lookup workflow run by token, or fallback to numeric ID
    workflow_run = await db_client.get_workflow_run_by_public_token(token)
    if not workflow_run and token.isdigit():
        workflow_run, _ = await db_client.get_workflow_run_with_context(int(token))

    if not workflow_run:
        logger.warning(f"Invalid public access token or run ID: {token[:8]}...")
        raise HTTPException(status_code=404, detail="Invalid or expired token")

    # 2. For transcripts, serve directly from logged events if available
    if artifact_type == "transcript":
        logs = workflow_run.logs if isinstance(workflow_run.logs, dict) else {}
        events = logs.get("events", []) if isinstance(logs.get("events"), list) else []
        transcript_text = generate_transcript_text(events)

        if transcript_text:
            disposition = "inline" if inline else f'attachment; filename="transcript_{workflow_run.id}.txt"'
            return Response(
                content=transcript_text,
                media_type="text/plain; charset=utf-8",
                headers={"Content-Disposition": disposition},
            )

    # 3. Get file path based on artifact type with fallback to standard artifact paths
    if artifact_type == "recording":
        file_path = workflow_run.recording_url or f"recordings/{workflow_run.id}.wav"
    else:  # transcript
        file_path = workflow_run.transcript_url or f"transcripts/{workflow_run.id}.txt"

    # 4. Get storage backend for this workflow run
    try:
        storage = get_storage_for_backend(workflow_run.storage_backend)
    except ValueError as e:
        logger.error(f"Invalid storage backend: {workflow_run.storage_backend}")
        raise HTTPException(status_code=500, detail="Storage configuration error")

    # 5. Attempt direct file download and response (bypassing external endpoint redirects)
    try:
        temp_dir = tempfile.gettempdir()
        ext = "wav" if artifact_type == "recording" else "txt"
        local_file = os.path.join(temp_dir, f"public_{workflow_run.id}_{artifact_type}.{ext}")
        
        success = await storage.adownload_file(file_path, local_file)
        if success and os.path.exists(local_file) and os.path.getsize(local_file) > 0:
            media_type = "audio/wav" if artifact_type == "recording" else "text/plain; charset=utf-8"
            filename = f"{artifact_type}_{workflow_run.id}.{ext}"
            return FileResponse(
                path=local_file,
                media_type=media_type,
                filename=filename,
                content_disposition_type="inline" if inline else "attachment",
            )
    except Exception as e:
        logger.warning(f"Direct file download failed for {artifact_type} ({file_path}): {e}")

    # 6. Fallback to signed URL redirect (1 hour expiration)
    try:
        signed_url = await storage.aget_signed_url(
            file_path=file_path,
            expiration=3600,
            force_inline=inline,
        )
        if signed_url:
            return RedirectResponse(url=signed_url, status_code=302)
    except Exception as e:
        logger.error(f"Failed to generate signed URL: {e}")

    raise HTTPException(
        status_code=404,
        detail=f"{artifact_type.capitalize()} is currently unavailable for this run",
    )
