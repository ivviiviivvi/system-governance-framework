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
Thank you for your interest in contributing to the System Governance Framework! We welcome contributions from the community and are pleased to have you join us.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Submitting Changes](#submitting-changes)
- [Style Guidelines](#style-guidelines)
- [Community](#community)

## 📜 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to our maintainers.

## 🚀 Getting Started

### Ways to Contribute

- **🐛 Report bugs** - Help us identify and fix issues
- **💡 Suggest features** - Propose new functionality or improvements
- **📝 Improve documentation** - Help make our docs better
- **🔧 Submit code changes** - Fix bugs or implement features
- **🎨 Design improvements** - Enhance user experience
- **🧪 Add tests** - Improve our test coverage
- **🔍 Review pull requests** - Help evaluate contributions

### Before You Start

1. **Search existing issues** to see if your bug/feature is already reported
2. **Read our documentation** to understand the project structure
3. **Check our project roadmap** to see planned features
4. **Join our discussions** to connect with other contributors

## 🛠️ How to Contribute

### Reporting Bugs

Use our [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) and include:

- **Clear description** of the issue
- **Steps to reproduce** the problem
- **Expected vs actual behavior**
- **Environment information** (OS, browser, versions)
- **Screenshots or logs** if applicable

### Suggesting Features

Use our [feature request template](.github/ISSUE_TEMPLATE/feature_request.md) and include:

- **Clear description** of the proposed feature
- **Use case** and motivation
- **Detailed specification** of expected behavior
- **Acceptance criteria** for implementation

### Documentation Improvements

- Fix typos, clarify instructions
- Add missing documentation
- Improve code comments
- Update outdated information
- Add examples and tutorials

## 💻 Development Setup

### Prerequisites

- Git
- Your preferred code editor
- Basic understanding of YAML (for GitHub Actions)
- Familiarity with your target programming language

### Fork and Clone

1. **Fork** this repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/system-governance-framework.git
   cd system-governance-framework
   ```
3. **Add upstream** remote:
   ```bash
   git remote add upstream https://github.com/4-b100m/system-governance-framework.git
   ```

### Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Adding tests
- `chore/` - Maintenance tasks

## 📤 Submitting Changes

### Pull Request Process

1. **Ensure your changes work** and don't break existing functionality
2. **Add tests** if you're introducing new features
3. **Update documentation** if needed
4. **Follow our coding standards** (see Style Guidelines)
5. **Create a pull request** using our [PR template](.github/PULL_REQUEST_TEMPLATE/pull_request_template.md)

### PR Requirements

- [ ] **Clear title** describing the change
- [ ] **Detailed description** of what was changed and why
- [ ] **Link to related issues** (e.g., "Closes #123")
- [ ] **Tests pass** (our CI will verify this)
- [ ] **Code is documented** where necessary
- [ ] **Breaking changes** are clearly marked

### Review Process

1. **Automated checks** run automatically (CI, linting, security scans)
2. **Maintainer review** - We'll review your PR and provide feedback
3. **Address feedback** - Make requested changes if needed
4. **Final approval** - Once approved, we'll merge your PR

## 🎨 Style Guidelines

### General Principles

- **Clarity over cleverness** - Write code that's easy to understand
- **Consistency** - Follow existing patterns in the codebase
- **Documentation** - Comment complex logic and public interfaces
- **Testing** - Write tests for new functionality

### YAML/GitHub Actions

```yaml
# Use consistent indentation (2 spaces)
name: Workflow Name
on:
  push:
    branches: [ main ]

jobs:
  job-name:
    name: Human Readable Name
    runs-on: ubuntu-latest
    steps:
      - name: Clear step description
        uses: actions/checkout@v4
```

### Markdown

- Use proper headers (`#`, `##`, `###`)
- Include code blocks with language specification
- Add alt text for images
- Use consistent formatting for lists
- Include table of contents for long documents

### Commit Messages

Follow conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

Examples:
```
feat: add automated release workflow
fix: resolve dependency scanning issue
docs: update contributing guidelines
```

## 📞 Getting Help

### Community Channels

- **GitHub Discussions** - General questions and ideas
- **Issues** - Bug reports and feature requests
- **Pull Requests** - Code review and collaboration

### Response Times

We aim to respond to:
- **Issues**: Within 1-3 business days
- **Pull Requests**: Within 1 week
- **Security Issues**: Within 24 hours

### Maintainer Contact

- Create an issue for project-related questions
- Use discussions for general questions
- Email for security concerns (see SECURITY.md)

## 🏆 Recognition

Contributors are recognized in several ways:

- **Contributors list** in our README
- **Release notes** mention significant contributions
- **GitHub insights** track all contributions
- **Special recognition** for outstanding contributions

## 📚 Resources

- [GitHub Flow](https://guides.github.com/introduction/flow/) - Branching workflow
- [Conventional Commits](https://www.conventionalcommits.org/) - Commit message format
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Markdown Guide](https://www.markdownguide.org/)

## ❓ Questions?

Don't hesitate to ask questions! We're here to help:

- **New to open source?** Check out [First Timers Only](https://www.firsttimersonly.com/)
- **Need help getting started?** Create a discussion or issue
- **Want to pair program?** Reach out to maintainers

Thank you for contributing! 🎉
