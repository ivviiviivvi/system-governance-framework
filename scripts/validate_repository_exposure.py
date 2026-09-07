"""Validate the repository exposure disposition ledger."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = ROOT / "config" / "repository-exposure.inventory.json"
ALLOWED = {
    "completed_split",
    "split_required",
    "public_candidate",
    "keep_private",
    "archived_private",
}


def validate(inventory: dict) -> list[str]:
    errors: list[str] = []
    coverage = inventory.get("coverage", {})
    dispositions = inventory.get("dispositions", {})

    unknown = set(dispositions) - ALLOWED
    if unknown:
        errors.append(f"unknown dispositions: {sorted(unknown)}")

    seen: dict[str, str] = {}
    for disposition, repositories in dispositions.items():
        if repositories != sorted(repositories):
            errors.append(f"{disposition} repositories must be sorted")
        for repository in repositories:
            if repository in seen:
                errors.append(f"{repository} appears in both {seen[repository]} and {disposition}")
            seen[repository] = disposition

    if len(seen) != coverage.get("private"):
        errors.append(
            f"disposition count {len(seen)} does not match private coverage "
            f"{coverage.get('private')}"
        )
    if coverage.get("public", 0) + coverage.get("private", 0) != coverage.get("repositories"):
        errors.append("public + private coverage must equal repositories")

    reference = inventory.get("reference_split", {})
    private_reference = reference.get("private")
    if private_reference not in dispositions.get("completed_split", []):
        errors.append("reference private repository must be in completed_split")
    if reference.get("status") != "completed_split":
        errors.append("reference split must have completed_split status")

    tranche = inventory.get("next_tranche", {})
    candidates = set(dispositions.get("public_candidate", []))
    if not set(tranche.get("repositories", [])).issubset(candidates):
        errors.append("next tranche may contain only public_candidate repositories")
    if tranche.get("status") != "pending_content_and_history_audit":
        errors.append("next tranche must remain audit-gated")

    return errors


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
    try:
        inventory = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Unable to load {path}: {exc}", file=sys.stderr)
        return 1

    errors = validate(inventory)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    dispositions = inventory["dispositions"]
    print(
        json.dumps(
            {
                "private_repositories": sum(map(len, dispositions.values())),
                "dispositions": {key: len(value) for key, value in dispositions.items()},
                "next_tranche": inventory["next_tranche"]["name"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
