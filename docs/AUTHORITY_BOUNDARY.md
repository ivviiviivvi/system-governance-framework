# Agent authority boundary

Proposal, authorization, execution, verification, and evidence publication are distinct
capabilities, not a requirement to invent five people or service accounts. An agent review is
evidence; it never grants merge authority. Different model or account labels do not prove
independent oversight; authenticate principals and bind their delegated capabilities.

Consequential changes require an authorization record bound to the exact commit or artifact
digest, operation, repository or environment, conditions, expiry, and authorizing human
principal. A later push invalidates approval until that exact head is authorized again.

For this authority-defining repository, the default branch must require a pull request, block
force pushes/deletion, and preserve exact-head human authorization of protected control inputs.
`config/protected-control-inputs.json` is a coverage catalogue, NOT an installed GitHub rule.
Use required code-owner review only after an independent eligible reviewer with write access is
demonstrated. GitHub does not let PR authors approve themselves; two accounts controlled by the
same human do not establish independence. A separately authenticated owner action-time grant may
authorize a precisely scoped bootstrap, but is not an independent GitHub PR approval.

Copilot submitting a review and Copilot approvals satisfying merge requirements are different
settings. The latter must be Disabled everywhere in each relevant organization, not delegated
to repositories; do not infer effective policy from an inaccessible setting. A personal account
is not an organization and requires its own verified configuration.

This proposal does not silently replace Limen's registry-declared single-owner integration rail.
Ordinary changes continue through the canonical PR-only/no-bypass rail; authority-changing work
and explicitly held relay bootstrap work retain their additional authorization gates. The
proposed rule must be reconciled with `institutio/github/estate.yaml` before any administrator
applies it, so an existing reconciler cannot later undo it.

Emergency authorization must be action-time, human, narrowly scoped, time-limited, and followed
by a durable incident receipt. It must not be represented as an ordinary independent PR review.

Public receipts contain allowlisted, redacted metadata and digests. Public repository coordinates
and already-public stable repository IDs can establish identity; private deployment IDs, customer
payloads, private prompts, session transcripts, and detailed traces cannot be copied into public
receipts. Hashes provide integrity, not redaction or authenticity. Secrets never belong in Git.

Excluded operational files still require deterministic validation and an authorized review route.
Content exclusions are defense in depth, not repository isolation or evidence of absent context.

## Bootstrap and execution evidence

A new base-controlled `pull_request_target` workflow cannot authenticate its own introduction.
The bootstrap requires a separately authorized exact revision, followed by the post-merge
self-check and adversarial canaries. The relay remains unactivated until those execute. A
`pull_request_target` status can describe the base SHA; do not label it an exact candidate-head
gate without observing that binding. Likewise a normal PR workflow may execute a synthetic merge
revision: record that checkout alongside the associated PR head.

Passing tests only establish the predicates run in that environment. Failed jobs do not prove
tests never executed, and a receipt constructed before ledger publication cannot attest that its
own publication later succeeded. Public aggregate status must preserve those distinctions.

## Bootstrap status

The repository had no visible ruleset at the 2026-09-07 baseline. Repository administration is
not available to the connected GitHub integration, and `@4-b100m` reviewer eligibility could not
be established through its collaborator-permission response. A review-request API success with
no returned requested reviewer does not establish eligibility or delivery. The policy files are
proposals until the owner demonstrates the authorization path; a separately authorized bootstrap
may break the introduction dependency, never the permanent authority boundary.


### Defining workflow identity

Reusable CI reads the authenticated workflow-run attempt metadata before checking
out any repository source. Its unique `referenced_workflows` entry for
`organvm-iv-taxis/system-governance-framework/.github/workflows/reusable-ci.yml`
supplies the immutable defining SHA. Missing, ambiguous, oversized, malformed or
mismatched metadata fails closed. The setup job alone needs `actions: read` in
addition to `contents: read`; callers must grant those read permissions. No OIDC
permission or caller-provided defining revision is accepted. Repository transfers
require an independently reviewed update to the trusted repository name.

The existing Python CI now calls the local reusable workflow with the existing
minimal preset and an empty language list. This canary must execute its identity,
checkout and parser steps; the intentionally absent language jobs are skips, not
test evidence. Offline mocked API tests do not establish hosted canary acceptance.

Receipt aggregates use failure, then pending, then skipped, then success
precedence across execution, verification and publication. Both claimed stages
and available independent observations must agree with the aggregate; successful
individual stages do not erase incomplete or failed stages.

Sources: [GitHub contexts](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts)
and [workflow-run attempt metadata](https://docs.github.com/en/rest/actions/workflow-runs#get-a-workflow-run-attempt).
