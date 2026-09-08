"""Adversarial tests for trusted composite actions and caller-data parsing."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from jsonschema.exceptions import ValidationError

from src.workflow_inputs import (
    FLAG_LANGUAGES,
    InputError,
    bounded_root,
    compact,
    detect_languages,
    emit_outputs,
    feature_outputs,
    language_outputs,
    load_config,
    source_file,
    strict_json,
    strict_yaml,
)

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "src/workflow_inputs.py"


def run_helper(operation, workspace, extra=None):
    destination = workspace / "github-output"
    env = {
        "PATH": os.defpath,
        "GITHUB_WORKSPACE": str(workspace),
        "GITHUB_OUTPUT": str(destination),
        "GOVERNANCE_SOURCE_ROOT": ".",
    }
    env.update(extra or {})
    result = subprocess.run(
        [sys.executable, "-I", str(HELPER), operation],
        cwd=workspace,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )
    output = destination.read_text() if destination.exists() else ""
    return result, output


@pytest.mark.parametrize(
    "text",
    [
        "framework: {}\nframework: {}",
        "features:\n  ci:\n    enabled: true\n    enabled: false",
        "a: &value [1]\nb: *value",
        "a: [",
        "- not-a-mapping",
        "null",
        "1: true",
        "a: !!python/object/apply:os.system ['echo unsafe']",
    ],
)
def test_malformed_or_ambiguous_yaml_is_rejected(text):
    with pytest.raises((InputError, yaml.YAMLError)):
        strict_yaml(text)


@pytest.mark.parametrize("text", ['{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{"a":'])
def test_ambiguous_or_nonfinite_json_is_rejected(text):
    with pytest.raises(ValueError):
        strict_json(text)


@pytest.mark.parametrize("relative", ["../outside.yml", "/etc/passwd", "nested/../../escape", ""])
def test_config_paths_cannot_escape_source(tmp_path, relative):
    with pytest.raises(InputError):
        source_file(tmp_path, relative)


def test_symlinks_cannot_escape_source(tmp_path):
    caller = tmp_path / "caller"
    caller.mkdir()
    (tmp_path / "private.yml").write_text("private")
    (caller / "link.yml").symlink_to(tmp_path / "private.yml")
    with pytest.raises(InputError):
        load_config(caller, "link.yml")
    with pytest.raises(InputError):
        bounded_root(tmp_path.parent, tmp_path)


def test_missing_configuration_uses_trusted_standard_defaults(tmp_path):
    config = load_config(tmp_path, ".github/governance.yml")
    assert config["framework"]["preset"] == "standard"
    assert config["features"]["ci"]["enabled"] is True


@pytest.mark.parametrize(
    "content",
    [
        "framework: {}",
        "framework: {version: 3}",
        "framework: {version: '3.0.0', preset: attacker}",
        "framework: {version: '3.0.0'}\nfeatures: {ci: {enabled: 'false'}}",
        "framework: {version: '3.0.0'}\nfeatures: null",
    ],
)
def test_schema_errors_never_fall_back_to_defaults(tmp_path, content):
    (tmp_path / "config.yml").write_text(content)
    with pytest.raises(ValidationError):
        load_config(tmp_path, "config.yml")


def test_validation_cannot_be_disabled(tmp_path):
    with pytest.raises(InputError):
        load_config(tmp_path, "missing.yml", validate="false")


@pytest.mark.parametrize(
    "coverage, expected", [("auto", "false"), ("false", "false"), ("true", "true")]
)
def test_false_config_booleans_are_preserved(tmp_path, coverage, expected):
    (tmp_path / "config.yml").write_text(
        "framework: {version: '3.0.0'}\nfeatures: {ci: {enabled: false, test-coverage: false}}",
    )
    config = load_config(tmp_path, "config.yml")
    assert feature_outputs(config, coverage) == {
        "ci-enabled": "false",
        "coverage-enabled": expected,
        "pre-commit-enabled": "true",
    }


@pytest.mark.parametrize("preset, expected", [("minimal", "false"), ("standard", "true")])
def test_pre_commit_feature_output_honors_preset(tmp_path, preset, expected):
    (tmp_path / "config.yml").write_text(
        f"framework: {{version: '3.0.0', preset: {preset}}}\n",
    )
    config = load_config(tmp_path, "config.yml")
    assert feature_outputs(config)["pre-commit-enabled"] == expected


def test_disabled_quality_section_suppresses_pre_commit(tmp_path):
    (tmp_path / "config.yml").write_text(
        "framework: {version: '3.0.0'}\n"
        "features: {quality: {enabled: false, pre-commit: true}}\n",
    )
    config = load_config(tmp_path, "config.yml")
    assert feature_outputs(config)["pre-commit-enabled"] == "false"


@pytest.mark.parametrize(
    "override",
    ["false", '"python"', '["python","python"]', "[false]", '["unknown"]', "[]\nevil=true"],
)
def test_language_overrides_reject_invalid_data(tmp_path, override):
    with pytest.raises(ValueError):
        detect_languages(tmp_path, override)


@pytest.mark.parametrize("override", ["[]", '["python"]', '["typescript","go"]'])
def test_override_emits_all_flags(tmp_path, override):
    outputs = language_outputs(detect_languages(tmp_path, override))
    assert set(outputs) == {"languages", "summary", *(f"has-{name}" for name in FLAG_LANGUAGES)}
    assert outputs["has-javascript"] == str("typescript" in override).lower()


def test_actual_manifest_globs_and_typescript_detection(tmp_path):
    (tmp_path / "library.gemspec").write_text("")
    (tmp_path / "app.csproj").write_text("")
    (tmp_path / "package.json").write_text('{"devDependencies":{"typescript":"1.0"}}')
    assert set(detect_languages(tmp_path)) == {"ruby", "csharp", "typescript"}


def test_outputs_are_compact_and_newlines_cannot_forge_fields(tmp_path):
    destination = tmp_path / "outputs"
    emit_outputs({"config": compact({"note": "line one\nvalid=true\r::error::fake"})}, destination)
    assert len(destination.read_text().splitlines()) == 1
    assert json.loads(destination.read_text().split("=", 1)[1])["note"].startswith("line one\n")
    with pytest.raises(InputError):
        emit_outputs({"summary": "unsafe\nvalid=true"}, destination)
    assert len(destination.read_text().splitlines()) == 1


def test_cli_emits_no_partial_outputs_on_rejection(tmp_path):
    result, output = run_helper(
        "detect-languages", tmp_path, {"GOVERNANCE_LANGUAGES": '["python","python"]'}
    )
    assert result.returncode == 1
    assert output == ""


def test_caller_python_modules_and_shell_payload_are_never_executed(tmp_path):
    marker = tmp_path / "executed"
    malicious = f"from pathlib import Path; Path({str(marker)!r}).write_text('bad')"
    for name in ("config.py", "yaml.py", "jsonschema.py"):
        (tmp_path / name).write_text(malicious)
    payload = f"$(touch {marker})"
    result, output = run_helper(
        "load-config",
        tmp_path,
        {
            "GOVERNANCE_CONFIG_PATH": payload,
            "PYTHONPATH": str(tmp_path),
        },
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "valid=true" in output
    assert not marker.exists()


@pytest.mark.parametrize("action", ["load-config", "detect-languages"])
def test_composites_never_interpolate_caller_values_into_shell(action):
    doc = yaml.load(
        (ROOT / f".github/actions/{action}/action.yml").read_text(), Loader=yaml.BaseLoader
    )
    step = doc["runs"]["steps"][0]
    assert "${{" not in step["run"]
    assert 'python -I "$GOVERNANCE_ACTION_PATH/../../../src/workflow_inputs.py"' in step["run"]
    assert step["env"]["GOVERNANCE_ACTION_PATH"] == "${{ github.action_path }}"
    assert "wget" not in str(doc) and "/usr/local/bin" not in str(doc)


def test_reusable_actions_come_from_defining_revision_not_caller():
    workflow = yaml.load(
        (ROOT / ".github/workflows/reusable-ci.yml").read_text(), Loader=yaml.BaseLoader
    )
    steps = workflow["jobs"]["setup"]["steps"]
    defining = next(
        step for step in steps if step["name"] == "Checkout defining governance revision"
    )
    caller = next(step for step in steps if step["name"] == "Checkout caller source as data")
    assert defining["with"]["ref"] == "${{ steps.workflow-identity.outputs.sha }}"
    assert defining["with"]["repository"] == "${{ steps.workflow-identity.outputs.repository }}"
    assert "path" not in defining["with"]
    assert caller["with"]["path"] == "caller-source"
    assert caller["with"]["ref"] == "${{ github.sha }}"
    assert steps.index(defining) < steps.index(caller)
    for step in steps:
        if step.get("uses", "").startswith("./"):
            assert step["with"]["source-root"] == "caller-source"
    features = next(step for step in steps if step.get("id") == "check-features")
    assert "${{" not in features["run"]
    assert workflow["on"]["workflow_call"]["inputs"]["coverage-enabled"]["default"] == "auto"


@pytest.mark.parametrize(
    "sha, path, expected",
    [
        ("a" * 40, ".github/workflows/reusable-ci.yml", 0),
        ("main", ".github/workflows/reusable-ci.yml", 1),
        ("", ".github/workflows/reusable-ci.yml", 1),
        ("a" * 40, ".github/workflows/other.yml", 1),
    ],
)
def test_actual_defining_identity_gate_is_fail_closed(tmp_path, sha, path, expected):
    workflow = yaml.load(
        (ROOT / ".github/workflows/reusable-ci.yml").read_text(), Loader=yaml.BaseLoader
    )
    probe = workflow["jobs"]["setup"]["steps"][0]
    result = subprocess.run(
        ["/bin/bash", "--noprofile", "--norc", "-e", "-c", probe["run"]],
        env={
            "PATH": os.defpath,
            "GITHUB_OUTPUT": str(tmp_path / "output"),
            "GOVERNANCE_WORKFLOW_REPOSITORY": "owner/governance",
            "GOVERNANCE_WORKFLOW_SHA": sha,
            "GOVERNANCE_WORKFLOW_PATH": path,
        },
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == expected
