# Documentation Task Template

## Task Metadata
```yaml
task_type: documentation
category: technical_writing
priority: medium
estimated_effort: 2-4 hours
```

## Assigned Agent
**Primary**: documentation_agent
**Validator**: validator_agent

## Task Description
Update, improve, or create documentation following project standards.

## Prerequisites
- [ ] Reviewed existing documentation
- [ ] Understood target audience
- [ ] Identified related documents
- [ ] Checked for existing issues/PRs

## Scope & Objectives
### In Scope
- Content accuracy and completeness
- Structure and organization
- Clarity and readability
- Examples and code snippets
- Cross-references and links
- Formatting and style

### Out of Scope
- Code implementation (unless examples)
- Workflow modification
- Policy changes
- Architecture decisions

## Task Steps

### 1. Analysis Phase
- [ ] Read target document completely
- [ ] Identify improvement areas
- [ ] Check related documentation
- [ ] Verify technical accuracy
- [ ] Review feedback/issues

### 2. Planning Phase
- [ ] Outline changes needed
- [ ] Identify dependencies
- [ ] Determine impact scope
- [ ] Plan validation approach
- [ ] Estimate effort

### 3. Execution Phase
- [ ] Update AI handoff header with context
- [ ] Make content changes
- [ ] Add/update examples
- [ ] Fix broken links
- [ ] Update cross-references
- [ ] Improve formatting
- [ ] Check spelling/grammar

### 4. Validation Phase
- [ ] Run markdown linter
- [ ] Check all links
- [ ] Verify code examples
- [ ] Review for consistency
- [ ] Validate against style guide
- [ ] Test local rendering

### 5. Handoff Phase
- [ ] Update AI handoff footer
- [ ] Create handoff summary
- [ ] List all changes made
- [ ] Note any issues found
- [ ] Tag validator agent

## Quality Standards

### Content Quality
- **Accuracy**: 100% technically correct
- **Completeness**: All necessary information included
- **Clarity**: Easy to understand for target audience
- **Conciseness**: No unnecessary verbosity

### Structure Quality
- **Organization**: Logical flow and hierarchy
- **Navigation**: Clear TOC, headings, links
- **Formatting**: Consistent markdown style
- **Accessibility**: Readable by all tools

### Technical Quality
- **Links**: All links functional
- **Examples**: All examples tested and working
- **References**: All references accurate and current
- **Standards**: Follows project conventions

## Deliverables
- [ ] Updated documentation file(s)
- [ ] AI handoff header/footer complete
- [ ] Handoff summary document
- [ ] Validation report
- [ ] Related document updates (if any)

## Success Criteria
✓ Documentation is accurate and complete
✓ All links are functional
✓ Examples are tested and working
✓ Style is consistent with project
✓ Markdown linter passes
✓ Validator agent approves

## Common Pitfalls to Avoid
⚠️ Breaking existing links
⚠️ Inconsistent terminology
⚠️ Outdated examples
⚠️ Missing cross-references
⚠️ Poor formatting
⚠️ Incomplete context in handoff

## Related Templates
- [Quality Check Template](quality-check.yml)
- [Standard Handoff Protocol](../handoff-protocols/standard-handoff.md)

## Resources
- [Project Style Guide](../../CONTRIBUTING.md#documentation-style)
- [Markdown Best Practices](https://www.markdownguide.org/basic-syntax/)
- [Technical Writing Guide](https://developers.google.com/tech-writing)

## Notes
This template should be adapted based on specific documentation needs.
Always prioritize clarity and accuracy over complexity.
