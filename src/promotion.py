"""Promotion state machine for repository lifecycle.

States: PLANNED → SKELETON → PROTOTYPE → PRODUCTION → ARCHIVED

When available, the canonical organvm-engine state machine is imported for
compatibility with the wider ORGANVM governance model. This module preserves
the repo's legacy public API and state names through a compatibility adapter.
"""

from __future__ import annotations

from dataclasses import dataclass

try:
    from organvm_engine.governance.state_machine import (
        check_transition as _engine_check_transition,
    )
    from organvm_engine.governance.state_machine import (
        get_valid_transitions as _engine_get_valid_transitions,
    )

    _HAS_ENGINE_STATE_MACHINE = True
except ImportError:
    _HAS_ENGINE_STATE_MACHINE = False

VALID_TRANSITIONS: dict[str, set[str]] = {
    "PLANNED": {"SKELETON"},
    "SKELETON": {"PROTOTYPE", "DESIGN_ONLY"},
    "DESIGN_ONLY": {"PROTOTYPE", "SKELETON"},
    "PROTOTYPE": {"PRODUCTION", "SKELETON"},
    "PRODUCTION": {"ARCHIVED", "PROTOTYPE"},
    "ARCHIVED": {"PRODUCTION"},  # un-archive is allowed
}

ALL_STATES = set(VALID_TRANSITIONS.keys()) | {"ARCHIVED"}

_LEGACY_TO_CANONICAL = {
    "PLANNED": "INCUBATOR",
    "SKELETON": "LOCAL",
    "DESIGN_ONLY": "LOCAL",
    "PROTOTYPE": "CANDIDATE",
    "PRODUCTION": "GRADUATED",
    "ARCHIVED": "ARCHIVED",
}


@dataclass
class PromotionResult:
    """Result of a promotion attempt."""

    success: bool
    from_state: str
    to_state: str
    message: str


def _legacy_allowed(current: str, target: str) -> bool:
    """Check the repo's legacy transition table directly."""
    allowed = VALID_TRANSITIONS.get(current, set())
    return target in allowed


def _engine_allowed(current: str, target: str) -> bool:
    """Check canonical engine transitions for canonical state names."""
    current_canonical = _LEGACY_TO_CANONICAL.get(current, current)
    target_canonical = _LEGACY_TO_CANONICAL.get(target, target)

    if current_canonical == current and target_canonical == target:
        ok, _ = _engine_check_transition(current, target)
        return ok

    valid_targets = set(_engine_get_valid_transitions(current_canonical))
    if target_canonical in valid_targets:
        return True

    # The canonical machine models ARCHIVED as terminal, but the legacy API
    # keeps the original unarchive path. Preserve that repo behavior.
    return current == "ARCHIVED" and target == "PRODUCTION"


def can_promote(current: str, target: str) -> bool:
    """Check if a transition from current to target is valid."""
    if current not in ALL_STATES or target not in ALL_STATES:
        return False

    if _HAS_ENGINE_STATE_MACHINE:
        # Preserve the repo's legacy surface while still consulting the
        # canonical engine state machine for canonical compatibility.
        return _legacy_allowed(current, target) or _engine_allowed(current, target)

    return _legacy_allowed(current, target)


def promote(current: str, target: str, repo_name: str = "") -> PromotionResult:
    """Attempt to promote a repo from current state to target state."""
    if current not in ALL_STATES:
        return PromotionResult(False, current, target, f"Unknown state: {current}")
    if target not in ALL_STATES:
        return PromotionResult(False, current, target, f"Unknown target state: {target}")
    if can_promote(current, target):
        return PromotionResult(
            True, current, target, f"{repo_name or 'Repo'}: {current} → {target}"
        )
    allowed = VALID_TRANSITIONS.get(current, set())
    if _HAS_ENGINE_STATE_MACHINE and not allowed:
        allowed = set(_engine_get_valid_transitions(_LEGACY_TO_CANONICAL.get(current, current)))
    return PromotionResult(
        False,
        current,
        target,
        f"Cannot promote from {current} to {target}. Allowed: {sorted(allowed)}",
    )
