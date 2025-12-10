# Contributing to System Governance Framework

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Getting Started

1. **Fork the repository** and clone it locally
2. **Create a branch** for your changes: `git checkout -b feature/your-feature-name`
3. **Install pre-commit hooks**: `pip install pre-commit && pre-commit install`
4. **Make your changes** following the guidelines below
5. **Test your changes** locally
6. **Submit a pull request**

## Development Setup

### Prerequisites
- Python 3.11+ (for pre-commit hooks)
- Git

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/system-governance-framework.git
cd system-governance-framework

# Install pre-commit
pip install pre-commit
pre-commit install

# Test pre-commit setup
pre-commit run --all-files
```

## Guidelines

### Code Quality

- All commits must pass pre-commit checks
- Files must end with a newline
- No trailing whitespace
- YAML and JSON files must be valid
- No private keys or secrets in code

### Commit Messages

Use clear, descriptive commit messages:
- `feat: Add new feature`
- `fix: Fix bug in X`
- `docs: Update documentation`
- `chore: Update dependencies`
- `refactor: Restructure code`

### Pull Requests

1. Fill out the pull request template completely
2. Link to any related issues
3. Ensure CI checks pass
4. Request review from code owners
5. Respond to feedback promptly

### Issue Reporting

Use the appropriate issue template:
- **Bug Report**: For reporting bugs
- **Feature Request**: For suggesting enhancements
- **Question**: For asking questions

Include:
- Clear description
- Steps to reproduce (for bugs)
- Expected vs actual behavior
- Relevant logs or screenshots

## Code of Conduct

Please be respectful and constructive in all interactions. We aim to maintain a welcoming and inclusive community.

### Expected Behavior
- Be respectful and professional
- Accept constructive criticism gracefully
- Focus on what's best for the project
- Show empathy toward others

### Unacceptable Behavior
- Harassment or discrimination
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information

## Review Process

1. **Initial Review**: Code owners review PRs
2. **Feedback**: Address requested changes
3. **Approval**: At least one approval required
4. **Merge**: Code owners merge approved PRs

## Questions?

- Check existing issues and discussions
- Use the Question issue template
- Reach out in GitHub Discussions

Thank you for contributing! 🎉
