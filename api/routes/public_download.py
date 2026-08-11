import os
import tempfile
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import FileResponse, RedirectResponse
from loguru import logger

from api.db import db_client
from api.services.storage import get_storage_for_backend
from api.utils.transcript import generate_transcript_text

router = APIRouter(prefix="/public/download")


async def _handle_artifact_download(
    token: str,
    artifact_type: str,
    inline: bool = True,
) -> Response:
    """Core handler for resolving workflow run artifacts and streaming them directly."""
    token = token.strip()
    artifact_type = artifact_type.lower().strip()

    if artifact_type not in ["recording", "transcript"]:
        artifact_type = "recording"

    logger.info(f"Processing public download request: token='{token}', artifact_type='{artifact_type}', inline={inline}")

    # 1. Lookup workflow run by token UUID, or numeric run ID fallback
    workflow_run = await db_client.get_workflow_run_by_public_token(token)
    if not workflow_run and token.isdigit():
        workflow_run, _ = await db_client.get_workflow_run_with_context(int(token))

    if not workflow_run:
        logger.warning(f"Workflow run not found for token: '{token}'")
        raise HTTPException(
            status_code=404,
            detail=f"Workflow run not found for public token: {token}",
        )

    # Ensure token exists on workflow_run object
    if not workflow_run.public_access_token:
        try:
            await db_client.ensure_public_access_token(workflow_run.id)
        except Exception as e:
            logger.warning(f"Failed to ensure public token for run {workflow_run.id}: {e}")

    # 2. For transcripts: first check logged speech events in database (100% reliable)
    if artifact_type == "transcript":
        logs = workflow_run.logs if isinstance(workflow_run.logs, dict) else {}
        events = logs.get("events", []) if isinstance(logs.get("events"), list) else []
        transcript_text = generate_transcript_text(events)

        if transcript_text and transcript_text.strip():
            disposition = "inline" if inline else f'attachment; filename="transcript_{workflow_run.id}.txt"'
            return Response(
                content=transcript_text,
                media_type="text/plain; charset=utf-8",
                headers={"Content-Disposition": disposition},
            )

    # 3. Determine file path in storage
    if artifact_type == "recording":
        file_path = workflow_run.recording_url or f"recordings/{workflow_run.id}.wav"
    else:
        file_path = workflow_run.transcript_url or f"transcripts/{workflow_run.id}.txt"

    # 4. Get storage backend
    try:
        storage = get_storage_for_backend(workflow_run.storage_backend)
    except Exception as e:
        logger.error(f"Error resolving storage backend '{workflow_run.storage_backend}': {e}")
        # Fallback to default storage filesystem
        from api.services.storage import storage_fs
        storage = storage_fs

    # 5. Attempt direct file download & stream
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
        logger.warning(f"Direct storage download failed for {artifact_type} ({file_path}): {e}")

    # 6. Fallback to signed URL redirect if available
    try:
        signed_url = await storage.aget_signed_url(
            file_path=file_path,
            expiration=3600,
            force_inline=inline,
        )
        if signed_url:
            return RedirectResponse(url=signed_url, status_code=302)
    except Exception as e:
        logger.error(f"Signed URL generation failed for {file_path}: {e}")

    # 7. Explicit detail error if file is missing
    detail_msg = (
        f"Audio recording is not available for call run {workflow_run.id}."
        if artifact_type == "recording"
        else f"Transcript is not available for call run {workflow_run.id}."
    )
    raise HTTPException(status_code=404, detail=detail_msg)


@router.get("/workflow/{token}/{artifact_type}")
@router.get("/workflow/{token}/{artifact_type}/")
async def download_workflow_artifact(
    token: str,
    artifact_type: str,
    inline: bool = Query(default=True),
):
    """Download workflow artifact via /workflow/{token}/{artifact_type}."""
    return await _handle_artifact_download(token=token, artifact_type=artifact_type, inline=inline)


@router.get("/workflow/{token}")
@router.get("/workflow/{token}/")
async def download_workflow_default(
    token: str,
    inline: bool = Query(default=True),
):
    """Fallback route for /workflow/{token} defaulting to recording."""
    return await _handle_artifact_download(token=token, artifact_type="recording", inline=inline)


@router.get("/recording/{token}")
@router.get("/recording/{token}/")
async def download_recording_alias(
    token: str,
    inline: bool = Query(default=True),
):
    """Alias route for /recording/{token}."""
    return await _handle_artifact_download(token=token, artifact_type="recording", inline=inline)


@router.get("/transcript/{token}")
@router.get("/transcript/{token}/")
async def download_transcript_alias(
    token: str,
    inline: bool = Query(default=True),
):
    """Alias route for /transcript/{token}."""
    return await _handle_artifact_download(token=token, artifact_type="transcript", inline=inline)

