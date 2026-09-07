# Agent authority boundary

Proposal, authorization, execution, verification, and evidence publication are distinct
capabilities. An agent review is evidence; it is never authorization for that agent's own
change. A different model, prompt, account, or provider does not create independent oversight.

Consequential changes require an authorization record bound to the exact commit or artifact
digest, operation, repository or environment, conditions, expiry, and authorizing human
principal. A later push invalidates approval until that exact head is authorized again.

The default branch and the paths in `config/protected-control-inputs.json` must be protected by a
GitHub ruleset requiring a pull request and an eligible human code-owner review. Force pushes,
branch deletion, stale approvals, and unresolved review conversations must be rejected. Copilot
approvals may provide review evidence but must be disabled as merge-satisfying approvals.

Emergency authorization must be action-time, human, narrowly scoped, time-limited, and followed
by a durable incident receipt. It must not be represented as an ordinary independent PR review.

Public receipts contain redacted metadata and digests. Credentials, customer payloads, private
prompts, session transcripts, and live deployment identifiers belong only in access-controlled
traces. Secrets never belong in Git.

## Bootstrap status

The repository had no visible ruleset at the 2026-09-07 baseline. Repository administration is
not available to the connected GitHub integration, and `@4-b100m` reviewer eligibility could not
be established through its collaborator-permission response. The policy files can merge only
after an organization owner demonstrates the human authorization path and applies the ruleset.

