"""Validation helpers for the AI platform governance evidence inventory.

The inventory deliberately distinguishes a verified observation from a complete
control assessment. A failed API read or a vendor announcement must never be
interpreted as proof that an organization setting is enabled or disabled.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

ALLOWED_STATUSES = {
    "verified",
    "partial",
    "announcement_only",
    "needs_admin_verification",
    "needs_account_owner_verification",
    "blocked",
    "not_applicable",
}
ALLOWED_VERIFICATION_MODES = {"api", "repository_file", "admin_manual", "mixed"}
ALLOWED_EVIDENCE_TYPES = {
    "github_api",
    "repository_file",
    "admin_export",
    "announcement",
    "api_error",
}
VERIFIABLE_EVIDENCE_TYPES = {"github_api", "repository_file", "admin_export"}
REQUIRED_CONTROL_FIELDS = {
    "id",
    "name",
    "scopes",
    "owner_role",
    "verification_mode",
    "status",
    "finding",
    "evidence",
    "next_action",
    "review_due",
}


class InventoryError(ValueError):
    """Raised when an inventory file cannot be loaded or is invalid."""


def _is_iso_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _declared_scopes(data: dict[str, Any]) -> set[str]:
    scope = data.get("scope", {})
    if not isinstance(scope, dict):
        return set()
    organizations = scope.get("organizations", [])
    user_accounts = scope.get("user_accounts", [])
    repositories = scope.get("repositories", [])
    if (
        not isinstance(organizations, list)
        or not isinstance(user_accounts, list)
        or not isinstance(repositories, list)
    ):
        return set()
    return {
        *(f"organization:{organization}" for organization in organizations),
        *(f"user_account:{account}" for account in user_accounts),
        *(f"repository:{repository}" for repository in repositories),
    }


def validate_inventory(data: dict[str, Any]) -> list[str]:
    """Return all validation errors found in an inventory document."""
    errors: list[str] = []

    if data.get("schema_version") != "1.0.0":
        errors.append("schema_version must be '1.0.0'")
    if not _is_iso_date(data.get("as_of")):
        errors.append("as_of must be an ISO date")

    declared_scopes = _declared_scopes(data)
    if not declared_scopes:
        errors.append("scope must declare at least one organization or repository")

    controls = data.get("controls")
    if not isinstance(controls, list) or not controls:
        errors.append("controls must be a non-empty list")
        return errors

    seen_ids: set[str] = set()
    for index, control in enumerate(controls):
        prefix = f"controls[{index}]"
        if not isinstance(control, dict):
            errors.append(f"{prefix} must be an object")
            continue

        missing = sorted(REQUIRED_CONTROL_FIELDS - control.keys())
        if missing:
            errors.append(f"{prefix} missing fields: {', '.join(missing)}")
            continue

        control_id = control["id"]
        if not isinstance(control_id, str) or not control_id:
            errors.append(f"{prefix}.id must be a non-empty string")
        elif control_id in seen_ids:
            errors.append(f"duplicate control id: {control_id}")
        else:
            seen_ids.add(control_id)

        status = control["status"]
        if status not in ALLOWED_STATUSES:
            errors.append(f"{prefix}.status is invalid: {status}")

        verification_mode = control["verification_mode"]
        if verification_mode not in ALLOWED_VERIFICATION_MODES:
            errors.append(f"{prefix}.verification_mode is invalid: {verification_mode}")

        scopes = control["scopes"]
        if not isinstance(scopes, list) or not scopes:
            errors.append(f"{prefix}.scopes must be a non-empty list")
        else:
            undeclared = sorted(set(scopes) - declared_scopes)
            if undeclared:
                errors.append(f"{prefix}.scopes are undeclared: {', '.join(undeclared)}")

        if not isinstance(control["owner_role"], str) or not control["owner_role"]:
            errors.append(f"{prefix}.owner_role must be a non-empty string")
        if not isinstance(control["finding"], str) or not control["finding"]:
            errors.append(f"{prefix}.finding must be a non-empty string")
        if not _is_iso_date(control["review_due"]):
            errors.append(f"{prefix}.review_due must be an ISO date")

        evidence = control["evidence"]
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{prefix}.evidence must be a non-empty list")
            evidence_types: set[str] = set()
        else:
            evidence_types = set()
            for evidence_index, item in enumerate(evidence):
                item_prefix = f"{prefix}.evidence[{evidence_index}]"
                if not isinstance(item, dict):
                    errors.append(f"{item_prefix} must be an object")
                    continue
                required = {"type", "source", "observed_at", "result"}
                missing_evidence = sorted(required - item.keys())
                if missing_evidence:
                    errors.append(f"{item_prefix} missing fields: {', '.join(missing_evidence)}")
                    continue
                if item["type"] not in ALLOWED_EVIDENCE_TYPES:
                    errors.append(f"{item_prefix}.type is invalid: {item['type']}")
                else:
                    evidence_types.add(item["type"])
                if not _is_iso_date(item["observed_at"]):
                    errors.append(f"{item_prefix}.observed_at must be an ISO date")
                for field in ("source", "result"):
                    if not isinstance(item[field], str) or not item[field]:
                        errors.append(f"{item_prefix}.{field} must be a non-empty string")

        if status == "verified" and not evidence_types.intersection(VERIFIABLE_EVIDENCE_TYPES):
            errors.append(f"{prefix} is verified without verifiable evidence")
        if (
            verification_mode == "admin_manual"
            and status == "verified"
            and "admin_export" not in evidence_types
        ):
            errors.append(f"{prefix} needs admin_export evidence before verified status")

        unresolved = status not in {"verified", "not_applicable"}
        if unresolved and (
            not isinstance(control["next_action"], str) or not control["next_action"]
        ):
            errors.append(f"{prefix}.next_action is required for unresolved controls")

    return errors


def load_inventory(path: str | Path) -> dict[str, Any]:
    """Load and validate an inventory JSON file."""
    path = Path(path)
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise InventoryError(f"Unable to load inventory {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise InventoryError("Inventory root must be an object")
    errors = validate_inventory(data)
    if errors:
        raise InventoryError("Invalid inventory:\n- " + "\n- ".join(errors))
    return data


def summarize_inventory(data: dict[str, Any]) -> dict[str, int]:
    """Count controls by status for a compact review summary."""
    return dict(sorted(Counter(control["status"] for control in data["controls"]).items()))
