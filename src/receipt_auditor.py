"""Read-only consistency auditor; never a source of deployment/merge authority.

Receipts are untrusted claims. A caller must separately authenticate and authorize
the observations used to construct ``TrustedAuditContext``. Passing a context
copied from the receipt does NOT establish trust; this module does not fetch,
authenticate, sign, persist, or consume anything. A passing synthetic test is not
hosted execution, confidentiality, or production-authorization evidence.

The v1 call shape remains accepted, but absent external context is always unknown
and v1/self-attested booleans can no longer produce a passing audit. v2 is a small
audit envelope, not a replacement for the canonical limen execution contract.
Adapters must preserve canonical evidence and authenticate it outside this module.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, StrictBool, ValidationError


def _aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp requires an explicit timezone")
    return value


Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Commit = Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
Identifier = Annotated[str, Field(min_length=1, max_length=256)]
Timestamp = Annotated[datetime, AfterValidator(_aware)]
Cost = Annotated[float, Field(ge=0, le=1e12, allow_inf_nan=False)]
Count = Annotated[int, Field(ge=0, le=10**12)]
Status = Literal["success", "failure", "pending", "skipped"]
Origin = Literal[
    "local_execution",
    "organization_actions",
    "personal_relay",
    "external_review",
    "static_inspection",
    "reported_not_reproduced",
    "review_bot",
]
EXECUTION_ORIGINS = {"local_execution", "organization_actions", "personal_relay"}


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class Scope(Record):
    repository: Identifier
    environment: Identifier
    operation: Identifier


class Task(Scope):
    id: Identifier
    source_sha: Commit
    task_digest: Digest
    artifact_digest: Digest


class WorkflowIdentity(Record):
    repository: Identifier
    file_path: Annotated[str, Field(pattern=r"^\.github/workflows/[^\s]+\.ya?ml$")]
    ref: Identifier
    sha: Commit


class Workflows(Record):
    caller: WorkflowIdentity
    defining: WorkflowIdentity


class Actor(Record):
    principal: Identifier


class AuthorizationClaim(Actor):
    record_id: Identifier
    kind: Literal["human_authorization", "independent_review"]
    source_sha: Commit


class ExecutionClaim(Actor):
    result_id: Identifier
    reservation_id: Identifier
    reservation_state: Literal["pending", "acknowledged", "rejected"]
    status: Status
    started_at: Timestamp
    completed_at: Timestamp
    provider: Identifier
    model: Identifier
    tool_policy_digest: Digest
    data_classification: Literal["synthetic", "public", "private", "restricted"]
    permissions: dict[str, Literal["read", "write", "none"]]
    mutations: list[Digest]


class VerificationClaim(Actor):
    record_id: Identifier
    result_id: Identifier
    artifact_digest: Digest
    status: Status


class PublicationClaim(Actor):
    record_id: Identifier
    artifact_digest: Digest
    status: Status


class Stages(Record):
    proposal: Actor
    authorization: AuthorizationClaim
    execution: ExecutionClaim
    verification: VerificationClaim
    publication: PublicationClaim


class Budget(Record):
    reserved: Cost
    actual: Cost
    currency: Annotated[str, Field(pattern=r"^[A-Z]{3}$")]


class Claim(Record):
    execution_success: StrictBool
    evidence_origin: Origin


class Receipt(Record):
    schema_version: Literal["organvm-execution-receipt/v2"]
    receipt_id: Identifier
    task: Task
    stages: Stages
    workflow: Workflows
    budget: Budget
    claim: Claim
    aggregate: Status
    public_payload: dict[str, Any]


class Principal(Record):
    """Authenticated actor identity; authority domain is not a model/vendor label."""

    kind: Literal["human", "agent", "service"]
    authority_domain: Identifier
    authorization_scopes: list[Scope]
    verification_scopes: list[Scope]
    publication_scopes: list[Scope]
    provenance_digest: Digest


class AuthorizationEvidence(AuthorizationClaim, Scope):
    task_digest: Digest
    # Explicit null authorizes exact source/task, not a yet-unknown output.
    # A supplied digest additionally restricts authorization to that artifact.
    artifact_digest: Digest | None
    issued_at: Timestamp
    expires_at: Timestamp
    revoked_at: Timestamp | None
    provenance_digest: Digest


class ReservationEvidence(Record):
    reservation_id: Identifier
    task_id: Identifier
    task_digest: Digest
    source_sha: Commit
    result_id: Identifier
    provider: Identifier
    model: Identifier
    tool_policy_digest: Digest
    data_classification: Literal["synthetic", "public", "private", "restricted"]
    reserved: Cost
    currency: Annotated[str, Field(pattern=r"^[A-Z]{3}$")]
    acknowledged_at: Timestamp
    expires_at: Timestamp
    state: Literal["pending", "acknowledged", "rejected"]
    provenance_digest: Digest


class ExecutionEvidence(ExecutionClaim):
    task_digest: Digest
    source_sha: Commit
    artifact_digest: Digest
    actual_cost: Cost
    currency: Annotated[str, Field(pattern=r"^[A-Z]{3}$")]
    workflow: Workflows
    evidence_origin: Origin
    provenance_digest: Digest


class VerificationEvidence(VerificationClaim):
    source_sha: Commit
    completed_at: Timestamp
    provenance_digest: Digest


class PublicationEvidence(PublicationClaim):
    result_id: Identifier
    completed_at: Timestamp
    provenance_digest: Digest


class PublicReview(Actor):
    payload_digest: Digest
    status: Literal["approved", "rejected", "unknown"]
    provenance_digest: Digest


class TrustedAuditContext(Record):
    """Separately sourced, authenticated snapshot. JSON alone cannot prove trust.

    Counts include the current result; prior IDs exclude it. Collect a consistent
    snapshot after publication. Missing observations are unknown, never success.
    No replay IDs are consumed here: atomic replay admission belongs to the
    existing governor, not this read-only auditor.
    """

    observed_at: Timestamp
    provenance_digest: Digest
    expected_task: Task
    expected_workflow: Workflows
    observed_proposal: Actor
    principals: dict[str, Principal]
    authorizations: dict[str, AuthorizationEvidence]
    reservations: dict[str, ReservationEvidence]
    executions: dict[str, ExecutionEvidence]
    verifications: dict[str, VerificationEvidence]
    publications: dict[str, PublicationEvidence]
    reservation_use_counts: dict[str, Count]
    prior_result_ids: list[Identifier]
    prior_receipt_ids: list[Identifier]
    public_review: PublicReview | None


def canonical_digest(value: Any) -> str:
    """SHA-256 of JSON using this version's encoding, not an authentication proof."""
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False, ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def audit_receipt(receipt: Any, *, context: TrustedAuditContext | None = None) -> dict[str, Any]:
    """Audit supplied observations, without network, writes, execution or authority."""
    findings: list[dict[str, str]] = []

    def add(code: str, path: str, detail: str, severity: str = "error") -> None:
        findings.append({"code": code, "path": path, "detail": detail, "severity": severity})

    def result(digest: str | None) -> dict[str, Any]:
        errors = any(item["severity"] == "error" for item in findings)
        unknowns = [item["code"] for item in findings if item["severity"] == "unknown"]
        return {
            "schema": "organvm-receipt-audit/v2",
            "receipt_digest": digest,
            "valid": not findings,
            "status": "rejected" if errors else "unknown" if unknowns else "verified",
            "scope": "supplied_evidence_consistency",
            "production_authorized": False,
            "findings": sorted(findings, key=lambda item: (item["code"], item["path"])),
            "uncertainty": sorted(set(unknowns)),
            "unsupported_claims": sorted(
                {item["code"] for item in findings if "SUCCESS" in item["code"]}
            ),
            "writes_performed": False,
        }

    try:
        digest = canonical_digest(receipt)
        # JSON validation admits RFC3339 datetime strings without coercing other types.
        parsed = Receipt.model_validate_json(
            json.dumps(receipt, allow_nan=False, ensure_ascii=True)
        )
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        if isinstance(exc, ValidationError):
            # Even error locations can contain attacker-supplied private key names.
            # Do not publish Pydantic locations, values, or validator context.
            add("INVALID_RECEIPT", "$", "schema/type/format validation failed")
        else:
            add("INVALID_RECEIPT", "$", "expected finite, serializable JSON")
        return result(locals().get("digest"))

    if context is None:
        add("TRUSTED_CONTEXT_REQUIRED", "context", "external observations absent", "unknown")
        return result(digest)
    if not isinstance(context, TrustedAuditContext):
        add(
            "INVALID_CONTEXT", "context", "a typed, independently authenticated context is required"
        )
        return result(digest)
    try:
        # Revalidate nested mutable containers / model_construct bypasses before use.
        context = TrustedAuditContext.model_validate(context.model_dump(mode="python"))
    except (TypeError, ValueError, OverflowError, RecursionError):
        add("INVALID_CONTEXT", "context", "trusted snapshot failed schema validation")
        return result(digest)

    task, stages, expected = parsed.task, parsed.stages, context.expected_task
    execution, authorization = stages.execution, stages.authorization
    scope = Scope(
        repository=expected.repository,
        environment=expected.environment,
        operation=expected.operation,
    )

    def match(actual: Any, admitted: Any, code: str, path: str) -> None:
        if actual != admitted:
            add(code, path, "claim differs from independently observed/admitted value")

    def observed(mapping: dict[str, Any], key: str, path: str) -> Any:
        value = mapping.get(key)
        if value is None:
            add("MISSING_OBSERVATION", path, "independent evidence absent", "unknown")
        return value

    def principal(identity: str, path: str) -> Principal | None:
        return observed(context.principals, identity, path)

    for field in Task.model_fields:
        match(
            getattr(task, field), getattr(expected, field), "TASK_BINDING_MISMATCH", f"task.{field}"
        )
    match(
        stages.proposal, context.observed_proposal, "PROPOSAL_EVIDENCE_MISMATCH", "stages.proposal"
    )
    for name in ("caller", "defining"):
        identity, admitted = (
            getattr(parsed.workflow, name),
            getattr(context.expected_workflow, name),
        )
        for field in WorkflowIdentity.model_fields:
            code = "WORKFLOW_SHA_MISMATCH" if field == "sha" else "WORKFLOW_IDENTITY_MISMATCH"
            match(
                getattr(identity, field), getattr(admitted, field), code, f"workflow.{name}.{field}"
            )

    proposer = principal(stages.proposal.principal, "stages.proposal.principal")
    authorizer = principal(authorization.principal, "stages.authorization.principal")
    executor = principal(execution.principal, "stages.execution.principal")
    verifier = principal(stages.verification.principal, "stages.verification.principal")
    publisher = principal(stages.publication.principal, "stages.publication.principal")
    if authorizer:
        if authorizer.kind != "human":
            add(
                "NON_HUMAN_AUTHORIZATION",
                "stages.authorization.principal",
                "actor is not an authenticated human",
            )
        if scope not in authorizer.authorization_scopes:
            add(
                "INELIGIBLE_AUTHORIZER",
                "stages.authorization.principal",
                "human lacks scope eligibility",
            )
        if (
            proposer
            and authorization.kind == "independent_review"
            and proposer.authority_domain == authorizer.authority_domain
        ):
            add(
                "SELF_AUTHORIZATION",
                "stages.authorization.kind",
                "same authority domain is not independent review",
            )
    if verifier:
        if scope not in verifier.verification_scopes:
            add(
                "INELIGIBLE_VERIFIER",
                "stages.verification.principal",
                "verifier lacks scope eligibility",
            )
        if executor and verifier.authority_domain == executor.authority_domain:
            add(
                "MISSING_INDEPENDENT_VERIFIER",
                "stages.verification.principal",
                "different labels share execution authority",
            )
        if proposer and verifier.authority_domain == proposer.authority_domain:
            add(
                "MISSING_INDEPENDENT_VERIFIER",
                "stages.verification.principal",
                "different labels share proposal authority",
            )
    if publisher and scope not in publisher.publication_scopes:
        add(
            "INELIGIBLE_PUBLISHER",
            "stages.publication.principal",
            "publisher lacks scope eligibility",
        )

    auth = observed(context.authorizations, authorization.record_id, "stages.authorization")
    if auth:
        for field in AuthorizationClaim.model_fields:
            match(
                getattr(authorization, field),
                getattr(auth, field),
                "AUTHORIZATION_PROVENANCE_MISMATCH",
                f"stages.authorization.{field}",
            )
        for field in (
            "repository",
            "environment",
            "operation",
            "source_sha",
            "task_digest",
        ):
            match(
                getattr(auth, field),
                getattr(expected, field),
                "STALE_AUTHORIZATION" if field == "source_sha" else "AUTHORIZATION_SCOPE_MISMATCH",
                f"authorization.{field}",
            )
        if auth.artifact_digest is not None:
            match(
                auth.artifact_digest,
                expected.artifact_digest,
                "AUTHORIZATION_SCOPE_MISMATCH",
                "authorization.artifact_digest",
            )
        if not auth.issued_at <= execution.started_at < auth.expires_at:
            add(
                "AUTHORIZATION_EXPIRED_OR_NOT_YET_VALID",
                "authorization.expires_at",
                "authorization does not cover action time",
            )
        if auth.revoked_at is not None and auth.revoked_at <= execution.started_at:
            add(
                "REVOKED_AUTHORIZATION",
                "authorization.revoked_at",
                "authorization revoked before execution",
            )

    if not execution.started_at <= execution.completed_at <= context.observed_at:
        add(
            "INVALID_EXECUTION_TIME",
            "stages.execution",
            "execution chronology conflicts with observation time",
        )
    reservation = observed(
        context.reservations, execution.reservation_id, "stages.execution.reservation_id"
    )
    if execution.reservation_state != "acknowledged":
        add(
            "UNACKNOWLEDGED_RESERVATION",
            "stages.execution.reservation_state",
            "claim does not identify acknowledged admission",
        )
    if reservation:
        for field in (
            "reservation_id",
            "result_id",
            "provider",
            "model",
            "tool_policy_digest",
            "data_classification",
        ):
            match(
                getattr(execution, field),
                getattr(reservation, field),
                "RESERVATION_BINDING_MISMATCH",
                f"stages.execution.{field}",
            )
        for field, task_field in (
            ("task_id", "id"),
            ("task_digest", "task_digest"),
            ("source_sha", "source_sha"),
        ):
            match(
                getattr(reservation, field),
                getattr(expected, task_field),
                "RESERVATION_BINDING_MISMATCH",
                f"reservation.{field}",
            )
        match(
            parsed.budget.reserved,
            reservation.reserved,
            "BUDGET_BINDING_MISMATCH",
            "budget.reserved",
        )
        match(
            parsed.budget.currency,
            reservation.currency,
            "BUDGET_BINDING_MISMATCH",
            "budget.currency",
        )
        if (
            reservation.state != "acknowledged"
            or reservation.acknowledged_at > execution.started_at
        ):
            add(
                "UNACKNOWLEDGED_RESERVATION",
                "reservation.acknowledged_at",
                "canonical acknowledgement did not precede invocation",
            )
        if execution.started_at >= reservation.expires_at:
            add(
                "EXPIRED_RESERVATION",
                "reservation.expires_at",
                "reservation expired before invocation",
            )
    uses = observed(
        context.reservation_use_counts, execution.reservation_id, "reservation.use_count"
    )
    if uses is not None and uses != 1:
        add(
            "DUPLICATE_RESERVATION" if uses > 1 else "UNOBSERVED_RESERVATION_USE",
            "reservation.use_count",
            "canonical history must show exactly one admitted result",
        )
    if execution.result_id in context.prior_result_ids:
        add("REPLAYED_RESULT", "stages.execution.result_id", "result was previously consumed")
    if parsed.receipt_id in context.prior_receipt_ids:
        add("REPLAYED_RECEIPT", "receipt_id", "receipt was previously consumed")

    run = observed(context.executions, execution.result_id, "stages.execution")
    if run:
        for field in ExecutionClaim.model_fields:
            match(
                getattr(execution, field),
                getattr(run, field),
                "EXECUTION_EVIDENCE_MISMATCH",
                f"stages.execution.{field}",
            )
        for field in ("source_sha", "task_digest", "artifact_digest"):
            match(
                getattr(run, field),
                getattr(expected, field),
                "EXECUTION_EVIDENCE_MISMATCH",
                f"execution.{field}",
            )
        match(
            run.workflow,
            context.expected_workflow,
            "WORKFLOW_OBSERVATION_MISMATCH",
            "execution.workflow",
        )
        match(parsed.budget.actual, run.actual_cost, "BUDGET_BINDING_MISMATCH", "budget.actual")
        match(parsed.budget.currency, run.currency, "BUDGET_BINDING_MISMATCH", "budget.currency")
        match(
            parsed.claim.evidence_origin,
            run.evidence_origin,
            "EVIDENCE_ORIGIN_MISMATCH",
            "claim.evidence_origin",
        )
        if run.actual_cost > parsed.budget.reserved:
            add("BUDGET_OVERRUN", "budget.actual", "observed cost exceeds acknowledged reservation")
        if parsed.claim.execution_success and (
            run.status != "success" or run.evidence_origin not in EXECUTION_ORIGINS
        ):
            add(
                "MISLEADING_SUCCESS",
                "claim.execution_success",
                "observations do not establish executed success",
            )
    if parsed.claim.execution_success != (execution.status == "success"):
        add(
            "CONTRADICTORY_SUCCESS",
            "claim.execution_success",
            "success claim and execution status differ",
        )

    verification = observed(
        context.verifications, stages.verification.record_id, "stages.verification"
    )
    if verification:
        for field in VerificationClaim.model_fields:
            match(
                getattr(stages.verification, field),
                getattr(verification, field),
                "VERIFICATION_EVIDENCE_MISMATCH",
                f"stages.verification.{field}",
            )
        match(
            verification.result_id,
            execution.result_id,
            "VERIFICATION_BINDING_MISMATCH",
            "verification.result_id",
        )
        match(
            verification.artifact_digest,
            expected.artifact_digest,
            "VERIFICATION_BINDING_MISMATCH",
            "verification.artifact_digest",
        )
        match(
            verification.source_sha,
            expected.source_sha,
            "VERIFICATION_BINDING_MISMATCH",
            "verification.source_sha",
        )
        if not execution.completed_at <= verification.completed_at <= context.observed_at:
            add(
                "INVALID_VERIFICATION_TIME",
                "verification.completed_at",
                "verification must follow execution",
            )
    publication = observed(context.publications, stages.publication.record_id, "stages.publication")
    if publication:
        for field in PublicationClaim.model_fields:
            match(
                getattr(stages.publication, field),
                getattr(publication, field),
                "PUBLICATION_EVIDENCE_MISMATCH",
                f"stages.publication.{field}",
            )
        match(
            publication.result_id,
            execution.result_id,
            "PUBLICATION_BINDING_MISMATCH",
            "publication.result_id",
        )
        match(
            publication.artifact_digest,
            expected.artifact_digest,
            "PUBLICATION_BINDING_MISMATCH",
            "publication.artifact_digest",
        )
        if (
            verification
            and not verification.completed_at <= publication.completed_at <= context.observed_at
        ):
            add(
                "INVALID_PUBLICATION_TIME",
                "publication.completed_at",
                "publication must follow verification",
            )
    if parsed.aggregate == "success":
        if any(
            stage.status != "success"
            for stage in (execution, stages.verification, stages.publication)
        ):
            add(
                "FALSE_AGGREGATE_SUCCESS", "aggregate", "one or more claimed stages did not succeed"
            )
        if any(
            item is not None and item.status != "success"
            for item in (run, verification, publication)
        ):
            add(
                "FALSE_AGGREGATE_SUCCESS", "aggregate", "independent stage evidence did not succeed"
            )

    review = context.public_review
    if review is None or review.status == "unknown":
        add(
            "PUBLIC_REVIEW_UNKNOWN",
            "public_payload",
            "no approved independent redaction review",
            "unknown",
        )
    else:
        reviewer = principal(review.principal, "public_review.principal")
        if reviewer and scope not in reviewer.publication_scopes:
            add(
                "INELIGIBLE_PUBLIC_REVIEWER",
                "public_review.principal",
                "reviewer lacks publication scope",
            )
        if (
            review.status != "approved"
            or canonical_digest(parsed.public_payload) != review.payload_digest
        ):
            add(
                "UNAPPROVED_PUBLIC_PAYLOAD",
                "public_payload",
                "public bytes not covered by approved redaction evidence",
            )

    return result(digest)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = item
    return value


def audit_file(path: Path, *, context: TrustedAuditContext | None = None) -> dict[str, Any]:
    """Read only the explicitly supplied file. Duplicate keys fail closed."""
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    except (OSError, UnicodeError, ValueError):
        return audit_receipt(None, context=context)
    return audit_receipt(receipt, context=context)
