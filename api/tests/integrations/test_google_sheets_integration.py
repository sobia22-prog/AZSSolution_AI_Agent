import pytest
from unittest.mock import AsyncMock, patch
from pydantic import ValidationError

from api.services.integrations.google_sheets.client import (
    extract_spreadsheet_id,
    get_google_drive_auth_url,
)
from api.services.integrations.google_sheets.node import (
    DEFAULT_COLUMN_MAPPINGS,
    GoogleSheetsNodeData,
)
from api.services.integrations.google_sheets.completion import run_completion
from api.services.integrations.base import IntegrationCompletionContext
from api.services.integrations.registry import (
    all_node_specs,
    all_routers,
    get_node_data_model,
    get_node_registration,
    get_node_spec,
)


def test_extract_spreadsheet_id():
    url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlb74OgvE2upmsw/edit#gid=0"
    raw_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlb74OgvE2upmsw"
    
    assert extract_spreadsheet_id(url) == raw_id
    assert extract_spreadsheet_id(raw_id) == raw_id
    assert extract_spreadsheet_id("") == ""


def test_get_google_drive_auth_url():
    url = get_google_drive_auth_url(
        client_id="test-client-id",
        redirect_uri="http://localhost:3000/callback",
        state="org_1",
    )
    assert "https://accounts.google.com/o/oauth2/v2/auth" in url
    assert "client_id=test-client-id" in url
    assert "response_type=code" in url
    assert "scope=" in url


def test_google_sheets_node_data_validation():
    # Valid Google Drive mount config
    valid_node = GoogleSheetsNodeData(
        name="AZS Google Sheets Export",
        google_sheets_enabled=True,
        auth_mode="google_drive",
        spreadsheet_id_or_url="https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlb74OgvE2upmsw/edit",
        sheet_name="Sheet1",
    )
    assert valid_node.auth_mode == "google_drive"

    # Missing spreadsheet link should fail when enabled
    with pytest.raises(ValidationError):
        GoogleSheetsNodeData(
            name="Invalid Node",
            google_sheets_enabled=True,
            auth_mode="google_drive",
            spreadsheet_id_or_url="",
        )

    # Disabled node doesn't enforce spreadsheet requirement
    disabled_node = GoogleSheetsNodeData(
        name="Disabled Node",
        google_sheets_enabled=False,
        auth_mode="google_drive",
    )
    assert disabled_node.google_sheets_enabled is False


def test_google_sheets_registry_integration():
    reg = get_node_registration("google_sheets")
    assert reg is not None
    assert reg.type_name == "google_sheets"
    assert reg.data_model == GoogleSheetsNodeData

    spec = get_node_spec("google_sheets")
    assert spec is not None
    assert spec.name == "google_sheets"
    assert spec.display_name == "Google Sheets"

    model = get_node_data_model("google_sheets")
    assert model == GoogleSheetsNodeData

    all_specs = all_node_specs()
    spec_names = [s.name for s in all_specs]
    assert "google_sheets" in spec_names

    routers = all_routers()
    assert len(routers) > 0


@pytest.mark.asyncio
async def test_google_sheets_completion_google_drive():
    mock_run = AsyncMock()
    mock_run.id = 101
    mock_run.name = "Test Call Run"
    mock_run.workflow_id = 5
    mock_run.workflow.name = "AZS AI Agent Workflow"
    mock_run.campaign_id = None
    mock_run.created_at = None
    mock_run.initial_context = {"phone_number": "+19876543210"}
    mock_run.gathered_context = {
        "customer_name": "Bob Johnson",
        "summary": "Customer confirmed booking for Friday at 10 AM.",
        "call_disposition": "completed",
    }
    mock_run.usage_info = {"call_duration_seconds": 62.0}
    mock_run.annotations = {}
    mock_run.recording_url = "https://example.com/recording.mp3"
    mock_run.transcript_url = "https://example.com/transcript.txt"

    ctx = IntegrationCompletionContext(
        workflow_run_id=101,
        workflow_run=mock_run,
        workflow_definition={"nodes": []},
        definition_id=1,
        organization_id=1,
        public_token="azs-public-token",
    )

    node_dict = {
        "id": "gs_node_1",
        "type": "google_sheets",
        "data": {
            "name": "Google Sheets Export",
            "google_sheets_enabled": True,
            "auth_mode": "google_drive",
            "spreadsheet_id_or_url": "https://docs.google.com/spreadsheets/d/12345/edit",
            "sheet_name": "Sheet1",
            "column_mappings": DEFAULT_COLUMN_MAPPINGS,
        },
    }

    with patch(
        "api.services.integrations.google_sheets.completion._resolve_access_token",
        new_callable=AsyncMock,
        return_value=("mock-access-token", None),
    ), patch(
        "api.services.integrations.google_sheets.completion.append_row_to_drive_sheet",
        new_callable=AsyncMock,
        return_value=True,
    ) as mock_append:
        results = await run_completion([node_dict], ctx)

        assert "google_sheets_gs_node_1" in results
        res = results["google_sheets_gs_node_1"]
        assert res["success"] is True
        assert res["mode"] == "google_drive"
        assert res["exported_columns"] == 8

        mock_append.assert_called_once()
        args, kwargs = mock_append.call_args
        row_values = kwargs["row_values"]
        assert "+19876543210" in row_values
        assert "Bob Johnson" in row_values
        assert "Customer confirmed booking for Friday at 10 AM." in row_values


@pytest.mark.asyncio
async def test_google_sheets_completion_disabled_node():
    mock_run = AsyncMock()
    mock_run.id = 102
    mock_run.workflow_id = 5
    mock_run.workflow.name = "AZS AI Agent Workflow"
    mock_run.campaign_id = None
    mock_run.created_at = None
    mock_run.initial_context = {}
    mock_run.gathered_context = {}
    mock_run.usage_info = {}
    mock_run.annotations = {}
    mock_run.recording_url = None
    mock_run.transcript_url = None

    ctx = IntegrationCompletionContext(
        workflow_run_id=102,
        workflow_run=mock_run,
        workflow_definition={"nodes": []},
        definition_id=1,
        organization_id=1,
        public_token=None,
    )

    node_dict = {
        "id": "gs_node_2",
        "type": "google_sheets",
        "data": {
            "name": "Disabled Node",
            "google_sheets_enabled": False,
            "auth_mode": "google_drive",
            "spreadsheet_id_or_url": "12345",
        },
    }

    results = await run_completion([node_dict], ctx)
    assert results == {}
