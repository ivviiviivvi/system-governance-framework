"""A valid coverage ledger is not evidence that the program is complete."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "0",
    "A1",
    "A2",
    "B1",
    "B2",
    "B3",
    "C1",
    "C2",
    "C3",
    "D1",
    "D2",
    "E1",
    "E2",
    "E3",
    "F1",
    "F2",
    "F3",
    "G1",
    "G2",
    "G3",
    "H1",
    "H2",
    "H3",
    "I1",
    "I2",
}


def test_every_plan_gate_has_a_durable_owner_and_disposition():
    program = json.loads((ROOT / "config/implementation-program.json").read_text())
    rows = program["gates"]
    assert len(rows) == len(REQUIRED)
    assert {row["id"] for row in rows} == REQUIRED
    for row in rows:
        assert row["owner"] in program["owners"]
        assert row["disposition"].strip()
        assert set(row["depends_on"]) <= REQUIRED - {row["id"]}
    assert program["program_complete"] is False
    assert program["scope"]["current_estate_census"] is False


def test_dependency_graph_is_acyclic():
    program = json.loads((ROOT / "config/implementation-program.json").read_text())
    rows = {row["id"]: row for row in program["gates"]}

    def visit(identity, ancestors):
        assert identity not in ancestors
        for parent in rows[identity]["depends_on"]:
            visit(parent, ancestors | {identity})

    for identity in rows:
        visit(identity, set())


def test_control_catalogue_is_explicitly_not_live_enforcement():
    catalogue = json.loads((ROOT / "config/protected-control-inputs.json").read_text())
    assert catalogue["enforcement_status"] == "proposal_not_applied"
    assert {"src/**", "scripts/**", "tests/**", ".github/workflows/**", "AGENTS.md"} <= set(
        catalogue["paths"]
    )
