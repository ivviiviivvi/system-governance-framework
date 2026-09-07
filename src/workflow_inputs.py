"""Parse workflow data without executing caller strings or importing caller code."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import yaml
from jsonschema import Draft7Validator
from jsonschema.exceptions import ValidationError

# Python is invoked with -I; only this defining-revision directory is added.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import ConfigError, _deep_merge, load_preset, load_schema

MAX_INPUT_BYTES = 1_048_576
LANGUAGES = (
    "python",
    "javascript",
    "typescript",
    "go",
    "java",
    "rust",
    "ruby",
    "php",
    "csharp",
    "swift",
    "kotlin",
    "scala",
)
FLAG_LANGUAGES = ("python", "javascript", "go", "java", "rust", "ruby", "php", "csharp")


class InputError(ValueError):
    """Untrusted workflow data failed admission."""


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if not isinstance(key, str) or key in result:
            raise InputError("Mapping keys must be unique strings")
        result[key] = value
    return result


class UniqueSafeLoader(yaml.SafeLoader):
    """Safe YAML with no duplicate, merge, or non-string mapping keys."""


def unique_mapping(loader, node):
    return unique_pairs(
        (loader.construct_object(key, deep=True), loader.construct_object(value, deep=True))
        for key, value in node.value
    )


UniqueSafeLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def strict_yaml(text):
    if len(text.encode("utf-8")) > MAX_INPUT_BYTES:
        raise InputError("Configuration exceeds size limit")
    for event in yaml.parse(text):
        if isinstance(event, yaml.events.AliasEvent) or getattr(event, "anchor", None):
            raise InputError("YAML aliases and anchors are not admitted")
    value = yaml.load(text, Loader=UniqueSafeLoader)
    if not isinstance(value, dict):
        raise InputError("Configuration must be an object")
    return value


def reject_constant(_value):
    raise InputError("Non-finite JSON values are not admitted")


def strict_json(text):
    if len(text.encode("utf-8")) > MAX_INPUT_BYTES:
        raise InputError("JSON input exceeds size limit")
    return json.loads(text, object_pairs_hook=unique_pairs, parse_constant=reject_constant)


def bounded_root(raw_root, workspace):
    workspace = Path(workspace).resolve(strict=True)
    root = Path(raw_root)
    if not root.is_absolute():
        root = workspace / root
    root = root.resolve(strict=True)
    if not root.is_relative_to(workspace) or not root.is_dir():
        raise InputError("Source root must be a directory inside the workspace")
    return root


def source_file(root, relative):
    relative = Path(relative)
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise InputError("Input path must be relative without parent traversal")
    candidate = root / relative
    if not candidate.resolve().is_relative_to(root):
        raise InputError("Input path escapes the caller source root")
    for part in (candidate, *candidate.parents):
        if part == root:
            break
        if part.is_symlink():
            raise InputError("Symlinked input paths are not admitted")
    return candidate


def read_bounded(path):
    if not path.is_file() or path.stat().st_size > MAX_INPUT_BYTES:
        raise InputError("Input must be a regular file within the size limit")
    return path.read_text(encoding="utf-8")


def validate_config(config):
    Draft7Validator(load_schema()).validate(config)
    json.dumps(config, allow_nan=False)
    return config


def load_config(root, relative, validate="true"):
    if validate != "true":
        raise InputError("Schema validation cannot be disabled")
    path = source_file(root, relative)
    if not path.exists():
        return validate_config(load_preset("standard"))
    override = strict_yaml(read_bounded(path))
    validate_config(override)
    preset = override["framework"].get("preset", "standard")
    return validate_config(_deep_merge(load_preset(preset), override))


def detect_languages(root, override="auto"):
    if override != "auto":
        languages = strict_json(override)
        if (
            not isinstance(languages, list)
            or any(not isinstance(item, str) or item not in LANGUAGES for item in languages)
            or len(languages) != len(set(languages))
        ):
            raise InputError("Language override must be a unique JSON list of supported names")
        return languages
    languages = []
    manifests = {
        "python": ("requirements.txt", "pyproject.toml", "setup.py", "Pipfile"),
        "go": ("go.mod", "go.sum"),
        "java": ("pom.xml", "build.gradle", "build.gradle.kts"),
        "rust": ("Cargo.toml",),
        "ruby": ("Gemfile",),
        "php": ("composer.json",),
        "swift": ("Package.swift",),
    }
    for language, names in manifests.items():
        if any(source_file(root, name).is_file() for name in names):
            languages.append(language)
    package = source_file(root, "package.json")
    if package.exists():
        data = strict_json(read_bounded(package))
        if not isinstance(data, dict):
            raise InputError("package.json must contain an object")
        has_typescript = False
        for field in ("dependencies", "devDependencies", "peerDependencies"):
            dependencies = data.get(field, {})
            if not isinstance(dependencies, dict):
                raise InputError("Package dependency fields must be objects")
            has_typescript |= "typescript" in dependencies
        languages.append("typescript" if has_typescript else "javascript")
    for pattern, language in (("*.gemspec", "ruby"), ("*.csproj", "csharp"), ("*.sln", "csharp")):
        for candidate in root.glob(pattern):
            if source_file(root, candidate.name).is_file() and language not in languages:
                languages.append(language)
    return languages


def compact(value):
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), allow_nan=False)


def language_outputs(languages):
    outputs = {"languages": compact(languages)}
    for language in FLAG_LANGUAGES:
        selected = language in languages or (language == "javascript" and "typescript" in languages)
        outputs[f"has-{language}"] = str(selected).lower()
    outputs["summary"] = (
        "Detected languages: " + ", ".join(languages) if languages else "No languages detected"
    )
    return outputs


def feature_outputs(config, coverage="auto"):
    validate_config(config)
    if coverage not in {"auto", "true", "false"}:
        raise InputError("Coverage override must be auto, true, or false")
    ci = config.get("features", {}).get("ci", {})
    enabled = ci.get("enabled", True)
    enabled_coverage = ci.get("test-coverage", True) if coverage == "auto" else coverage == "true"
    return {"ci-enabled": str(enabled).lower(), "coverage-enabled": str(enabled_coverage).lower()}


def emit_outputs(outputs, destination):
    for key, value in outputs.items():
        if not isinstance(value, str) or any(char in value for char in "\r\n"):
            raise InputError("Output values must be safely encoded single lines")
        if not key or any(char not in "abcdefghijklmnopqrstuvwxyz-" for char in key):
            raise InputError("Invalid output key")
    with Path(destination).open("a", encoding="utf-8") as handle:
        handle.write("".join(f"{key}={value}\n" for key, value in outputs.items()))


def main():
    try:
        operation = sys.argv[1]
        if operation == "features":
            outputs = feature_outputs(
                strict_json(os.environ["GOVERNANCE_CONFIG_JSON"]),
                os.environ.get("GOVERNANCE_COVERAGE", "auto"),
            )
        else:
            root = bounded_root(
                os.environ.get("GOVERNANCE_SOURCE_ROOT", "."),
                os.environ["GITHUB_WORKSPACE"],
            )
            if operation == "load-config":
                config = load_config(
                    root,
                    os.environ.get("GOVERNANCE_CONFIG_PATH", ".github/governance.yml"),
                    os.environ.get("GOVERNANCE_VALIDATE", "true"),
                )
                outputs = {
                    "config": compact(config),
                    "preset": config["framework"]["preset"],
                    "version": config["framework"]["version"],
                    "valid": "true",
                }
            elif operation == "detect-languages":
                outputs = language_outputs(
                    detect_languages(root, os.environ.get("GOVERNANCE_LANGUAGES", "auto"))
                )
            else:
                raise InputError("Unknown workflow input operation")
        emit_outputs(outputs, os.environ["GITHUB_OUTPUT"])
    except (
        InputError,
        ConfigError,
        ValidationError,
        yaml.YAMLError,
        ValueError,
        TypeError,
        OSError,
        KeyError,
        IndexError,
        RecursionError,
    ):
        print("::error::Workflow input validation failed; no outputs were admitted.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
