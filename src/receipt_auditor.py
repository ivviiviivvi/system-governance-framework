"""Deterministic, read-only checks for synthetic execution receipts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REQUIRED_STAGES = ("proposal", "authorization", "execution", "verification", "publication")


def _finding(code: str, path: str, detail: str) -> dict[str, str]:
    return {"code": code, "path": path, "detail": detail}


def audit_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    task = receipt.get("task", {})
    stages = receipt.get("stages", {})
    workflow = receipt.get("workflow", {})

    for stage in REQUIRED_STAGES:
        if not isinstance(stages.get(stage), dict):
            findings.append(_finding("MISSING_STAGE", f"stages.{stage}", "required stage absent"))

    authorization = stages.get("authorization", {})
    proposal = stages.get("proposal", {})
    execution = stages.get("execution", {})
    verification = stages.get("verification", {})

    expected_sha = task.get("source_sha")
    if authorization.get("source_sha") != expected_sha:
        findings.append(
            _finding(
                "STALE_AUTHORIZATION",
                "stages.authorization.source_sha",
                "authorization is not bound to task head",
            )
        )
    if proposal.get("principal") and proposal.get("principal") == authorization.get("principal"):
        findings.append(
            _finding(
                "SELF_AUTHORIZATION",
                "stages.authorization.principal",
                "proposer cannot independently authorize its own change",
            )
        )
    if authorization.get("kind") != "human":
        findings.append(
            _finding(
                "NON_HUMAN_AUTHORIZATION",
                "stages.authorization.kind",
                "consequential mutation requires human authorization",
            )
        )
    if execution.get("reservation_state") != "acknowledged":
        findings.append(
            _finding(
                "UNACKNOWLEDGED_RESERVATION",
                "stages.execution.reservation_state",
                "provider execution preceded canonical acknowledgement",
            )
        )
    if not verification.get("principal") or verification.get("principal") == execution.get(
        "principal"
    ):
        findings.append(
            _finding(
                "MISSING_INDEPENDENT_VERIFIER",
                "stages.verification.principal",
                "verification must identify an independent principal",
            )
        )

    defining = workflow.get("defining", {})
    for field in ("repository", "file_path", "ref", "sha"):
        if not defining.get(field):
            findings.append(
                _finding(
                    "MISSING_WORKFLOW_IDENTITY",
                    f"workflow.defining.{field}",
                    "defining workflow identity incomplete",
                )
            )
    if workflow.get("expected_defining_sha") != defining.get("sha"):
        findings.append(
            _finding(
                "WORKFLOW_SHA_MISMATCH",
                "workflow.defining.sha",
                "executed workflow does not match admitted workflow",
            )
        )

    budget = receipt.get("budget", {})
    if (
        isinstance(budget.get("reserved"), (int, float))
        and isinstance(budget.get("actual"), (int, float))
        and budget["actual"] > budget["reserved"]
    ):
        findings.append(
            _finding("BUDGET_OVERRUN", "budget.actual", "actual cost exceeds reservation")
        )

    if receipt.get("duplicate_reservation"):
        findings.append(
            _finding(
                "DUPLICATE_RESERVATION",
                "duplicate_reservation",
                "reservation ID was already admitted",
            )
        )
    if receipt.get("replayed_result"):
        findings.append(
            _finding("REPLAYED_RESULT", "replayed_result", "result was previously consumed")
        )
    if receipt.get("claim", {}).get("evidence_origin") == "review_bot" and receipt.get(
        "claim", {}
    ).get("execution_success"):
        findings.append(
            _finding(
                "MISLEADING_SUCCESS",
                "claim.execution_success",
                "review evidence is not execution evidence",
            )
        )
    if receipt.get("public", {}).get("contains_private_payload"):
        findings.append(
            _finding(
                "PUBLIC_PRIVATE_DATA",
                "public.contains_private_payload",
                "public receipt contains private material",
            )
        )
    if (
        stages.get("publication", {}).get("status") != "success"
        and receipt.get("aggregate") == "success"
    ):
        findings.append(
            _finding(
                "FALSE_AGGREGATE_SUCCESS",
                "aggregate",
                "publication failed but receipt claims success",
            )
        )

    canonical = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    return {
        "schema": "organvm-receipt-audit/v1",
        "receipt_digest": hashlib.sha256(canonical).hexdigest(),
        "valid": not findings,
        "findings": sorted(findings, key=lambda finding: (finding["code"], finding["path"])),
        "writes_performed": False,
    }


def audit_file(path: Path) -> dict[str, Any]:
    return audit_receipt(json.loads(path.read_text(encoding="utf-8")))
