# GitHub Copilot Instructions for System Governance Framework

## Language and Tool Preferences

### Programming Languages
- Prefer writing **Python** if no language is specified for scripts and automation
- Use **Markdown** for all documentation files
- Use **YAML** for GitHub Actions workflows and configuration files

### Package Managers
- Use **pip** for Python dependencies
- Use **pre-commit** for code quality hooks and validation

### Code Quality Standards
- All Python code must follow PEP 8 style guidelines
- Use Python 3.11+ features and syntax
- YAML files must use 2-space indentation
- Markdown files must follow consistent formatting with proper headers

## Knowledge Base Priorities

### Documentation References
When asking about governance, security, or contribution topics, prioritize:
1. **SECURITY.md** - For vulnerability reporting procedures and security policies
2. **CONTRIBUTING.md** - For development setup, contribution guidelines, and coding standards
3. **CODE_OF_CONDUCT.md** - For community behavior and interaction guidelines
4. **README.md** - For project overview, features, and getting started instructions
5. **GOVERNANCE_ANALYSIS.md** - For governance framework analysis and best practices

### GitHub Actions and CI/CD
When working with workflows and automation:
- Reference existing workflow files in `.github/workflows/`
- Follow GitHub Actions best practices documentation
- Use pinned versions for actions (e.g., `actions/checkout@v4`)
- Validate YAML syntax before committing

### Pre-commit Hooks
When modifying or adding pre-commit hooks:

- Reference `.pre-commit-config.yaml` for existing hook configurations
- Follow pre-commit.com documentation for hook syntax
- Ensure all hooks are compatible with Python 3.11+
- Test hooks locally before committing: `pre-commit run --all-files`

## Response Format Preferences

### General Communication
- Respond with **bullet points** and minimal preamble
- Provide direct, actionable answers
- Include code examples when relevant
- Link to specific documentation when referencing policies or guidelines

### Code Suggestions
- Provide complete, working code snippets
- Include necessary imports and dependencies
- Add inline comments only for complex logic
- Follow existing code patterns and conventions in the repository

### Documentation Changes
- Use clear, concise language
- Include code blocks with proper syntax highlighting
- Add table of contents for long documents
- Follow the existing documentation structure and style

## Repository-Specific Guidelines

### File Organization
- GitHub-specific files belong in `.github/` directory
- Issue templates go in `.github/ISSUE_TEMPLATE/`
- PR templates go in `.github/PULL_REQUEST_TEMPLATE/`
- Workflow files go in `.github/workflows/`
- Configuration files in `.github/configs/`

### Commit Message Format
Follow conventional commits:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation updates
- `chore:` - Maintenance tasks
- `refactor:` - Code restructuring
- `test:` - Test additions or modifications

### Testing and Validation
Before committing any changes:
- Run pre-commit hooks: `pre-commit run --all-files`
- Validate YAML files: `check-yaml`
- Validate JSON files: `check-json`
- Check for trailing whitespace and file endings
- Ensure no large files or private keys are included

## Topic-Specific Guidance

### Security Topics
- Always reference SECURITY.md for vulnerability reporting procedures
- Follow secure coding practices
- Never include secrets, API keys, or private keys in code
- Use GitHub's security features (Dependabot, code scanning)
- Prioritize security fixes over feature development

### Governance Topics
- Reference GOVERNANCE_ANALYSIS.md for framework details
- Align with established governance policies
- Consider impact on existing governance structures
- Document decision-making processes

### Contribution and Community Topics
- Reference CODE_OF_CONDUCT.md for behavior expectations
- Follow CONTRIBUTING.md for development workflows
- Respect code review processes
- Maintain inclusive and welcoming language

### GitHub Actions and Automation
- Use latest stable versions of actions
- Pin action versions for security and reproducibility
- Add clear names and descriptions to workflow steps
- Include error handling and appropriate timeouts
- Test workflows in a fork before merging to main

## Best Practices

### When Suggesting Changes
- Make minimal, focused changes
- Preserve existing functionality
- Maintain backward compatibility when possible
- Update related documentation
- Consider impact on existing users and contributors

### When Adding Dependencies
- Justify the need for new dependencies
- Check for security vulnerabilities
- Prefer well-maintained, popular packages
- Document new dependencies in appropriate files
- Configure Dependabot for automated updates

### When Writing Documentation
- Use clear, accessible language
- Include practical examples
- Provide context for decisions
- Link to related resources
- Keep documentation up-to-date with code changes
