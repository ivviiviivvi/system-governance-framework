"""Static workflow authority checks; these do not assert hosted execution."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATHS = sorted(
    path for path in (ROOT / ".github/workflows").rglob("*") if path.suffix in {".yml", ".yaml"}
)
ACTION_PATHS = sorted(
    path
    for path in (ROOT / ".github/actions").rglob("*")
    if path.name in {"action.yml", "action.yaml"}
)
DOCUMENT_PATHS = WORKFLOW_PATHS + ACTION_PATHS
COMMIT_PIN = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_./-]+)?@[0-9a-f]{40}")


def load_yaml(path: Path) -> dict:
    # BaseLoader avoids YAML 1.1 treating GitHub's `on` key as a boolean.
    return yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def mappings(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from mappings(child)
    elif isinstance(value, list):
        for child in value:
            yield from mappings(child)


@pytest.mark.parametrize("path", DOCUMENT_PATHS, ids=lambda path: str(path.relative_to(ROOT)))
def test_external_actions_have_full_commit_pins(path):
    for item in mappings(load_yaml(path)):
        reference = item.get("uses")
        if reference is not None and not reference.startswith("./"):
            assert COMMIT_PIN.fullmatch(reference), f"Unpinned external action: {reference}"


@pytest.mark.parametrize("path", DOCUMENT_PATHS, ids=lambda path: str(path.relative_to(ROOT)))
def test_local_action_references_have_real_manifests(path):
    for item in mappings(load_yaml(path)):
        reference = item.get("uses", "")
        if reference.startswith("./"):
            local_path = (ROOT / reference).resolve()
            assert local_path.is_relative_to(ROOT), f"Local action escapes checkout: {reference}"
            if local_path.is_relative_to(ROOT / ".github/workflows"):
                assert local_path.is_file(), f"Local reusable workflow is missing: {reference}"
            else:
                assert any(
                    (local_path / name).is_file() for name in ("action.yml", "action.yaml")
                ), f"Local action is missing: {reference}"


@pytest.mark.parametrize("path", DOCUMENT_PATHS, ids=lambda path: str(path.relative_to(ROOT)))
def test_checkouts_never_persist_credentials(path):
    for item in mappings(load_yaml(path)):
        if item.get("uses", "").startswith("actions/checkout@"):
            assert item.get("with", {}).get("persist-credentials") == "false"


@pytest.mark.parametrize("filename", ["ci.yml", "reusable-ci.yml"])
def test_required_ci_cannot_ignore_failures(filename):
    workflow = load_yaml(ROOT / ".github/workflows" / filename)
    for job in workflow["jobs"].values():
        assert job.get("continue-on-error", "false") == "false"
        for step in job.get("steps", []):
            assert step.get("continue-on-error", "false") == "false"


def test_primary_ci_has_only_read_contents_permission():
    workflow = load_yaml(ROOT / ".github/workflows/ci.yml")
    assert workflow["permissions"] == {}
    assert workflow["jobs"]["test"]["permissions"] == {"contents": "read"}
    assert workflow["jobs"]["test"]["strategy"]["matrix"]["python-version"] == ["3.11", "3.12"]


def test_reusable_ci_has_no_write_authority():
    workflow = load_yaml(ROOT / ".github/workflows/reusable-ci.yml")
    assert workflow["permissions"] == {"contents": "read"}
    for name, job in workflow["jobs"].items():
        expected = (
            {"contents": "read", "actions": "read"} if name == "setup" else {"contents": "read"}
        )
        assert job.get("permissions", workflow["permissions"]) == expected


def test_reusable_conditions_do_not_use_forbidden_secrets_context():
    workflow = load_yaml(ROOT / ".github/workflows/reusable-ci.yml")
    for item in mappings(workflow):
        assert "secrets." not in item.get("if", "")


def test_pre_commit_job_honors_the_validated_feature_output():
    workflow = load_yaml(ROOT / ".github/workflows/reusable-ci.yml")
    assert workflow["jobs"]["setup"]["outputs"]["pre-commit-enabled"] == (
        "${{ steps.check-features.outputs.pre-commit-enabled }}"
    )
    assert workflow["jobs"]["pre-commit"]["if"] == (
        "needs.setup.outputs.pre-commit-enabled == 'true'"
    )


@pytest.mark.parametrize("job_id", ["test-python", "test-javascript", "test-go"])
def test_coverage_token_is_not_exposed_to_caller_tests(job_id):
    workflow = load_yaml(ROOT / ".github/workflows/reusable-ci.yml")
    job = workflow["jobs"][job_id]
    assert "secrets." not in str(workflow.get("env", {}))
    assert "secrets." not in str(job.get("env", {}))
    steps = job["steps"]
    test_index = next(index for index, step in enumerate(steps) if step.get("name") == "Run tests")
    presence_index = next(
        index for index, step in enumerate(steps) if step.get("id") == "coverage-token"
    )
    assert presence_index > test_index
    assert steps[presence_index]["env"] == {"CODECOV_TOKEN": "${{ secrets.codecov-token }}"}
    assert "GITHUB_ENV" not in steps[presence_index]["run"]
    assert all("secrets." not in str(step.get("env", {})) for step in steps[:presence_index])
    upload = next(step for step in steps if step.get("name") == "Upload coverage")
    assert "steps.coverage-token.outputs.available == 'true'" in upload["if"]
    assert upload["with"]["token"] == "${{ secrets.codecov-token }}"


def test_release_authority_is_scoped_and_cannot_publish_packages():
    workflow = load_yaml(ROOT / ".github/workflows/release.yml")
    assert workflow["permissions"] == {}
    assert workflow["jobs"]["release"]["permissions"] == {"contents": "write"}
    assert "packages" not in str(workflow)


def test_branch_protection_probe_emits_unknown_without_admin_evidence(tmp_path):
    workflow = load_yaml(ROOT / ".github/workflows/repository-health-check.yml")
    steps = workflow["jobs"]["health-check"]["steps"]
    probe = next(step for step in steps if step.get("id") == "branch-protection")
    output = tmp_path / "github-output"
    result = subprocess.run(
        ["bash", "--noprofile", "--norc", "-e", "-c", probe["run"]],
        env={"PATH": os.defpath, "GITHUB_OUTPUT": str(output)},
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert output.read_text(encoding="utf-8").splitlines() == [
        "branch_protected=unknown",
        "evidence_status=not_verified",
    ]
    score = next(step for step in steps if step.get("id") == "health-score")
    assert 'steps.branch-protection.outputs.branch_protected }}" != "true"' in score["run"]


def test_missing_test_tools_are_failures_not_successful_skips():
    workflow = load_yaml(ROOT / ".github/workflows/reusable-ci.yml")
    for job_id in ("test-python", "test-javascript"):
        job = workflow["jobs"][job_id]
        test_step = next(step for step in job["steps"] if step.get("name") == "Run tests")
        assert "skipping" not in test_step["run"]
        assert "exit 1" in test_step["run"]
    java_steps = workflow["jobs"]["test-java"]["steps"]
    assert any(
        step.get("name") == "Reject missing Java test configuration" and "exit 1" in step["run"]
        for step in java_steps
    )


@pytest.mark.parametrize("job_id", ["test-python", "test-javascript"])
def test_actual_test_step_fails_when_test_tools_are_missing(job_id, tmp_path):
    workflow = load_yaml(ROOT / ".github/workflows/reusable-ci.yml")
    steps = workflow["jobs"][job_id]["steps"]
    test_step = next(step for step in steps if step.get("name") == "Run tests")
    # Run only the no-tool branch, using an empty PATH and no production secrets.
    result = subprocess.run(
        ["/bin/bash", "--noprofile", "--norc", "-e", "-c", test_step["run"]],
        env={"PATH": str(tmp_path)},
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 1
    assert "no tests were executed" in result.stdout


@pytest.mark.parametrize(
    "reference", ["actions/checkout@v7", "owner/repo@main", "owner/repo@abc123"]
)
def test_short_or_mutable_pins_are_not_accepted(reference):
    assert COMMIT_PIN.fullmatch(reference) is None
