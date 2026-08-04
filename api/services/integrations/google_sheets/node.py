from __future__ import annotations

from typing import Any
from pydantic import model_validator

from api.services.integrations.base import IntegrationNodeRegistration
from api.services.workflow.node_data import BaseNodeData
from api.services.workflow.node_specs._base import (
    GraphConstraints,
    NodeCategory,
    NodeExample,
    PropertyType,
)
from api.services.workflow.node_specs.model_spec import (
    build_spec,
    node_spec,
    spec_field,
)

DEFAULT_COLUMN_MAPPINGS = [
    {"column_name": "Call Time", "value_template": "{{call_time}}"},
    {"column_name": "Phone Number", "value_template": "{{initial_context.phone_number}}"},
    {"column_name": "Customer Name", "value_template": "{{gathered_context.customer_name}}"},
    {"column_name": "Call Summary", "value_template": "{{gathered_context.summary}}"},
    {"column_name": "Call Disposition", "value_template": "{{gathered_context.call_disposition}}"},
    {"column_name": "Duration (s)", "value_template": "{{cost_info.call_duration_seconds}}"},
    {"column_name": "Recording URL", "value_template": "{{recording_url}}"},
    {"column_name": "Transcript URL", "value_template": "{{transcript_url}}"},
]


@node_spec(
    name="google_sheets",
    display_name="Google Sheets",
    description="Mount Google Drive and automatically save post-call summaries, customer context, and recordings directly to Google Sheets or Excel",
    llm_hint=(
        "Google Sheets is a post-call export node. It does not participate in the "
        "live conversation graph and should not be connected to audio nodes."
    ),
    category=NodeCategory.integration,
    icon="Table",
    examples=[
        NodeExample(
            name="google_sheets_export",
            data={
                "name": "Google Sheets Export",
                "google_sheets_enabled": True,
                "auth_mode": "google_drive",
                "spreadsheet_id_or_url": "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlb74OgvE2upmsw/edit",
                "sheet_name": "Sheet1",
                "column_mappings": DEFAULT_COLUMN_MAPPINGS,
            },
        )
    ],
    graph_constraints=GraphConstraints(
        min_incoming=0,
        max_incoming=0,
        min_outgoing=0,
        max_outgoing=0,
    ),
    property_order=(
        "name",
        "google_sheets_enabled",
        "auth_mode",
        "credential_uuid",
        "spreadsheet_id_or_url",
        "sheet_name",
        "column_mappings",
    ),
    field_overrides={
        "name": {
            "spec_default": "Google Sheets Export",
            "description": "Short identifier for this Google Sheets integration node.",
        },
        "google_sheets_enabled": {
            "display_name": "Enabled",
            "description": "When false, AZS Solution's AI Agent skips exporting post-call data to Google Sheets.",
        },
        "auth_mode": {
            "display_name": "Authentication Mode",
            "description": "Choose 'google_drive' for mounted 1-click Google Drive connection.",
            "spec_default": "google_drive",
        },
        "credential_uuid": {
            "display_name": "Connected Google Drive Account",
            "description": "UUID of your mounted Google Drive credential in AZS Solution's AI Agent.",
        },
        "spreadsheet_id_or_url": {
            "display_name": "Spreadsheet ID or URL",
            "description": "Select or paste your Google Sheets / Excel document URL from Google Drive.",
        },
        "sheet_name": {
            "display_name": "Sheet Name",
            "description": "Name of the target worksheet tab (e.g. Sheet1 or Calls Log).",
            "spec_default": "Sheet1",
        },
        "column_mappings": {
            "display_name": "Column Mappings",
            "description": "List of columns and template fields to save on call completion.",
        },
    },
)
class GoogleSheetsNodeData(BaseNodeData):
    google_sheets_enabled: bool = spec_field(
        default=True,
        ui_type=PropertyType.boolean,
        display_name="Enabled",
        description="When false, AZS Solution's AI Agent skips exporting post-call data.",
    )
    auth_mode: str = spec_field(
        default="google_drive",
        ui_type=PropertyType.string,
        display_name="Authentication Mode",
        description="Authentication mode: 'google_drive'.",
    )
    credential_uuid: str | None = spec_field(
        default=None,
        ui_type=PropertyType.string,
        display_name="Connected Google Drive Account",
        description="Credential reference for mounted Google Drive.",
    )
    spreadsheet_id_or_url: str | None = spec_field(
        default=None,
        ui_type=PropertyType.string,
        display_name="Spreadsheet ID or URL",
        description="Google Spreadsheet ID or full Google Drive URL.",
    )
    sheet_name: str = spec_field(
        default="Sheet1",
        ui_type=PropertyType.string,
        display_name="Sheet Name",
        description="Target tab name in Google Sheets.",
    )
    column_mappings: list[dict[str, Any]] | None = spec_field(
        default=None,
        ui_type=PropertyType.json,
        display_name="Column Mappings",
        description="List of column name and template value dictionaries.",
    )

    @model_validator(mode="after")
    def _validate_config(self):
        if not self.google_sheets_enabled:
            return self

        if not self.spreadsheet_id_or_url or not self.spreadsheet_id_or_url.strip():
            raise ValueError(
                "Google Sheets node requires a 'spreadsheet_id_or_url' (Google Drive link or ID)."
            )

        return self


SPEC = build_spec(GoogleSheetsNodeData)

NODE = IntegrationNodeRegistration(
    type_name="google_sheets",
    data_model=GoogleSheetsNodeData,
    node_spec=SPEC,
    sensitive_fields=(),
)
