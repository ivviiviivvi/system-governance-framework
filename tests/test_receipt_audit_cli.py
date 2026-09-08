"""CLI failures never grant authority or reflect sensitive input."""

import json
import subprocess
import sys
from pathlib import Path

from tests.test_receipt_auditor import synthetic_case

ROOT = Path(__file__).resolve().parents[1]


def test_missing_receipt_is_rejected_without_traceback(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/audit_execution_receipt.py"),
            str(tmp_path / "missing"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert json.loads(result.stdout)["production_authorized"] is False
    assert not result.stderr


def test_invalid_context_does_not_echo_secret_payload(tmp_path):
    context = tmp_path / "context.json"
    context.write_text('{"synthetic-secret-field":"synthetic-secret-value"}')
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/audit_execution_receipt.py"),
            str(tmp_path / "missing"),
            "--context",
            str(context),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["status"] == "unknown"
    assert report["schema"] == "organvm-receipt-audit/v2"
    assert report["valid"] is False
    assert report["writes_performed"] is False
    assert report["uncertainty"] == ["INVALID_CONTEXT"]
    assert "synthetic-secret" not in result.stdout + result.stderr


def test_valid_receipt_without_observations_is_unknown(tmp_path):
    receipt, _ = synthetic_case()
    path = tmp_path / "receipt.json"
    path.write_text(json.dumps(receipt), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/audit_execution_receipt.py"), str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["status"] == "unknown"
    assert report["valid"] is False
    assert report["production_authorized"] is False
    assert report["uncertainty"] == ["TRUSTED_CONTEXT_REQUIRED"]
    assert not result.stderr


def test_synthetic_observation_context_verifies_consistency_not_authenticity(tmp_path):
    receipt, context = synthetic_case()
    path = tmp_path / "receipt.json"
    context_path = tmp_path / "context.json"
    path.write_text(json.dumps(receipt), encoding="utf-8")
    context_path.write_text(json.dumps(context), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/audit_execution_receipt.py"),
            str(path),
            "--context",
            str(context_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["status"] == "verified"
    assert report["valid"] is True
    assert report["scope"] == "supplied_evidence_consistency"
    assert report["production_authorized"] is False
    assert report["writes_performed"] is False
    assert not result.stderr
