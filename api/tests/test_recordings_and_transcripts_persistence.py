from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from api.services.reports.run_report import (
    _ensure_tokens_for_report_runs,
    build_run_report_csv,
)
from api.tasks.run_integrations import _build_render_context


class MockWorkflowRun:
    def __init__(self, run_id=1, public_token="test-uuid-123"):
        self.id = run_id
        self.name = "Test Call Run"
        self.workflow_id = 10
        self.workflow = MagicMock(name="Test Workflow")
        self.workflow.name = "Test Workflow"
        self.campaign_id = None
        self.created_at = datetime.now(UTC)
        self.initial_context = {"phone_number": "+1234567890"}
        self.gathered_context = {
            "mapped_call_disposition": "completed",
            "extracted_variables": {"customer_intent": "billing"},
        }
        self.cost_info = {"call_duration_seconds": 45}
        self.usage_info = {}
        self.annotations = {}
        self.recording_url = "recordings/1.wav"
        self.transcript_url = "transcripts/1.txt"
        self.public_access_token = public_token
        self.logs = {
            "events": [
                {
                    "type": "rtf-user-transcription",
                    "payload": {"text": "Hello world", "final": True, "timestamp": "12:00:00"},
                },
                {
                    "type": "rtf-bot-text",
                    "payload": {"text": "Hi, how can I help?", "timestamp": "12:00:02"},
                },
            ]
        }


def test_build_render_context_includes_urls_and_transcript_text():
    run = MockWorkflowRun(run_id=42, public_token="token-abc")
    context = _build_render_context(run, public_token="token-abc")

    assert context["workflow_run_id"] == 42
    assert "token-abc/recording" in context["recording_url"]
    assert "token-abc/transcript" in context["transcript_url"]
    assert "user: Hello world" in context["transcript_text"]
    assert "assistant: Hi, how can I help?" in context["transcript_text"]


@pytest.mark.asyncio
async def test_ensure_tokens_for_report_runs():
    from api.db import db_client

    run_without_token = MockWorkflowRun(run_id=99, public_token=None)

    with patch.object(
        db_client,
        "ensure_public_access_token",
        new=AsyncMock(return_value="generated-token-999"),
    ):
        ensured = await _ensure_tokens_for_report_runs([run_without_token])

    assert len(ensured) == 1
    assert ensured[0]["public_access_token"] == "generated-token-999"


def test_build_run_report_csv_contains_public_urls():
    run = MockWorkflowRun(run_id=5, public_token="token-xyz-123")

    csv_output = build_run_report_csv([run])
    content = csv_output.getvalue()

    assert "Transcript URL" in content
    assert "Recording URL" in content
    assert "token-xyz-123/transcript" in content
    assert "token-xyz-123/recording" in content
