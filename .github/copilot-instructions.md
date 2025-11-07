# Copilot Instructions for System Governance Framework

## 1. Core Principles & Preferences

### Languages & Tools
- **Python** (default for scripts/automation) - PEP 8 compliant, Python 3.11+
- **Markdown** (documentation) - Consistent headers, proper formatting
- **YAML** (configs/workflows) - 2-space indentation, validated syntax
- **Package Manager**: `pip` with `requirements.txt` or `pyproject.toml`
- **Quality Automation**: `pre-commit` for validation hooks

### Response Style
- Use concise bullet points with minimal preamble
- Provide working code examples with proper imports
- Include inline comments only for complex logic
- Link to specific documentation files when referencing policies
- Follow existing repository patterns and conventions

### Commit Format
Use Conventional Commits specification:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation only
- `chore:` Maintenance tasks
- `refactor:` Code restructuring
- `test:` Testing changes
- `ci:` CI/CD pipeline changes

## 2. Knowledge Base Priority

When answering questions, consult these files in order:

1. **SECURITY.md** → Vulnerability reporting, security policies
2. **CONTRIBUTING.md** → Development setup, contribution workflow, coding standards
3. **CODE_OF_CONDUCT.md** → Community standards, behavior expectations
4. **README.md** → Project overview, features, getting started
5. **GOVERNANCE_ANALYSIS.md** → Governance framework, decision-making processes
6. **.github/workflows/** → CI/CD patterns, automation examples
7. **.pre-commit-config.yaml** → Code quality hook configurations

## 3. Topic-Specific Guidance

### Security (Critical Priority)
- **Always** reference `SECURITY.md` for procedures
- **Never** commit secrets, API keys, tokens, or credentials
- Pin GitHub Action versions for security: `actions/checkout@v4`
- Prioritize security fixes over feature development
- Use Dependabot and GitHub security scanning
- Validate all user inputs in scripts

### Governance & Compliance
- Reference `GOVERNANCE_ANALYSIS.md` for framework alignment
- Document all architectural decisions and policy changes
- Consider impact on existing governance structures
- Maintain transparency in decision-making processes

### Contributions & Community
- Follow `CONTRIBUTING.md` for development workflows
- Adhere to `CODE_OF_CONDUCT.md` expectations
- Use inclusive, welcoming language in all interactions
- Respect code review feedback and iterate constructively

### GitHub Actions & Automation
- Pin action versions: `uses: actions/setup-python@v5`
- Add descriptive `name:` fields to all workflow steps
- Include error handling and appropriate timeouts
- Test workflows in a fork before merging to main branch
- Use workflow dispatch for manual triggers when appropriate

## 4. Best Practices

### Making Changes
- **Scope**: Keep changes minimal and focused
- **Compatibility**: Maintain backward compatibility when possible
- **Documentation**: Update related docs with code changes
- **Testing**: Run `pre-commit run --all-files` before committing
- **Impact**: Consider effects on existing users and contributors

### Managing Dependencies
- Justify necessity before adding new dependencies
- Check for known vulnerabilities (CVEs)
- Prefer well-maintained packages with active communities
- Document in `requirements.txt` or `pyproject.toml`
- Configure Dependabot for automated security updates

### Pre-Commit Validation
Run before every commit:
```bash
pre-commit run --all-files
```
Checks include: `check-yaml`, `check-json`, `end-of-file-fixer`, `trailing-whitespace`, `check-added-large-files`

### File Organization
```
.github/
├── copilot-instructions.md
├── ISSUE_TEMPLATE/          # Issue templates
├── PULL_REQUEST_TEMPLATE/   # PR templates
├── workflows/               # GitHub Actions
└── configs/                 # Additional configurations
```

## 5. Code Examples

### Python Script Template
```python
#!/usr/bin/env python3
"""Brief description of script purpose."""

def main():
    """Main entry point."""
    pass

if __name__ == "__main__":
    main()
```

### GitHub Action Workflow Template
```yaml
name: Descriptive Workflow Name
on: [push, pull_request]
jobs:
  job-name:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Descriptive step name
        run: echo "Command here"
```

---
*Last Updated: 2025-11-07 | Maintained by @ivi374forivi*