"""Read-only consistency audit CLI; context files are not authentication evidence."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from receipt_auditor import TrustedAuditContext, audit_file


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate context key")
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument(
        "--context",
        type=Path,
        help="Separately authenticated observations, never copied from the candidate receipt",
    )
    args = parser.parse_args()
    context = None
    if args.context:
        try:
            payload = json.loads(
                args.context.read_text(encoding="utf-8"), object_pairs_hook=unique_object
            )
            context = TrustedAuditContext.model_validate_json(json.dumps(payload, allow_nan=False))
        except (OSError, UnicodeError, ValueError, TypeError, RecursionError):
            print(
                json.dumps(
                    {
                        "schema": "organvm-receipt-audit/v2",
                        "receipt_digest": None,
                        "valid": False,
                        "status": "unknown",
                        "scope": "supplied_evidence_consistency",
                        "production_authorized": False,
                        "findings": [
                            {
                                "code": "INVALID_CONTEXT",
                                "path": "context",
                                "detail": "context read/schema validation failed",
                                "severity": "unknown",
                            }
                        ],
                        "uncertainty": ["INVALID_CONTEXT"],
                        "unsupported_claims": [],
                        "writes_performed": False,
                    }
                )
            )
            return 2
    result = audit_file(args.receipt, context=context)
    print(json.dumps(result, sort_keys=True, allow_nan=False))
    return {"verified": 0, "rejected": 1, "unknown": 2}[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
