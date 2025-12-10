<!--
╔════════════════════════════════════════════════════════════════════════════╗
║                        AI AGENT HANDOFF METADATA                           ║
╚════════════════════════════════════════════════════════════════════════════╝

Document: VERSIONING.md
Version: 1.0.0
Last Updated: 2025-10-28
Primary Maintainer: System Governance Framework Team
AI Context Level: Versioning Strategy

═══════════════════════════════════════════════════════════════════════════

PURPOSE & SCOPE
────────────────────────────────────────────────────────────────────────────
Defines the versioning strategy and release process for the System
Governance Framework, based on Semantic Versioning principles.

DEPENDENCIES & RELATIONSHIPS
────────────────────────────────────────────────────────────────────────────
Related Documents:
  • CHANGELOG.md - Version history
  • MAINTAINERS.md - Release responsibilities
  • ROADMAP.md - Future version plans

═══════════════════════════════════════════════════════════════════════════
-->

# Versioning Strategy

This document describes the versioning strategy for the System Governance Framework.

## Semantic Versioning

We follow [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) (SemVer):

```
MAJOR.MINOR.PATCH
```

### Version Components

- **MAJOR** (X.0.0): Incompatible API changes or breaking changes
- **MINOR** (x.X.0): New functionality in a backward-compatible manner
- **PATCH** (x.x.X): Backward-compatible bug fixes

### Examples

- `1.0.0` → `1.0.1`: Bug fix (PATCH)
- `1.0.1` → `1.1.0`: New feature (MINOR)
- `1.1.0` → `2.0.0`: Breaking change (MAJOR)

## What Constitutes a Breaking Change?

For the System Governance Framework, breaking changes include:

### Documentation Framework
- Removing or significantly restructuring required files
- Changing the purpose or scope of core documents
- Modifying established governance processes that users depend on
- Breaking existing workflow integrations

### Automation & Workflows
- Changing workflow input/output contracts
- Removing required workflow jobs
- Changing required environment variables or secrets
- Breaking GitHub Actions compatibility

### Configuration Files
- Changing configuration file formats
- Removing required configuration options
- Changing default behaviors that users rely on

### Templates
- Removing required template fields
- Changing template file formats
- Breaking template rendering

### NOT Breaking Changes
- Adding new optional features
- Deprecating features with migration paths
- Internal refactoring without external impact
- Documentation improvements
- Bug fixes
- Performance improvements

## Pre-release Versions

Pre-release versions are denoted by appending identifiers:

```
1.0.0-alpha.1    # Alpha release
1.0.0-beta.2     # Beta release
1.0.0-rc.1       # Release candidate
```

### Pre-release Stages

1. **Alpha** (`-alpha.X`): Early testing, unstable, frequent changes
2. **Beta** (`-beta.X`): Feature complete, testing and bug fixes
3. **Release Candidate** (`-rc.X`): Potentially final, final testing

## Release Cycle

### Regular Releases

- **Major Releases**: Quarterly (every 3 months)
- **Minor Releases**: Monthly
- **Patch Releases**: As needed for critical fixes

### Schedule

```
Q1: January, February, March   → Major release in March
Q2: April, May, June           → Major release in June
Q3: July, August, September    → Major release in September
Q4: October, November, December → Major release in December
```

### Exceptions

- **Security Fixes**: Released immediately as patches
- **Critical Bugs**: Released within 24-48 hours
- **Emergency Releases**: As needed for major issues

## Version Tags

### Git Tags

All releases are tagged in Git:

```bash
v1.0.0        # Release version
v1.0.0-rc.1   # Pre-release version
```

### Tag Format

- Use `v` prefix: `v1.0.0`
- Annotated tags with release notes
- Signed tags (recommended)

```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## Deprecation Policy

### Announcing Deprecations

Deprecated features must be:
1. **Announced**: In release notes and CHANGELOG
2. **Documented**: In documentation with migration guide
3. **Maintained**: For at least one MAJOR version
4. **Removed**: In next MAJOR version

### Deprecation Process

```
v1.5.0: Feature X deprecated, warning added
v1.6.0: Deprecation warning remains
v2.0.0: Feature X removed (with migration guide)
```

### Deprecation Notice Format

```markdown
**Deprecated**: Feature X is deprecated as of v1.5.0 and will be
removed in v2.0.0. Please use Feature Y instead.
See [Migration Guide](link) for details.
```

## Long-Term Support (LTS)

### LTS Versions (Future)

As the project matures, we may designate LTS versions:

- **Support Duration**: 12 months
- **Updates**: Security fixes and critical bugs only
- **Cadence**: One LTS version per year
- **Designation**: Major versions ending in 0 (e.g., 2.0, 3.0)

### LTS Benefits

- **Stability**: Predictable, stable base
- **Security**: Continued security updates
- **Planning**: Long-term planning for enterprises

### Non-LTS Versions

- **Support Duration**: Until next minor version
- **Updates**: All updates until superseded

## Release Process

### 1. Planning Phase

- Review [ROADMAP.md](ROADMAP.md)
- Identify changes for release
- Determine version number
- Update milestone

### 2. Preparation Phase

```bash
# Update version references
# Update CHANGELOG.md
# Update documentation
# Run full test suite
```

### 3. Release Branch

```bash
git checkout -b release/v1.0.0
# Make final adjustments
git commit -m "Prepare v1.0.0 release"
```

### 4. Tagging

```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### 5. GitHub Release

1. Go to GitHub Releases
2. Create new release from tag
3. Generate release notes automatically
4. Edit and enhance release notes
5. Attach any release artifacts
6. Publish release

### 6. Announcement

- Post in GitHub Discussions
- Update README badges (if applicable)
- Notify in any community channels

### 7. Post-Release

- Monitor for issues
- Address any immediate problems
- Plan next release

## Version Numbering Guidelines

### Starting Version

- **1.0.0**: First stable release
- **0.x.y**: Pre-1.0 development versions (breaking changes allowed in MINOR)

### Version Increments

#### PATCH (x.x.X)

Increment for:
- Bug fixes
- Security patches
- Documentation fixes
- Dependency updates (minor)
- Performance improvements (no API change)

#### MINOR (x.X.0)

Increment for:
- New features (backward-compatible)
- New workflows
- New templates
- New documentation sections
- Deprecations (with migration path)
- Dependency updates (major)

#### MAJOR (X.0.0)

Increment for:
- Breaking changes
- Removing deprecated features
- Major architecture changes
- Significant workflow changes
- Incompatible configuration changes

## Branching Strategy

### Main Branches

- **`main`**: Current stable version
- **`develop`**: Next release development (optional)

### Supporting Branches

- **`feature/*`**: New features
- **`fix/*`**: Bug fixes
- **`release/*`**: Release preparation
- **`hotfix/*`**: Emergency fixes

### Branch Lifecycle

```
feature/new-feature → main (via PR)
fix/bug-123 → main (via PR)
hotfix/security → main (direct if urgent)
```

## Version Compatibility

### Backward Compatibility

We maintain backward compatibility within MAJOR versions:

- **1.0.0 → 1.5.0**: Fully compatible
- **1.5.0 → 2.0.0**: May have breaking changes

### Forward Compatibility

Not guaranteed:
- Newer versions may introduce features not in older versions
- Use version checks if needed

## Documentation Versioning

### Approach

- Documentation reflects `main` branch (latest stable)
- Major versions may have separate docs (future)
- CHANGELOG documents version-specific changes

### Version-Specific Docs (Future)

```
docs/
  v1/
  v2/
  latest/ → symlink to current
```

## Automation

### Automated Version Bumping

Future enhancement:
- Use conventional commits for automatic version bumping
- Automated CHANGELOG generation
- Automated release notes

### Conventional Commits (Optional Future)

```
feat: Add new feature (MINOR bump)
fix: Fix bug (PATCH bump)
feat!: Breaking change (MAJOR bump)
```

## Checklist: Releasing a Version

### Pre-release
- [ ] All planned features/fixes complete
- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version number determined
- [ ] Security scan complete
- [ ] Breaking changes documented

### Release
- [ ] Create release branch (if needed)
- [ ] Final testing
- [ ] Create and push git tag
- [ ] Create GitHub release
- [ ] Update release notes
- [ ] Merge to main (if using release branch)

### Post-release
- [ ] Announcement posted
- [ ] Monitor for issues
- [ ] Update ROADMAP if needed
- [ ] Plan next release

## References

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Calendar Versioning](https://calver.org/) (not used, but reference)

## Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-10-28 | 1.0.0 | Initial versioning strategy | System Team |

---

**Questions about versioning?** Open a discussion or issue on GitHub.

<!--
╔════════════════════════════════════════════════════════════════════════════╗
║                     AI AGENT HANDOFF FOOTER - CHANGELOG                    ║
╚════════════════════════════════════════════════════════════════════════════╝

RECENT MODIFICATIONS
────────────────────────────────────────────────────────────────────────────
[2025-10-28] - GitHub Copilot Agent
  Action: Initial Creation
  Changes:
    • Created comprehensive versioning strategy
    • Defined semantic versioning approach
    • Documented release process
    • Added deprecation policy
    • Included LTS strategy for future
  Impact: Establishes clear versioning standards
  Verification: Document structure validated

VALIDATION CHECKLIST
────────────────────────────────────────────────────────────────────────────
☑ Follows Semantic Versioning 2.0.0
☑ Release process clearly defined
☑ Breaking change policy documented
☑ Deprecation policy included

HANDOFF INSTRUCTIONS
────────────────────────────────────────────────────────────────────────────
For Next Agent/Maintainer:
1. Follow versioning rules strictly
2. Update when releasing new versions
3. Document any versioning policy changes
4. Keep synchronized with CHANGELOG.md
5. Review annually for effectiveness

CRITICAL NOTES
────────────────────────────────────────────────────────────────────────────
⚠️  Important Considerations:
  • Versioning consistency builds user trust
  • Breaking changes must be well-documented
  • Deprecation policy must be followed
  • Security fixes take priority

═══════════════════════════════════════════════════════════════════════════
Document Processing Status: COMPLETE
Last Validated: 2025-10-28
Next Review Due: 2026-01-28
═══════════════════════════════════════════════════════════════════════════
-->
