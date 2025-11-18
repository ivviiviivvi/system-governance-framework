# System Governance Framework: Product Architecture

## Vision: Framework-as-Code (FaC)

Transform from copy-paste template to consumable product that users import and configure rather than fork.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     USER REPOSITORY                         │
├─────────────────────────────────────────────────────────────┤
│  .github/                                                   │
│    └── governance.yml          ← Single config file         │
│                                                             │
│  .github/workflows/                                         │
│    ├── governance-ci.yml       ← Thin wrapper               │
│    ├── governance-security.yml ← Calls remote workflows     │
│    └── governance-quality.yml  ← Minimal local footprint    │
│                                                             │
│  [Your actual project code...]                              │
└─────────────────────────────────────────────────────────────┘
                        ↓ imports from ↓
┌─────────────────────────────────────────────────────────────┐
│   SYSTEM-GOVERNANCE-FRAMEWORK (This Product)                │
├─────────────────────────────────────────────────────────────┤
│  .github/workflows/                                         │
│    ├── reusable-ci.yml         ← Reusable workflows         │
│    ├── reusable-security.yml   ← Called remotely            │
│    ├── reusable-quality.yml    ← Version-pinnable           │
│    └── ...                                                  │
│                                                             │
│  .github/actions/                                           │
│    ├── detect-languages/       ← Composite actions          │
│    ├── security-scan/          ← Reusable components        │
│    └── quality-check/          ← Atomic operations          │
│                                                             │
│  scripts/                                                   │
│    ├── install-framework.sh    ← Installation CLI           │
│    ├── update-framework.sh     ← Upgrade mechanism          │
│    └── validate-config.js      ← Config validator           │
│                                                             │
│  config/                                                    │
│    ├── schema.json             ← Config validation schema   │
│    ├── presets/                ← Pre-configured profiles    │
│    │   ├── minimal.yml                                      │
│    │   ├── standard.yml                                     │
│    │   └── enterprise.yml                                   │
│    └── defaults.yml            ← Default values             │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Principles

### 1. **Import, Don't Copy**
Users reference workflows from this repo, not copy them:

```yaml
# User's .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  governance:
    uses: 4-b100m/system-governance-framework/.github/workflows/reusable-ci.yml@v3.0.0
    with:
      config-path: '.github/governance.yml'
    secrets: inherit
```

### 2. **Configure, Don't Code**
Single configuration file defines all behavior:

```yaml
# User's .github/governance.yml
framework:
  version: "3.0.0"
  preset: "standard"  # minimal | standard | enterprise

project:
  languages: [python, javascript]
  frameworks: [django, react]

features:
  ci:
    enabled: true
    test-coverage: true

  security:
    enabled: true
    codeql: true
    dependency-scan: true

  quality:
    enabled: true
    linting: true
    pre-commit: true
```

### 3. **Version Everything**
Users pin to specific versions for stability:

```yaml
uses: 4-b100m/system-governance-framework/.github/workflows/reusable-ci.yml@v3.0.0
                                                                          ^^^^^^^^
```

### 4. **Update Transparently**
Built-in update mechanism with changelog review:

```bash
$ npx @sgf/cli update
Current version: v2.5.0
Latest version: v3.0.0

Changelog:
  - Added TypeScript support
  - Improved CodeQL performance
  - BREAKING: Removed Python 2.7 support

Proceed with update? [y/N]
```

### 5. **Graceful Degradation**
Features auto-disable when not applicable:

```yaml
# User has Python project → Python tests run
# User has no Go code → Go workflows skip automatically
# No CodeQL token → Security scan runs in free mode
```

---

## Product Components

### A. **Reusable Workflows** (`.github/workflows/reusable-*.yml`)

**Purpose**: Core workflow logic that users call remotely

**Example**: Reusable CI Workflow

```yaml
# .github/workflows/reusable-ci.yml
name: Reusable CI Workflow
on:
  workflow_call:
    inputs:
      config-path:
        required: false
        type: string
        default: '.github/governance.yml'
      languages:
        required: false
        type: string
        default: 'auto'
    secrets:
      codecov-token:
        required: false

jobs:
  setup:
    runs-on: ubuntu-latest
    outputs:
      config: ${{ steps.load-config.outputs.config }}
      languages: ${{ steps.detect.outputs.languages }}
    steps:
      - uses: actions/checkout@v4

      - name: Load governance config
        id: load-config
        uses: 4-b100m/system-governance-framework/.github/actions/load-config@v3.0.0
        with:
          config-path: ${{ inputs.config-path }}

      - name: Detect languages
        id: detect
        uses: 4-b100m/system-governance-framework/.github/actions/detect-languages@v3.0.0
        with:
          override: ${{ inputs.languages }}

  test:
    needs: setup
    if: fromJSON(needs.setup.outputs.config).features.ci.enabled
    uses: 4-b100m/system-governance-framework/.github/workflows/reusable-test.yml@v3.0.0
    with:
      languages: ${{ needs.setup.outputs.languages }}
      coverage: ${{ fromJSON(needs.setup.outputs.config).features.ci.test-coverage }}
    secrets: inherit
```

### B. **Composite Actions** (`.github/actions/*/action.yml`)

**Purpose**: Reusable building blocks for workflows

**Example**: Language Detection Action

```yaml
# .github/actions/detect-languages/action.yml
name: Detect Project Languages
description: Automatically detect programming languages in repository

outputs:
  languages:
    description: JSON array of detected languages
    value: ${{ steps.detect.outputs.languages }}
  has-python:
    description: Whether Python code detected
    value: ${{ steps.detect.outputs.has-python }}
  has-javascript:
    description: Whether JavaScript code detected
    value: ${{ steps.detect.outputs.has-javascript }}

runs:
  using: composite
  steps:
    - name: Detect languages
      id: detect
      shell: bash
      run: |
        LANGUAGES=[]

        if [[ -f "requirements.txt" || -f "pyproject.toml" || -f "setup.py" ]]; then
          LANGUAGES=$(echo $LANGUAGES | jq '. + ["python"]')
          echo "has-python=true" >> $GITHUB_OUTPUT
        fi

        if [[ -f "package.json" ]]; then
          LANGUAGES=$(echo $LANGUAGES | jq '. + ["javascript"]')
          echo "has-javascript=true" >> $GITHUB_OUTPUT
        fi

        echo "languages=$LANGUAGES" >> $GITHUB_OUTPUT
```

### C. **Configuration System**

**Config Schema** (`config/schema.json`):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["framework", "project"],
  "properties": {
    "framework": {
      "type": "object",
      "properties": {
        "version": {
          "type": "string",
          "pattern": "^v?\\d+\\.\\d+\\.\\d+$",
          "description": "Framework version to use"
        },
        "preset": {
          "type": "string",
          "enum": ["minimal", "standard", "enterprise"],
          "default": "standard"
        }
      }
    },
    "project": {
      "type": "object",
      "properties": {
        "languages": {
          "type": "array",
          "items": {
            "type": "string",
            "enum": ["python", "javascript", "typescript", "go", "java", "rust", "ruby", "php", "csharp", "swift"]
          }
        }
      }
    },
    "features": {
      "type": "object",
      "properties": {
        "ci": {
          "$ref": "#/definitions/featureToggle"
        },
        "security": {
          "$ref": "#/definitions/featureToggle"
        },
        "quality": {
          "$ref": "#/definitions/featureToggle"
        }
      }
    }
  },
  "definitions": {
    "featureToggle": {
      "type": "object",
      "properties": {
        "enabled": {
          "type": "boolean",
          "default": true
        }
      }
    }
  }
}
```

**Preset Configurations**:

```yaml
# config/presets/minimal.yml
framework:
  preset: minimal

features:
  ci:
    enabled: true
    test-coverage: false

  security:
    enabled: false

  quality:
    enabled: true
    linting: true
    pre-commit: false

dependabot:
  enabled: false
```

```yaml
# config/presets/standard.yml
framework:
  preset: standard

features:
  ci:
    enabled: true
    test-coverage: true

  security:
    enabled: true
    codeql: true
    dependency-scan: true

  quality:
    enabled: true
    linting: true
    pre-commit: true

dependabot:
  enabled: true
  schedule: weekly
```

```yaml
# config/presets/enterprise.yml
framework:
  preset: enterprise

features:
  ci:
    enabled: true
    test-coverage: true
    parallel-jobs: 5

  security:
    enabled: true
    codeql: true
    semgrep: true
    dependency-scan: true
    license-check: true
    security-scorecard: true

  quality:
    enabled: true
    linting: true
    pre-commit: true
    super-linter: true

dependabot:
  enabled: true
  schedule: daily
  auto-merge: patch

compliance:
  enabled: true
  soc2: true
  gdpr: true
```

### D. **Installation CLI**

**Tool**: `@sgf/cli` npm package

```bash
# Install framework
npx @sgf/cli install

# Interactive setup
npx @sgf/cli init

# Update to latest
npx @sgf/cli update

# Validate configuration
npx @sgf/cli validate

# Check framework health
npx @sgf/cli doctor
```

**Installation Script** (`scripts/install-framework.sh`):

```bash
#!/bin/bash
set -e

VERSION=${1:-latest}
PRESET=${2:-standard}

echo "🚀 System Governance Framework Installer"
echo "========================================"
echo ""
echo "Version: $VERSION"
echo "Preset: $PRESET"
echo ""

# Detect if in git repo
if [ ! -d ".git" ]; then
  echo "❌ Error: Not in a git repository"
  exit 1
fi

# Create .github directory if needed
mkdir -p .github/workflows

# Download governance config
echo "📥 Downloading configuration..."
curl -sSL https://raw.githubusercontent.com/4-b100m/system-governance-framework/$VERSION/config/presets/$PRESET.yml \
  -o .github/governance.yml

# Create wrapper workflows
echo "⚙️  Setting up workflows..."

cat > .github/workflows/governance-ci.yml <<'EOF'
name: Governance - CI
on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  ci:
    uses: 4-b100m/system-governance-framework/.github/workflows/reusable-ci.yml@VERSION
    with:
      config-path: '.github/governance.yml'
    secrets: inherit
EOF

sed -i "s/VERSION/$VERSION/g" .github/workflows/governance-ci.yml

# Detect project languages
echo "🔍 Detecting project languages..."
LANGUAGES=()

[[ -f "requirements.txt" ]] && LANGUAGES+=("python")
[[ -f "package.json" ]] && LANGUAGES+=("javascript")
[[ -f "go.mod" ]] && LANGUAGES+=("go")
[[ -f "pom.xml" || -f "build.gradle" ]] && LANGUAGES+=("java")

# Update config with detected languages
if [ ${#LANGUAGES[@]} -gt 0 ]; then
  echo "  Found: ${LANGUAGES[*]}"
  # Update YAML with detected languages
  # (Would use yq or similar in production)
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Review .github/governance.yml and customize as needed"
echo "  2. Commit the changes: git add .github && git commit -m 'chore: Add governance framework'"
echo "  3. Push to GitHub: git push"
echo ""
echo "Documentation: https://github.com/4-b100m/system-governance-framework#readme"
```

### E. **Version Management**

**Semantic Versioning**:
- `v1.x.x` - Initial template version
- `v2.x.x` - Enhanced template with analysis
- `v3.x.x` - **Framework-as-Code product** (this transformation)

**Release Process**:
1. Version bump in `package.json` and `VERSION` file
2. Update `CHANGELOG.md` with changes
3. Tag release: `git tag v3.0.0`
4. GitHub Actions auto-publishes npm package
5. Release notes generated from conventional commits

**Compatibility Matrix**:

| Framework Version | Min GitHub Actions | Supported Languages |
|-------------------|-------------------|---------------------|
| v3.0.0+          | v4.0+             | Python, JS, Go, Java, Rust, Ruby, PHP, C#, Swift |
| v2.0.0-v2.9.9    | v3.0+             | Template only       |

---

## Migration Path (v2 → v3)

### For Existing Template Users

```bash
# Current state: Forked repository with copied files
# Desired state: Lightweight config + remote workflow calls

# 1. Backup existing customizations
git checkout -b backup/v2-template

# 2. Run migration script
npx @sgf/cli migrate from-template

# Migration script will:
#   - Analyze current .github/ setup
#   - Extract customizations to governance.yml
#   - Replace local workflows with remote calls
#   - Preserve custom workflows/actions
#   - Create migration report

# 3. Review changes
git diff main

# 4. Test new setup
git checkout -b feature/migrate-to-v3
# ... test CI runs ...

# 5. Commit migration
git commit -m "chore: Migrate to Framework-as-Code v3"
```

### For New Users

```bash
# Simply install the framework
cd my-existing-project
npx @sgf/cli install

# Or during project creation
npx @sgf/cli init my-new-project
```

---

## Business Model

### Open Core Strategy

**Free Tier** (MIT License):
- Core workflows (CI, basic security)
- Community support
- Public repositories only

**Pro Tier** ($29/month per organization):
- Advanced security (Semgrep Pro, FOSSA integration)
- Compliance workflows (SOC2, GDPR, HIPAA)
- Private repository support
- Priority support
- SLA guarantees

**Enterprise Tier** (Custom pricing):
- On-premise deployment
- Custom workflow development
- Dedicated support
- Security audit assistance
- Training & onboarding

### Revenue Projections

**Year 1**:
- Free users: 1,000 organizations
- Pro users: 50 organizations ($17,400/year)
- Enterprise: 3 clients ($150,000/year)
- **Total**: ~$167,000

**Year 2**:
- Free users: 5,000 organizations
- Pro users: 250 organizations ($87,000/year)
- Enterprise: 10 clients ($500,000/year)
- **Total**: ~$587,000

---

## Success Metrics

### Product KPIs

**Adoption**:
- Installations per month
- Active users (monthly workflow runs)
- Retention rate (still using after 6 months)

**Quality**:
- Security issues detected per 1000 commits
- Average CI run time
- False positive rate
- User satisfaction (NPS score)

**Growth**:
- GitHub stars
- Monthly recurring revenue (MRR)
- Community contributions
- Documentation views

### Technical Metrics

**Performance**:
- Workflow execution time: < 5 minutes (p50), < 15 minutes (p95)
- Cache hit rate: > 80%
- Failure rate: < 5%

**Security**:
- Vulnerability detection rate: > 95% (vs manual audit)
- Time to detection: < 24 hours
- False positive rate: < 10%

---

## Roadmap

### v3.0.0 - Framework-as-Code Launch (Q1 2026)
- ✅ Reusable workflow architecture
- ✅ Configuration system
- ✅ Installation CLI
- ✅ Migration tools
- ✅ Core language support (Python, JS, Go, Java)

### v3.1.0 - Enhanced Language Support (Q2 2026)
- Rust, Ruby, PHP, C#, Swift support
- Framework-specific presets (Django, React, Rails, etc.)
- Custom action marketplace

### v3.2.0 - Advanced Security (Q3 2026)
- Semgrep Pro integration
- License compliance automation
- Supply chain security (SLSA)
- Secrets scanning enhancements

### v3.3.0 - Compliance Automation (Q4 2026)
- SOC2 workflow templates
- GDPR compliance checking
- HIPAA audit trails
- ISO 27001 evidence collection

### v4.0.0 - AI-Powered Governance (Q1 2027)
- AI-assisted code review
- Intelligent test generation
- Auto-fix security vulnerabilities
- Predictive risk scoring

---

## Architecture Decisions

### ADR-001: Why Reusable Workflows vs GitHub Apps?

**Decision**: Use reusable workflows instead of GitHub App

**Rationale**:
- ✅ No OAuth installation friction
- ✅ Users maintain full control
- ✅ Works in private repos without app permissions
- ✅ Transparent execution (visible in Actions tab)
- ❌ Cons: Requires workflow files in user repos (minimal overhead)

### ADR-002: Why YAML Config vs JSON?

**Decision**: Use YAML for user configuration

**Rationale**:
- ✅ More human-readable
- ✅ Supports comments
- ✅ Consistent with GitHub Actions ecosystem
- ✅ JSON schema validation still possible

### ADR-003: Why npm CLI vs Shell Script?

**Decision**: Provide both npm package and shell script

**Rationale**:
- npm package: Full-featured, cross-platform, auto-updates
- Shell script: Zero-dependency bootstrap, works without Node
- Best of both worlds approach

---

## Competitive Analysis

| Feature | SGF v3 | GitHub's Default | Renovate | Snyk | Dependabot |
|---------|--------|------------------|----------|------|------------|
| **Configuration** | Single YAML | Multiple files | JSON | Web UI | YAML |
| **Extensibility** | High | Medium | Medium | Low | Low |
| **Security Scanning** | Multi-tool | Basic | No | Yes | Yes |
| **Cost** | Free + Pro | Free | Free + Pro | Paid | Free |
| **Language Support** | 10+ | All | All | Limited | All |
| **On-premise** | Yes (Enterprise) | No | Yes | Yes | No |
| **Learning Curve** | Medium | Low | Medium | Low | Low |

**Differentiation**:
- Only solution combining CI + Security + Quality + Compliance in one framework
- Open-source core with commercial extensions
- Opinionated best practices out-of-the-box
- Framework-as-Code pattern (import vs install)

---

## Technical Debt Prevention

### Code Organization
```
.github/
  actions/           # Composite actions
  workflows/         # Reusable workflows
config/              # Configuration schemas & presets
scripts/             # Installation & management tools
docs/                # Product documentation
tests/               # Framework self-tests
examples/            # Example integrations
```

### Testing Strategy
- Unit tests for configuration parsing
- Integration tests for workflow execution
- End-to-end tests with sample projects
- Performance regression testing
- Security scanning of framework itself

### Documentation Standards
- API documentation for all inputs/outputs
- Migration guides for each major version
- Troubleshooting runbooks
- Video tutorials for common tasks

---

## Conclusion

This architecture transforms the framework from a **template** (copy-paste) to a **product** (import-configure-use), enabling:

1. **Centralized Updates**: Fix once, benefit everywhere
2. **Version Stability**: Pin to versions, upgrade intentionally
3. **Reduced Maintenance**: Less code in user repos
4. **Easier Adoption**: Install script vs manual setup
5. **Monetization**: Pro/Enterprise tiers for sustainability

**Next Steps**: Begin implementation of reusable workflows and configuration system.
