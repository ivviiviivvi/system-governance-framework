"""Deterministic receipt-auditor fixtures."""

from copy import deepcopy

from receipt_auditor import audit_receipt


def valid_receipt():
    return {
        "task": {"source_sha": "a" * 40},
        "stages": {
            "proposal": {"principal": "agent:codex"},
            "authorization": {"principal": "human:owner", "kind": "human", "source_sha": "a" * 40},
            "execution": {"principal": "workflow:relay", "reservation_state": "acknowledged"},
            "verification": {"principal": "validator:deterministic"},
            "publication": {"principal": "workflow:receipt", "status": "success"},
        },
        "workflow": {
            "expected_defining_sha": "b" * 40,
            "defining": {
                "repository": "owner/repo",
                "file_path": ".github/workflows/relay.yml",
                "ref": "refs/heads/main",
                "sha": "b" * 40,
            },
        },
        "budget": {"reserved": 10, "actual": 8},
        "aggregate": "success",
        "public": {"contains_private_payload": False},
    }


def codes(receipt):
    return {finding["code"] for finding in audit_receipt(receipt)["findings"]}


def test_valid_receipt_passes_without_writes():
    result = audit_receipt(valid_receipt())
    assert result["valid"] is True
    assert result["writes_performed"] is False


def test_authority_and_workflow_defects_fail_closed():
    receipt = valid_receipt()
    receipt["stages"]["authorization"] = {
        "principal": "agent:codex",
        "kind": "agent",
        "source_sha": "c" * 40,
    }
    receipt["workflow"]["defining"]["sha"] = "d" * 40
    assert {
        "SELF_AUTHORIZATION",
        "NON_HUMAN_AUTHORIZATION",
        "STALE_AUTHORIZATION",
        "WORKFLOW_SHA_MISMATCH",
    } <= codes(receipt)


def test_reservation_replay_budget_and_success_claims_fail_closed():
    receipt = valid_receipt()
    receipt["stages"]["execution"]["reservation_state"] = "pending"
    receipt["duplicate_reservation"] = True
    receipt["replayed_result"] = True
    receipt["budget"]["actual"] = 11
    receipt["claim"] = {"evidence_origin": "review_bot", "execution_success": True}
    receipt["stages"]["publication"]["status"] = "error"
    assert {
        "UNACKNOWLEDGED_RESERVATION",
        "DUPLICATE_RESERVATION",
        "REPLAYED_RESULT",
        "BUDGET_OVERRUN",
        "MISLEADING_SUCCESS",
        "FALSE_AGGREGATE_SUCCESS",
    } <= codes(receipt)


def test_public_private_payload_and_missing_verifier_fail_closed():
    receipt = deepcopy(valid_receipt())
    receipt["public"]["contains_private_payload"] = True
    receipt["stages"]["verification"] = {}
    assert {"PUBLIC_PRIVATE_DATA", "MISSING_INDEPENDENT_VERIFIER"} <= codes(receipt)
