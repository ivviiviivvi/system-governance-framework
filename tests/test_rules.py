"""Tests for governance rules."""

from src.rules import (
    BUILTIN_RULES,
    check_ci_enabled,
    check_compliance_for_enterprise,
    check_documentation_status,
    check_implementation_status,
    check_license_exists,
    check_no_back_edges,
    check_readme_exists,
    check_security_for_preset,
)


class TestReadmeRule:
    def test_passes_when_readme_exists(self):
        passed, _ = check_readme_exists({"has_readme": True})
        assert passed is True

    def test_fails_when_readme_missing(self):
        passed, _ = check_readme_exists({"has_readme": False})
        assert passed is False

    def test_fails_when_key_absent(self):
        passed, _ = check_readme_exists({})
        assert passed is False


class TestLicenseRule:
    def test_passes_when_license_exists(self):
        passed, _ = check_license_exists({"has_license": True})
        assert passed is True

    def test_fails_when_license_missing(self):
        passed, _ = check_license_exists({})
        assert passed is False


class TestNoBackEdges:
    def test_no_dependencies(self):
        passed, _ = check_no_back_edges({"organ": "I", "dependencies": []})
        assert passed is True

    def test_valid_forward_dependency(self):
        state = {"organ": "I", "dependencies": [{"organ": "I"}]}
        passed, _ = check_no_back_edges(state)
        assert passed is True

    def test_detects_back_edge(self):
        state = {"organ": "III", "dependencies": [{"organ": "IV"}]}
        passed, msg = check_no_back_edges(state)
        assert passed is False
        assert "Back-edge" in msg

    def test_allows_same_organ_dependency(self):
        state = {"organ": "II", "dependencies": [{"organ": "II"}]}
        passed, _ = check_no_back_edges(state)
        assert passed is True

    def test_organ_viii_in_order(self):
        """ORGAN-VIII must be recognised in the dependency graph."""
        state = {"organ": "VII", "dependencies": [{"organ": "VIII"}]}
        passed, msg = check_no_back_edges(state)
        assert passed is False
        assert "Back-edge" in msg

    def test_organ_viii_forward_is_valid(self):
        state = {"organ": "VIII", "dependencies": [{"organ": "I"}]}
        passed, _ = check_no_back_edges(state)
        assert passed is True


class TestDocumentationStatus:
    def test_valid_deployed(self):
        passed, _ = check_documentation_status({"documentation_status": "DEPLOYED"})
        assert passed is True

    def test_valid_skeleton(self):
        passed, _ = check_documentation_status({"documentation_status": "SKELETON"})
        assert passed is True

    def test_invalid_status(self):
        passed, _ = check_documentation_status({"documentation_status": "BROKEN"})
        assert passed is False


class TestImplementationStatus:
    def test_valid_production(self):
        passed, _ = check_implementation_status({"implementation_status": "PRODUCTION"})
        assert passed is True

    def test_invalid_status(self):
        passed, _ = check_implementation_status({"implementation_status": "UNKNOWN"})
        assert passed is False


class TestCiEnabled:
    def test_passes_when_enabled(self):
        passed, _ = check_ci_enabled({"ci_enabled": True})
        assert passed is True

    def test_fails_when_disabled(self):
        passed, _ = check_ci_enabled({"ci_enabled": False})
        assert passed is False

    def test_defaults_to_enabled(self):
        passed, _ = check_ci_enabled({})
        assert passed is True


class TestSecurityForPreset:
    def test_minimal_passes_without_security(self):
        passed, _ = check_security_for_preset({"preset": "minimal", "security_enabled": False})
        assert passed is True

    def test_standard_requires_security(self):
        passed, _ = check_security_for_preset({"preset": "standard", "security_enabled": False})
        assert passed is False

    def test_standard_passes_with_security(self):
        passed, _ = check_security_for_preset({"preset": "standard", "security_enabled": True})
        assert passed is True

    def test_enterprise_requires_codeql(self):
        passed, _ = check_security_for_preset(
            {
                "preset": "enterprise",
                "security_enabled": True,
                "codeql_enabled": False,
            }
        )
        assert passed is False

    def test_enterprise_passes_with_codeql(self):
        passed, _ = check_security_for_preset(
            {
                "preset": "enterprise",
                "security_enabled": True,
                "codeql_enabled": True,
            }
        )
        assert passed is True


class TestComplianceForEnterprise:
    def test_non_enterprise_passes(self):
        passed, _ = check_compliance_for_enterprise({"preset": "standard"})
        assert passed is True

    def test_enterprise_requires_compliance(self):
        passed, _ = check_compliance_for_enterprise(
            {
                "preset": "enterprise",
                "compliance_enabled": False,
            }
        )
        assert passed is False

    def test_enterprise_passes_with_compliance(self):
        passed, _ = check_compliance_for_enterprise(
            {
                "preset": "enterprise",
                "compliance_enabled": True,
            }
        )
        assert passed is True


class TestBuiltinRules:
    def test_all_rules_registered(self):
        assert len(BUILTIN_RULES) >= 8

    def test_all_rules_have_names(self):
        for rule in BUILTIN_RULES:
            assert rule.name
            assert rule.description

    def test_new_rules_present(self):
        names = {r.name for r in BUILTIN_RULES}
        assert "ci-enabled" in names
        assert "security-for-preset" in names
        assert "compliance-for-enterprise" in names
