# System Governance Framework v3.0

**Framework-as-Code** for modern software development: Import, configure, and enforce best practices for CI/CD, security, and code quality.

[![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)](https://github.com/4-b100m/system-governance-framework/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Framework](https://img.shields.io/badge/framework-as--code-orange.svg)](PRODUCT_ARCHITECTURE.md)

---

## 🚀 What is This?

Unlike traditional templates you copy and maintain, the **System Governance Framework** is a **product** you **import** and **configure**. Your repository stays lightweight while leveraging centralized, maintained workflows.

### Template (v2) vs Product (v3)

| Aspect | v2 Template | v3 Framework-as-Code |
|--------|-------------|----------------------|
| **Adoption** | Fork & copy files | Run installer |
| **Updates** | Manual merge | Bump version number |
| **Customization** | Edit workflow files | Edit single config file |
| **Maintenance** | You maintain workflows | We maintain workflows |
| **Repository Size** | Large (.github/* copied) | Minimal (config only) |
| **Upgrade Path** | Complex merges | Change version pin |

---

## ⚡ Quick Start

### One-Line Installation

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/4-b100m/system-governance-framework/v3.0.0/scripts/install-framework.sh)
```

### What Gets Created

```
your-repository/
├── .github/
│   ├── governance.yml              ← Your configuration (customize this)
│   └── workflows/
│       ├── governance-ci.yml       ← Thin wrapper (calls remote workflow)
│       └── governance-security.yml ← Thin wrapper
```

That's it! **2 workflow files** + **1 config file** = Full governance framework.

---

## 📝 Configuration

### Single File Controls Everything

Edit `.github/governance.yml`:

```yaml
framework:
  version: "3.0.0"           # Pin to specific version
  preset: "standard"         # minimal | standard | enterprise

project:
  languages: [python, javascript]  # Auto-detected if omitted

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
    schedule: "weekly"
```

### Available Presets

#### Minimal (`preset: minimal`)
- Basic CI with testing
- Essential dependency scanning
- Simple linting
- **Best for**: Prototypes, personal projects, small teams

#### Standard (`preset: standard`) ⭐ **Recommended**
- Full CI/CD with coverage
- CodeQL security scanning
- Pre-commit hooks
- Dependabot automation
- **Best for**: Team projects, open-source, production apps

#### Enterprise (`preset: enterprise`)
- All Standard features
- Advanced security (Semgrep, license checks)
- Compliance automation (SOC2, GDPR)
- Maximum parallelization
- **Best for**: Enterprise apps, regulated industries

---

## 🎯 How It Works

### Traditional Approach (v2)

```yaml
# Your repository contains full workflow logic
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -r requirements.txt
      - run: pytest
      # ... 50+ more lines ...
```

**Problems**:
- ❌ Duplicate workflow logic across projects
- ❌ Manual updates when best practices change
- ❌ Large .github/ directory
- ❌ Complex maintenance

### Framework-as-Code (v3) ✅

```yaml
# Your repository just calls the framework
name: CI
on: [push]
jobs:
  ci:
    uses: 4-b100m/system-governance-framework/.github/workflows/reusable-ci.yml@v3.0.0
    with:
      config-path: '.github/governance.yml'
    secrets: inherit
```

**Benefits**:
- ✅ 5 lines vs 50+ lines
- ✅ Updates via version bump
- ✅ Minimal repository footprint
- ✅ Centralized maintenance

---

## 🔧 Usage Guide

### Step 1: Install

```bash
# In your repository root
bash <(curl -fsSL https://raw.githubusercontent.com/4-b100m/system-governance-framework/v3.0.0/scripts/install-framework.sh)

# Or specify version and preset
bash <(curl -fsSL https://raw.githubusercontent.com/4-b100m/system-governance-framework/v3.0.0/scripts/install-framework.sh) v3.0.0 minimal
```

### Step 2: Configure

Edit `.github/governance.yml` to match your needs:

```yaml
project:
  languages: [python]  # Your languages

features:
  ci:
    test-coverage: true   # Enable/disable features
```

### Step 3: Commit & Push

```bash
git add .github/
git commit -m "chore: Add governance framework v3.0.0"
git push
```

### Step 4: Watch It Work

Visit your GitHub Actions tab and watch automated workflows run!

---

## 🔄 Updating

### Bump Version

```yaml
# .github/workflows/governance-ci.yml
uses: 4-b100m/system-governance-framework/.github/workflows/reusable-ci.yml@v3.1.0
#                                                                          ^^^^^^
#                                                                          Change this
```

### View Changelog

```bash
# See what's new in v3.1.0
curl -s https://raw.githubusercontent.com/4-b100m/system-governance-framework/v3.1.0/CHANGELOG.md
```

### Migration Guide

When new major versions are released, we provide migration guides:

- [v2 → v3 Migration Guide](docs/migration-v2-to-v3.md)

---

## 🎨 Customization

### Override Language Detection

```yaml
# .github/workflows/governance-ci.yml
jobs:
  ci:
    uses: 4-b100m/system-governance-framework/.github/workflows/reusable-ci.yml@v3.0.0
    with:
      languages: '["python", "typescript"]'  # Manual override
```

### Add Custom Workflows

Keep custom workflows alongside framework workflows:

```
.github/workflows/
├── governance-ci.yml       ← Framework CI
├── governance-security.yml ← Framework Security
└── custom-deploy.yml       ← Your custom workflow
```

### Extend Pre-commit

The framework uses standard `.pre-commit-config.yaml`:

```yaml
# Add your own hooks
repos:
  # Framework hooks (auto-detected)
  - repo: https://github.com/pre-commit/pre-commit-hooks
    # ...

  # Your custom hooks
  - repo: https://github.com/myorg/my-hooks
    rev: v1.0.0
    hooks:
      - id: custom-check
```

---

## 🔐 Required Secrets (Optional)

Some features require GitHub repository secrets:

### Codecov (Optional)
For coverage reporting:
1. Get token from [codecov.io](https://codecov.io)
2. Add as `CODECOV_TOKEN` secret

### Semgrep (Pro Feature)
For advanced security scanning:
1. Get token from [semgrep.dev](https://semgrep.dev)
2. Add as `SEMGREP_APP_TOKEN` secret

**Note**: Workflows gracefully degrade without these secrets.

---

## 📊 What Gets Automated

### ✅ Continuous Integration
- Auto-detect languages (Python, JS, Go, Java, Rust, etc.)
- Run tests with appropriate test runners
- Generate and upload coverage reports
- Cache dependencies for faster builds

### 🔒 Security Scanning
- **CodeQL**: Static security analysis
- **Dependency Scan**: Vulnerability detection
- **Secret Scan**: Pre-commit key detection
- **Semgrep** (Pro): Advanced security rules
- **OSSF Scorecard** (Enterprise): Security posture

### 🎯 Quality Enforcement
- **Pre-commit Hooks**: 12+ quality checks
- **Linting**: Multi-language code quality
- **Formatting**: Consistent code style
- **Super-Linter** (Optional): Comprehensive linting

### 🔄 Dependency Management
- **Dependabot**: Automated update PRs
- **License Compliance** (Pro): License validation
- **Auto-merge** (Enterprise): Patch updates

---

## 💰 Pricing

### Free (Open Source)
- Core CI/CD workflows
- Basic security scanning (CodeQL)
- Quality enforcement
- Public repositories
- Community support

### Pro ($29/month per organization)
- Advanced security (Semgrep Pro)
- License compliance (FOSSA)
- Private repository support
- Priority support
- Early access to features

### Enterprise (Custom)
- All Pro features
- Compliance automation (SOC2, GDPR, HIPAA)
- On-premise deployment
- Custom workflow development
- Dedicated support & SLA
- Training & onboarding

[Get Started →](https://github.com/4-b100m/system-governance-framework#pricing)

---

## 🤝 Support

### Documentation
- [Full Documentation](https://github.com/4-b100m/system-governance-framework#readme)
- [Configuration Schema](config/schema.json)
- [Product Architecture](PRODUCT_ARCHITECTURE.md)
- [Examples](examples/)

### Community
- [GitHub Discussions](https://github.com/4-b100m/system-governance-framework/discussions) - Questions & ideas
- [Issue Tracker](https://github.com/4-b100m/system-governance-framework/issues) - Bug reports
- [Changelog](CHANGELOG.md) - What's new

### Professional Support
- Email: support@4-b100m.dev
- Response time: 24-48 hours (Free), 4 hours (Pro), 1 hour (Enterprise)

---

## 🔬 Comparison

### vs GitHub's Default Templates
- ✅ More opinionated (best practices built-in)
- ✅ Centrally maintained (updates via version bump)
- ✅ Multi-language support out-of-the-box
- ✅ Security-first approach

### vs Renovate/Dependabot
- ✅ Full CI/CD + security + quality (not just dependencies)
- ✅ Single configuration file
- ✅ Framework approach (vs point solutions)

### vs Custom Workflows
- ✅ Less maintenance overhead
- ✅ Proven best practices
- ✅ Regular updates and improvements
- ❌ Less flexible (trade-off for simplicity)

---

## 📈 Success Stories

> "Reduced our .github/ directory from 500+ lines to 20 lines. Updates are now a version bump instead of hours of work."
> — **Tech Lead, SaaS Startup**

> "Framework-as-Code pattern cut our governance maintenance time by 80%."
> — **DevOps Engineer, Enterprise**

[Share your story →](https://github.com/4-b100m/system-governance-framework/discussions/categories/success-stories)

---

## 🗺️ Roadmap

### v3.1 (Q2 2026)
- Rust, Ruby, PHP native support
- Framework-specific presets (Django, Rails, etc.)
- Slack/Discord notification integrations

### v3.2 (Q3 2026)
- Advanced Semgrep rules
- Supply chain security (SLSA)
- Performance regression detection

### v3.3 (Q4 2026)
- SOC2 automation
- GDPR compliance checking
- Audit trail generation

### v4.0 (Q1 2027)
- AI-assisted code review
- Intelligent test generation
- Auto-fix security vulnerabilities

[Full Roadmap →](https://github.com/4-b100m/system-governance-framework/projects/1)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

Framework is free and open-source. Pro/Enterprise features require subscription.

---

## 🙏 Credits

Built with ❤️ by the open-source community.

Special thanks to:
- GitHub Actions team for reusable workflows
- All contributors and early adopters
- Security researchers for vulnerability reports

[Become a sponsor →](https://github.com/sponsors/4-b100m)

---

**Ready to transform your governance?**

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/4-b100m/system-governance-framework/v3.0.0/scripts/install-framework.sh)
```

🚀 **Let's build better software together!**
