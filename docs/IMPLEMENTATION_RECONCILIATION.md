# Implementation reconciliation — 2026-09-07

The complete original program is tracked in `config/implementation-program.json`: 25 named
gates, each with a canonical owner, disposition, and dependency. It intentionally reports
`program_complete: false`. Code and fixture completion do not close live authority gates.
The earlier three-workstream ledger is historical baseline evidence, not a current status feed.

## Corrections proven from the system

| Original assumption | Verified correction and implementation consequence |
| --- | --- |
| Different stage/account labels establish independent oversight | Separate capabilities and authenticated authority domains, not labels. Owner action-time authorization is distinct from independent PR review; the original plan does not require five people. |
| Require an independent PR approval everywhere | Limen's registry-defined single-owner PR-only rail is existing doctrine. Control-authority changes need explicit additional authorization; do not silently rewrite every repo's integration policy. |
| A new base workflow can validate its own introduction | Bootstrap is circular without a separately authorized exact revision. Post-merge canaries cannot be presented as pre-merge evidence. |
| A PR-associated check proves the candidate head ran | `pull_request_target` can run the base; normal PR CI can run a synthetic merge. Record associated head and actual execution checkout separately. |
| Failed aggregate means tests never ran | Failure leaves execution/checkout observations unknown unless step evidence establishes them. Relay receipt v3 preserves this. |
| A generated success receipt proves publication | Generation precedes upload/push. Relay v3 limits aggregate scope to execution; publication requires later ledger/workflow evidence. |
| A receipt can tell its auditor whether it is duplicated or private | Removed those self-attested flags. The v2 auditor compares claims with separately authenticated observation context; hashes do not authenticate that context. |
| Passing governance CI is an enforceable gate | Its job and lint were allowed to fail. Required CI now fails closed; a health-check stub that claimed protection now reports unknown. |
| Named frontier models should become routing constants | Existing canonical contracts and dynamic provider selection own routing. Historical policy-free v4 remains stable; explicit eligibility uses v5. Never grant authority by capability score. |
| A narrow new OIDC rule retires broad old authority | Trusted-publisher rules are additive. Inventory and explicit retirement are separate gates; no publishing configuration changed here. |

## Exposure scope and conflicts

Metadata-only inspection covered all 20 `split_required` and all three `public_candidate`
repositories in the existing inventory: 23 private, non-archived repositories, no unresolved
metadata reads. This did not read or publish private contents and is not a whole-estate census.
The August 10 Limen census (314) and August 31 governance census (323) are different historical
denominators. Existing issues [#64](https://github.com/organvm-iv-taxis/system-governance-framework/issues/64)
and [#65](https://github.com/organvm-iv-taxis/system-governance-framework/issues/65) still mention
17 splits plus six candidates; the current inventory already reclassified that same 23-item cohort.

All three direct-candidate readiness PRs are already merged. Preserve the existing
[history-audit receipt](https://github.com/organvm-iv-taxis/system-governance-framework/issues/67#issuecomment-5486238402);
it does not replace platform scanner results or exact visibility authorization.

Hospes currently has a public product and private companion with different stable IDs. An older
Limen coordinate-based private override conflicts with that observed split. Other proposed
public/extraction candidates conflict with private-core/internal-strategy classifications.
Do not auto-reconcile desired visibility from slugs or current visibility alone. Resolve stable
identity, approved intent, and scanner evidence through the existing owners first.

## Platform and deployment scope

All 16 existing AI-platform inventory controls remain unresolved; a valid inventory is not a
compliant account. Copilot exclusions require actual entitlement, effective-policy exports,
client/mode context-selection evidence, and compensating review. A synthetic marker that a model
does not repeat is not proof of absent context.

The [official ant apply documentation](https://platform.claude.com/docs/en/cli-sdks-libraries/cli/apply)
was retrieved during this pass. A zero-exit preview can still be blocked; applies have no built-in
all-writer locking, and partial failure can change the lockfile. A production adapter needs a
reviewed plan contract, an environment-wide lease, exact-revision approval, restricted workload
identity and durable private state even on failure. No provider resources, paid comparison,
identity federation, `--force` or `--prune` operation was authorized or activated in this pass.

No npm publisher was found in 30 inspected governance/Limen workflow files. Governance has one
publishable package-manifest candidate; Limen's four npm manifests are private. That does not
prove the governance package absent from npm, or prove no other estate package is active. Keep
npm migration conditional pending package-owner authority inventory. Removed the unused
`packages: write` grant from governance's GitHub-release-only workflow; this is not npm migration.

A live lookup of the manifest's exact scoped package in the
[public npm registry](https://registry.npmjs.org/@sgf%2Fsystem-governance-framework) returned HTTP
404 during this pass. This narrows the public-package finding; it does not establish private
package inventory or prove that no token or older trust configuration remains authorized.

## Concurrent relay integration

PR #4 merged during this pass at `bce5b5afbdb390f55fe6c3a48c37e197763ecc49`, with merge commit
`fc21ba4279e9758439c0eac4c8d353e8d3077ba3`. Its
[hosted policy run](https://github.com/4444J99/organvm-ci-relay/actions/runs/34143239079) succeeded,
while the [execution run](https://github.com/4444J99/organvm-ci-relay/actions/runs/34143238943)
failed in Danse because `ffmpeg` was missing. Actual runner execution is not a billing-denial
signal. PR #5 already supplies the media-tool repair at `957e95888f01fd73e52638c7faa7cd8defa7a397`.

The receipt-v3 repair is therefore preserved in [draft follow-up #6](https://github.com/4444J99/organvm-ci-relay/pull/6),
not attributed retroactively to merged PR #4. It incorporates the existing media-tool repair
and its profile digest/mode changes. A successful main run still would not prove the adversarial
ruleset gate; activation remains separately authorized and verified.

## Remaining verification boundaries

- Governance local tests cover this proposal, not installed branch protection or effective Copilot settings.
- All governance external `uses` references are pinned. Composite actions now read caller data
  through trusted, isolated Python at the defining workflow revision; they no longer interpolate
  caller inputs into shell code or download an unverified latest YAML binary. Legacy auxiliary
  scanners are not thereby proven effective required security gates.
- The read-only auditor is an offline evidence-consistency prototype. It neither authenticates
  remote observations nor consumes reservation/replay state. A production adapter must use the
  existing keeper and canonical execution contract, not import candidate claims as trusted context.
- The model experiment must predeclare zero missed critical authority defects, zero false positives
  on valid fixtures, zero unsupported-success assertions, and zero mutations. Only a real eligible
  provider run can establish latency, consistency, or cost-per-correct-case; no such metric is claimed.
- Limen's baseline lightweight scoped gates passed; the heavy phase stopped at host admission
  because the lease owner PID/start identity was unavailable. This refusal was not bypassed.

The governor repair now preserves failed/unknown provider outcomes and immutable ticket custody,
rejects forged handoff/refund markers, and filters model eligibility before capability ranking.
The new policy binds repository, exact source revision, retention, classification, tools and
destinations. Explicit policy-bearing tasks remain blocked in launch and canonical claims until
a trusted production attestation adapter exists. Legacy policy-free compatibility does not mean
that legacy tasks have acquired a verified retention policy. Full post-change heavy verification
and independent production settlement remain open; the published PR lists the smaller diagnostic
  shards separately from its historical full baseline checks.

Reusable CI's `coverage-enabled` input is now a string: `auto`, `'true'` or `'false'`. The previous
boolean/null interface could not reliably express inheritance. Existing explicit boolean callers
must quote the value. Composite `validate=false` is no longer accepted, because skipping validation
cannot establish trustworthy configuration. Defining-workflow identity must be available; missing
context (including unsupported GitHub Enterprise Server installations) fails closed.

The reusable workflow also removes direct secret references from step conditions, which the
[GitHub documentation](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets)
does not allow. Token-presence detection is isolated from caller test commands rather than granting
those commands a job-wide token environment.

## Running the offline auditor

From a development environment installed with `pip install -e '.[dev]'`:

```sh
python scripts/audit_execution_receipt.py supplied-receipt.json --context authenticated-observations.json
```

The context must come from a separately authenticated observation source, not from fields in the
candidate receipt. This CLI does not establish that authentication. It reads the two supplied
files and prints structured findings without modifying either file or contacting a service.
Exit codes are 0 for verified supplied-evidence consistency, 1 for rejected evidence, and 2 for
unknown or unavailable trusted context. No exit code grants merge, deployment, or publication
authority; every output explicitly retains `production_authorized: false`.

## Canonical workstreams

- [Governance PR #71](https://github.com/organvm-iv-taxis/system-governance-framework/pull/71)
- [Relay PR #4, merged predecessor](https://github.com/4444J99/organvm-ci-relay/pull/4)
- [Relay PR #6, current receipt repair](https://github.com/4444J99/organvm-ci-relay/pull/6)
- [Governor PR #2552](https://github.com/4444J99/limen/pull/2552)

Published exact-tree receipts on these PRs supersede stale PR descriptions. No merge, protected
branch update, settings change, private release, package publication or paid deployment is implied.
