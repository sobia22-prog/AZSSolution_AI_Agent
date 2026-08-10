"""CSV reports built from completed workflow runs.

Shared by campaign-, workflow-, and organization-usage-scoped reports.
The DB client supplies the row set; this module owns the column layout
so every endpoint emits the same shape.
"""

import csv
import io
from datetime import UTC, datetime
from typing import Any, List, Optional

from api.db import db_client
from api.utils.artifacts import artifact_url


def _get_attr(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _collect_extracted_variable_keys(runs: List[Any]) -> list[str]:
    """Collect all unique extracted variable keys across runs, preserving insertion order."""
    keys: dict[str, None] = {}
    for run in runs:
        gathered = _get_attr(run, "gathered_context") or {}
        extracted = gathered.get("extracted_variables", {})
        if isinstance(extracted, dict):
            for key in extracted:
                keys.setdefault(key, None)
    return list(keys)


async def _ensure_tokens_for_report_runs(runs: List[Any]) -> List[Any]:
    """Ensure every run has a public_access_token generated before building CSV."""
    ensured_runs = []
    for run in runs:
        token = _get_attr(run, "public_access_token")
        run_id = _get_attr(run, "id")
        if not token and run_id:
            try:
                token = await db_client.ensure_public_access_token(run_id)
            except Exception:
                token = None

        if isinstance(run, dict):
            run_dict = dict(run)
            run_dict["public_access_token"] = token
            ensured_runs.append(run_dict)
        else:
            # For Row / tuple / object instances, convert to dict with override
            ensured_runs.append({
                "id": _get_attr(run, "id"),
                "campaign_id": _get_attr(run, "campaign_id"),
                "workflow_id": _get_attr(run, "workflow_id"),
                "definition_id": _get_attr(run, "definition_id"),
                "created_at": _get_attr(run, "created_at"),
                "initial_context": _get_attr(run, "initial_context"),
                "gathered_context": _get_attr(run, "gathered_context"),
                "cost_info": _get_attr(run, "cost_info"),
                "public_access_token": token,
            })
    return ensured_runs


def build_run_report_csv(runs: List[Any]) -> io.StringIO:
    """Build a CSV from completed workflow runs."""
    extracted_var_keys = _collect_extracted_variable_keys(runs)

    output = io.StringIO()
    writer = csv.writer(output)

    pre_headers = [
        "Run ID",
        "Campaign ID",
        "Agent ID",
        "Agent Definition ID",
        "Created At",
        "Phone Number",
        "Call Disposition",
        "Call Duration (s)",
    ]
    post_headers = [
        "Call Tags",
        "Transcript URL",
        "Recording URL",
    ]
    writer.writerow(pre_headers + extracted_var_keys + post_headers)

    for run in runs:
        initial = _get_attr(run, "initial_context") or {}
        gathered = _get_attr(run, "gathered_context") or {}
        cost = _get_attr(run, "cost_info") or {}
        run_id = _get_attr(run, "id", "")
        campaign_id = _get_attr(run, "campaign_id")
        workflow_id = _get_attr(run, "workflow_id", "")
        definition_id = _get_attr(run, "definition_id")
        created_at = _get_attr(run, "created_at")
        token = _get_attr(run, "public_access_token")

        call_tags = gathered.get("call_tags", [])
        if isinstance(call_tags, list):
            call_tags = ", ".join(str(t) for t in call_tags)

        pre_values = [
            run_id,
            campaign_id if campaign_id is not None else "",
            workflow_id,
            definition_id if definition_id is not None else "",
            created_at.isoformat() if created_at else "",
            initial.get("phone_number", ""),
            gathered.get("mapped_call_disposition", ""),
            cost.get("call_duration_seconds", ""),
        ]

        extracted = gathered.get("extracted_variables", {})
        if not isinstance(extracted, dict):
            extracted = {}
        extracted_values = [extracted.get(key, "") for key in extracted_var_keys]

        post_values = [
            call_tags,
            artifact_url(token, "transcript") or "",
            artifact_url(token, "recording") or "",
        ]

        writer.writerow(pre_values + extracted_values + post_values)

    output.seek(0)
    return output


async def generate_campaign_report_csv(
    campaign_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> tuple[io.StringIO, str]:
    """Generate a CSV report for a campaign."""
    runs = await db_client.get_completed_runs_for_report(
        campaign_id=campaign_id, start_date=start_date, end_date=end_date
    )
    ensured_runs = await _ensure_tokens_for_report_runs(runs)
    return build_run_report_csv(ensured_runs), f"campaign_{campaign_id}_report.csv"


async def generate_workflow_report_csv(
    workflow_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> tuple[io.StringIO, str]:
    """Generate a CSV report for all completed runs of a workflow."""
    runs = await db_client.get_completed_runs_for_report(
        workflow_id=workflow_id, start_date=start_date, end_date=end_date
    )
    ensured_runs = await _ensure_tokens_for_report_runs(runs)
    return build_run_report_csv(ensured_runs), f"workflow_{workflow_id}_report.csv"


async def generate_usage_runs_report_csv(
    organization_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    filters: Optional[list[dict]] = None,
) -> tuple[io.StringIO, str]:
    """Generate a CSV report for runs visible on the org-wide usage page.

    Honors the same date / filter inputs as the `/usage/runs` listing.
    """
    runs = await db_client.get_usage_runs_for_report(
        organization_id,
        start_date=start_date,
        end_date=end_date,
        filters=filters,
    )
    ensured_runs = await _ensure_tokens_for_report_runs(runs)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    return build_run_report_csv(ensured_runs), f"usage_runs_{timestamp}.csv"

