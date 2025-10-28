# Standard Agent Handoff Protocol

## Purpose
This protocol defines the standard procedure for transferring work between AI agents to ensure continuity, quality, and traceability.

## When to Use
- Completing assigned task and passing to next agent
- Task requires expertise from different agent type
- Validation phase after completion
- Scheduled agent rotation
- Agent reaching capacity or timeout

## Handoff Phases

### Phase 1: Preparation (Outgoing Agent)

#### 1.1 Complete Current Work
- [ ] Finish all assigned subtasks
- [ ] Resolve any blocking issues
- [ ] Clean up temporary artifacts
- [ ] Commit all changes

#### 1.2 Document Changes
- [ ] Update AI handoff footer in all modified files
- [ ] List all changes made
- [ ] Note any deviations from plan
- [ ] Document decisions and rationale

#### 1.3 Run Validation
- [ ] Execute all relevant quality checks
- [ ] Run linters and formatters
- [ ] Verify links and references
- [ ] Test any code changes
- [ ] Document validation results

#### 1.4 Prepare Context
- [ ] Summarize work completed
- [ ] Identify remaining work
- [ ] List blockers or dependencies
- [ ] Highlight critical issues
- [ ] Gather relevant background

### Phase 2: Transfer (Transition)

#### 2.1 Create Handoff Document
Create a new document: `.github/agents/handoffs/YYYYMMDD-HHMMSS-[task-id].md`

**Required Content**:
```markdown
# Agent Handoff Report

## Metadata
- **From Agent**: [agent-id]
- **To Agent**: [target-agent-id]
- **Timestamp**: [ISO-8601 timestamp]
- **Task ID**: [task-identifier]
- **Priority**: [high/medium/low]

## Work Summary
### Completed
- [List completed items]

### In Progress
- [List partially completed items]

### Not Started
- [List remaining items]

## Changes Made
1. [Detailed list of all changes]
2. [Include file paths and descriptions]

## Context for Next Agent
### Background
[Essential context and history]

### Dependencies
[Related work, blocked items, external dependencies]

### Critical Information
[Must-know information for continuation]

### Recommendations
[Suggested approach for remaining work]

## Validation Status
- [ ] All checks passed
- [ ] Known issues: [list]
- [ ] Manual review needed: [Y/N]

## Handoff Checklist
- [ ] All changes documented
- [ ] AI handoff footers updated
- [ ] Quality checks completed
- [ ] Context is complete
- [ ] Next steps are clear
```

#### 2.2 Update Status Markers
- [ ] Set task status to "in-handoff"
- [ ] Tag next agent (if known)
- [ ] Update task tracker
- [ ] Notify coordinator agent

#### 2.3 Archive Work Artifacts
- [ ] Save logs and outputs
- [ ] Store validation reports
- [ ] Archive temporary files
- [ ] Update documentation index

### Phase 3: Reception (Incoming Agent)

#### 3.1 Review Handoff
- [ ] Read complete handoff document
- [ ] Review all modified files
- [ ] Check AI handoff headers/footers
- [ ] Verify context completeness
- [ ] Note any questions or concerns

#### 3.2 Validate Context
- [ ] Understand previous agent's work
- [ ] Verify changes are as described
- [ ] Run validation checks independently
- [ ] Confirm no regression introduced
- [ ] Identify any gaps in handoff

#### 3.3 Accept or Clarify
**If Handoff is Complete**:
- [ ] Accept handoff
- [ ] Acknowledge receipt
- [ ] Update task status to "in-progress"
- [ ] Begin work on next phase

**If Handoff Needs Clarification**:
- [ ] Document specific questions
- [ ] Request additional context
- [ ] Escalate to coordinator if needed
- [ ] Wait for clarification before proceeding

#### 3.4 Plan Next Steps
- [ ] Review remaining work
- [ ] Prioritize tasks
- [ ] Identify dependencies
- [ ] Estimate effort
- [ ] Set milestones

### Phase 4: Continuation (Ongoing Work)

#### 4.1 Maintain Context
- [ ] Reference previous agent's work
- [ ] Preserve intent and direction
- [ ] Build on existing foundation
- [ ] Avoid unnecessary changes

#### 4.2 Document Progress
- [ ] Update AI handoff footers regularly
- [ ] Log significant decisions
- [ ] Note deviations from plan
- [ ] Record blockers encountered

#### 4.3 Prepare for Next Handoff
- [ ] Keep documentation current
- [ ] Maintain clean working state
- [ ] Update context continuously
- [ ] Be ready for handoff at any time

## Quality Assurance

### Handoff Quality Checklist
✓ **Completeness**: All required information included
✓ **Clarity**: Context is clear and unambiguous
✓ **Accuracy**: Changes accurately documented
✓ **Traceability**: Full audit trail maintained
✓ **Validation**: Quality checks completed and passed

### Red Flags
🚩 Missing context or background
🚩 Incomplete change documentation
🚩 Failed validation checks
🚩 Unclear next steps
🚩 Broken references or dependencies
🚩 Conflicting information

## Escalation

### When to Escalate
- Handoff context is incomplete or unclear
- Validation checks failed
- Conflicting changes detected
- Blocked on external dependency
- Deadline at risk

### Escalation Process
1. **Document Issue**: Clearly describe the problem
2. **Notify Coordinator**: Alert coordinator agent
3. **Pause Work**: Stop making changes
4. **Wait for Resolution**: Don't proceed until cleared
5. **Resume**: Continue after issue resolved

### Escalation Channels
- Create GitHub issue with label "agent-handoff-issue"
- Update handoff document with "BLOCKED" status
- Notify coordinator agent via task system
- Request human review if needed

## Best Practices

### Do's ✓
- Always read handoff documents completely
- Validate independently before accepting
- Maintain comprehensive documentation
- Ask questions when unclear
- Preserve previous agent's intent
- Keep communication structured
- Update status regularly

### Don'ts ✗
- Skip reading handoff context
- Assume understanding without verification
- Make changes without documentation
- Ignore validation failures
- Break previous agent's work
- Leave handoff incomplete
- Delay escalation when blocked

## Templates

### Quick Handoff Template (Minor Changes)
```markdown
## Quick Handoff
**From**: [agent] → **To**: [agent]
**Task**: [brief description]

**Changes**: [1-2 sentence summary]
**Status**: [validation status]
**Next**: [immediate next step]
```

### Complex Handoff Template (Major Changes)
Use full handoff document template from Phase 2.1

## Metrics & Monitoring

### Track These Metrics
- Handoff completion rate
- Time to accept handoff
- Clarification request rate
- Validation success rate
- Escalation frequency

### Success Indicators
- 95%+ handoffs accepted on first attempt
- <1 hour average handoff time
- <5% escalation rate
- Zero handoff-related bugs

## Related Documents
- [Emergency Handoff Protocol](emergency-handoff.md)
- [Specialized Handoff Protocol](specialized-handoff.md)
- [Agent Coordinator Configuration](../coordinator.yml)
- [Task Templates](../task-templates/)

## Revision History
| Date | Version | Changes |
|------|---------|---------|
| 2025-10-28 | 1.0.0 | Initial protocol |
