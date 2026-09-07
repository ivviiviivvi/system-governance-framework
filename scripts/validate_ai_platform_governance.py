"""Validate the AI platform governance evidence inventory."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ai_platform_governance import InventoryError, load_inventory, summarize_inventory


def main() -> int:
    inventory_path = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else ROOT / "config" / "ai-platform-governance.inventory.json"
    )
    try:
        inventory = load_inventory(inventory_path)
    except InventoryError as exc:
        print(exc, file=sys.stderr)
        return 1

    print(json.dumps(summarize_inventory(inventory), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
