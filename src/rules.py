"""Governance rules for the ORGAN system.

Each rule is a callable that takes a repository state dict and returns
a (passed: bool, message: str) tuple.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    """A governance rule that can validate a repository or organ state."""

    name: str
    description: str
    check: Callable[[dict], tuple[bool, str]]
    severity: str = "error"  # error | warning | info


def check_readme_exists(state: dict) -> tuple[bool, str]:
    """Every repo must have a README."""
    has_readme = state.get("has_readme", False)
    if has_readme:
        return True, "README.md found"
    return False, "README.md is missing"


def check_license_exists(state: dict) -> tuple[bool, str]:
    """Every repo must have a LICENSE file."""
    has_license = state.get("has_license", False)
    if has_license:
        return True, "LICENSE file found"
    return False, "LICENSE file is missing"


def check_no_back_edges(state: dict) -> tuple[bool, str]:
    """Dependency flow is I→II→III only; higher organs cannot depend on lower."""
    organ_order = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8}
    organ = state.get("organ", "")
    dependencies = state.get("dependencies", [])

    for dep in dependencies:
        dep_organ = dep.get("organ", "")
        if (
            organ in organ_order
            and dep_organ in organ_order
            and organ_order[dep_organ] > organ_order[organ]
        ):
            return False, f"Back-edge detected: ORGAN-{organ} depends on ORGAN-{dep_organ}"
    return True, "No back-edges in dependency graph"


def check_documentation_status(state: dict) -> tuple[bool, str]:
    """Documentation status must be one of the valid values."""
    valid_statuses = {"DEPLOYED", "SKELETON", "DESIGN_ONLY", "EMPTY", "ACTIVE"}
    status = state.get("documentation_status", "")
    if status in valid_statuses:
        return True, f"Documentation status '{status}' is valid"
    return False, f"Invalid documentation status: '{status}'"


def check_implementation_status(state: dict) -> tuple[bool, str]:
    """Implementation status must follow the valid state machine."""
    valid_statuses = {"PRODUCTION", "PROTOTYPE", "SKELETON", "DESIGN_ONLY", "PLANNED"}
    status = state.get("implementation_status", "")
    if status in valid_statuses:
        return True, f"Implementation status '{status}' is valid"
    return False, f"Invalid implementation status: '{status}'"


def check_ci_enabled(state: dict) -> tuple[bool, str]:
    """All governed repos must have CI enabled."""
    if state.get("ci_enabled", True):
        return True, "CI is enabled"
    return False, "CI is disabled — all governed repos require CI"


def check_security_for_preset(state: dict) -> tuple[bool, str]:
    """Standard and enterprise presets require security scanning."""
    preset = state.get("preset", "")
    if preset in ("standard", "enterprise"):
        if not state.get("security_enabled", False):
            return False, f"Preset '{preset}' requires security scanning to be enabled"
        if preset == "enterprise" and not state.get("codeql_enabled", False):
            return False, "Enterprise preset requires CodeQL to be enabled"
    return True, f"Security configuration meets '{preset}' preset requirements"


def check_compliance_for_enterprise(state: dict) -> tuple[bool, str]:
    """Enterprise preset requires compliance features enabled."""
    preset = state.get("preset", "")
    if preset == "enterprise" and not state.get("compliance_enabled", False):
        return False, "Enterprise preset requires compliance features to be enabled"
    return True, "Compliance configuration is appropriate for preset"


# Registry of all built-in rules
BUILTIN_RULES: list[Rule] = [
    Rule("readme-exists", "Every repository must have a README", check_readme_exists),
    Rule("license-exists", "Every repository must have a LICENSE", check_license_exists),
    Rule("no-back-edges", "No reverse dependency edges allowed", check_no_back_edges),
    Rule("valid-doc-status", "Documentation status must be valid", check_documentation_status),
    Rule("valid-impl-status", "Implementation status must be valid", check_implementation_status),
    Rule(
        "ci-enabled",
        "CI must be enabled for all governed repos",
        check_ci_enabled,
        severity="warning",
    ),
    Rule(
        "security-for-preset",
        "Security scanning must match preset level",
        check_security_for_preset,
    ),
    Rule(
        "compliance-for-enterprise",
        "Enterprise preset requires compliance",
        check_compliance_for_enterprise,
    ),
]
