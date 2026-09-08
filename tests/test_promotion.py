"""Tests for the promotion state machine."""

import importlib
from unittest.mock import MagicMock, patch

import src.promotion as promotion_module
from src.promotion import VALID_TRANSITIONS, can_promote, promote


class TestCanPromote:
    def test_planned_to_skeleton(self):
        assert can_promote("PLANNED", "SKELETON") is True

    def test_skeleton_to_prototype(self):
        assert can_promote("SKELETON", "PROTOTYPE") is True

    def test_prototype_to_production(self):
        assert can_promote("PROTOTYPE", "PRODUCTION") is True

    def test_production_to_archived(self):
        assert can_promote("PRODUCTION", "ARCHIVED") is True

    def test_cannot_skip_states(self):
        assert can_promote("PLANNED", "PRODUCTION") is False

    def test_cannot_go_backwards_planned(self):
        assert can_promote("PROTOTYPE", "PLANNED") is False

    def test_unarchive_allowed(self):
        assert can_promote("ARCHIVED", "PRODUCTION") is True

    def test_design_only_to_prototype(self):
        assert can_promote("DESIGN_ONLY", "PROTOTYPE") is True

    def test_invalid_states(self):
        assert can_promote("INVALID", "SKELETON") is False
        assert can_promote("SKELETON", "INVALID") is False


class TestPromote:
    def test_successful_promotion(self):
        result = promote("SKELETON", "PROTOTYPE", "test-repo")
        assert result.success is True
        assert "SKELETON → PROTOTYPE" in result.message

    def test_failed_promotion(self):
        result = promote("PLANNED", "PRODUCTION", "test-repo")
        assert result.success is False
        assert "Cannot promote" in result.message

    def test_unknown_state(self):
        result = promote("INVALID", "SKELETON")
        assert result.success is False
        assert "Unknown state" in result.message

    def test_unknown_target(self):
        result = promote("SKELETON", "INVALID")
        assert result.success is False
        assert "Unknown target" in result.message


class TestStateMachine:
    def test_all_states_have_transitions(self):
        for state in VALID_TRANSITIONS:
            assert len(VALID_TRANSITIONS[state]) >= 1

    def test_no_self_transitions(self):
        for state, targets in VALID_TRANSITIONS.items():
            assert state not in targets

    def test_full_lifecycle(self):
        path = ["PLANNED", "SKELETON", "PROTOTYPE", "PRODUCTION", "ARCHIVED"]
        for i in range(len(path) - 1):
            assert can_promote(path[i], path[i + 1]), f"{path[i]} → {path[i + 1]} should be valid"


class TestEngineIntegration:
    def test_engine_state_machine_import(self):
        mock_engine = MagicMock()
        mock_sm = MagicMock()
        mock_engine.governance.state_machine = mock_sm

        with patch.dict(
            "sys.modules",
            {
                "organvm_engine": mock_engine,
                "organvm_engine.governance": mock_engine.governance,
                "organvm_engine.governance.state_machine": mock_sm,
            },
        ):
            importlib.reload(promotion_module)
            assert promotion_module._HAS_ENGINE_STATE_MACHINE is True

        # Restore original state
        importlib.reload(promotion_module)
        assert promotion_module._HAS_ENGINE_STATE_MACHINE is False

    def test_engine_allowed_same_canonical(self):
        promotion_module._engine_check_transition = MagicMock(return_value=(True, ""))
        # Both CANONICAL and LEGACY mapped identically (or not mapped)
        assert promotion_module._engine_allowed("CUSTOM_STATE", "CUSTOM_STATE_2") is True
        promotion_module._engine_check_transition.assert_called_with(
            "CUSTOM_STATE", "CUSTOM_STATE_2"
        )

    def test_engine_allowed_different_canonical(self):
        promotion_module._engine_get_valid_transitions = MagicMock(
            return_value=["CANDIDATE", "GRADUATED"]
        )
        # "SKELETON" -> "PROTOTYPE" maps to "LOCAL" -> "CANDIDATE"
        assert promotion_module._engine_allowed("SKELETON", "PROTOTYPE") is True
        promotion_module._engine_get_valid_transitions.assert_called_with("LOCAL")

    def test_engine_allowed_unarchive(self):
        promotion_module._engine_get_valid_transitions = MagicMock(return_value=[])
        assert promotion_module._engine_allowed("ARCHIVED", "PRODUCTION") is True

    def test_engine_allowed_false(self):
        promotion_module._engine_check_transition = MagicMock(return_value=(False, ""))
        promotion_module._engine_get_valid_transitions = MagicMock(return_value=[])
        assert promotion_module._engine_allowed("SKELETON", "ARCHIVED") is False

    @patch.object(promotion_module, "_HAS_ENGINE_STATE_MACHINE", True)
    @patch.object(promotion_module, "_engine_allowed", return_value=True)
    def test_can_promote_with_engine(self, mock_engine_allowed):
        # Even if legacy denies it, engine allows it
        assert promotion_module.can_promote("PLANNED", "PRODUCTION") is True

    @patch.object(promotion_module, "_HAS_ENGINE_STATE_MACHINE", True)
    def test_promote_failed_with_engine(self):
        promotion_module._engine_get_valid_transitions = MagicMock(return_value=["CANDIDATE"])
        with patch.object(promotion_module, "can_promote", return_value=False):
            # Temporarily clear the transitions to hit line 108
            original = promotion_module.VALID_TRANSITIONS["SKELETON"]
            promotion_module.VALID_TRANSITIONS["SKELETON"] = set()
            try:
                result = promotion_module.promote("SKELETON", "PRODUCTION")
                assert result.success is False
                assert "CANDIDATE" in result.message
            finally:
                promotion_module.VALID_TRANSITIONS["SKELETON"] = original
