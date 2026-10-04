---
name: plan-review
description: "Use in an independent session to review an implementation plan before execution; writes bounded inline findings into the plan."
license: MIT
compatibility: "Agent Skills-compatible coding agents; requires repository read access and permission to edit only the selected plan Markdown file."
metadata:
  author: "Daniil(Ngoroth) and Bes"
  version: "2.0.2"
---

# Plan Review

Independently verify that an implementation plan is correct, repository-grounded, bounded, and executable. Write review findings directly beside the affected plan text. Stop after review; do not implement the plan.

## Independence and write boundary

- Use this skill in a session that did not create or substantively revise the plan. If this session authored the plan, stop and request review in a separate session.
- Prefer one reviewer session for the plan's full review lifecycle. A replacement reviewer must continue the recorded rounds and finding IDs rather than restart from zero.
- Required decisions belong to the responsible party identified by the user's chosen process or supplied task context, whether a person or automated participant. Executing this skill does not confer that authority; report missing responsibility or decisions and reuse applicable decisions already supplied. The independent reviewer retains ownership of findings and technical verdicts.
- Treat the repository as read-only except for the selected `docs/plans/*.md` file.
- In that file, modify only review metadata and `PLAN-REVIEW` comment blocks. Never rewrite the plan's substantive content.
- Do not modify source, tests, configuration, brainstorm records, or backlog files. Do not commit, push, or implement.
- Never include secrets or credentials. Replace any encountered value with `[REDACTED]` in review text.

## Input

Require an explicit repository-relative plan path. If it is missing or ambiguous, ask one question to identify it. Do not guess from modification time.

Read:

1. the complete plan;
2. its linked brainstorm record, when present;
3. applicable `AGENTS.md`, `CLAUDE.md`, README, and project documentation;
4. relevant source, tests, build configuration, dependencies, and useful repository history.

Verify repository claims directly. Do not trust paths, symbols, commands, or behavior merely because the plan states them.

## Review state

Plans use these frontmatter fields:

```yaml
---
plan_revision: 1
review_round: 0
max_review_rounds: 3
review_status: pending
reviewed_revision: null
---
```

If a legacy plan has no review metadata, add these fields without replacing unrelated frontmatter. Review annotations do not increment `plan_revision`; substantive plan changes do.

Before reviewing:

- If `review_status` is `approved` or `approved-with-notes` and `reviewed_revision` equals `plan_revision`, report that the current revision is already approved and stop unless another review is explicitly authorized by the responsible party.
- If `review_status` is `needs-decision`, stop and report the unresolved findings to the responsible party. Do not exceed `max_review_rounds`.
- If `review_round >= max_review_rounds`, do not increment the counter or start another round. If blocking findings remain, set `review_status` to `needs-decision`. Report that the review limit has been reached. Continuing requires an explicit decision from the responsible party and an updated `max_review_rounds`; do not reset `review_round`.
- Otherwise increment `review_round` by one. Never exceed `max_review_rounds`.

## Review depth by round

### Round 1: complete review

Review the whole plan against the checklist below. Consolidate overlapping findings and report only concrete, actionable problems.

### Subsequent permitted rounds: convergence review

Do not restart the review from scratch. Check only:

- whether existing `addressed` or `open` findings meet their recorded `close_when` conditions;
- whether the revisions introduced regressions or contradictions;
- whether the revised plan remains executable and satisfies its acceptance criteria.

After Round 1, add a new blocking finding only when it was caused by a revision, supported by newly available evidence, or is a clearly missed high-risk defect. Mark it with `late_finding: true` and state why it appears late. Do not introduce new style preferences, optional abstractions, or scope expansion.

## Review checklist

Check only relevant dimensions:

- **Goal traceability:** the plan solves the stated problem and covers every acceptance criterion.
- **Decision fidelity:** it preserves approved brainstorm decisions unless repository evidence contradicts them.
- **Repository grounding:** referenced paths, symbols, patterns, dependencies, and commands exist or are explicitly identified as assumptions or discovery steps.
- **Executability:** tasks are ordered, bounded, and contain observable `Done when` criteria; the implementer does not have to infer completion.
- **Correctness and completeness:** relevant failures, edge cases, compatibility, migrations, rollout, rollback, security, observability, and external actions are covered.
- **Testing:** verification matches the repository and the changed behavior, including relevant failure paths. Repository task completion is separate from required external acceptance checks; each external check has an explicit prerequisite and observable evidence, including a human observer when the requirement explicitly calls for one. Preserve the agreed quality level without adding unrequested polish or moving required acceptance out of scope.
- **Scope and simplicity:** no unrelated cleanup, speculative flexibility, premature abstraction, or avoidable coupling.

Do not block on personal style preferences, harmless naming choices, optional refactoring, hypothetical future requirements, or details the implementer can safely determine locally.

## Finding format

Place each finding immediately after the affected plan text:

```markdown
<!-- PLAN-REVIEW
id: PR-001
severity: MAJOR
introduced_round: 1
status: open
late_finding: false
evidence: `src/example.py:42` contradicts the proposed call sequence.
issue: The migration order is unsafe for the currently deployed version.
impact: Old application instances can fail while the schema is rolling out.
close_when: The plan defines an expand/contract sequence and rollback procedure.
backlog_candidate: false
-->
```

Rules:

- Use stable sequential IDs and never recreate the same issue under another ID.
- Severity is `CRITICAL`, `MAJOR`, or `MINOR`.
- Every finding identifies the issue, impact, repository evidence, and an observable `close_when` condition.
- Questions are not findings unless the unanswered decision prevents safe execution.
- The planner may change `status` from `open` to `addressed` and add a `resolution`. Only the reviewer changes it to `resolved` or reopens it with evidence.
- Do not delete findings during the active review cycle. After the current plan revision reaches `approved` or `approved-with-notes`, the backlog skill may remove an explicitly accepted `MINOR` backlog candidate, but only after its backlog file has been written successfully.
- Reopen a resolved finding only when new evidence shows its `close_when` condition is no longer met.
- Set `backlog_candidate: true` only for a real, non-blocking `MINOR` item outside the current plan's required scope. Never defer a current acceptance criterion or a `CRITICAL`/`MAJOR` issue to backlog.
- Do not create backlog files during review. After review, an authorized participant may invoke the backlog skill for selected candidates. That skill preserves the finding in a standalone backlog file and then removes its complete `PLAN-REVIEW` block from the plan so deferred work does not consume plan context.

## Severity and verdict

- `CRITICAL`: the plan would fail, violate a contract, damage data, create a serious security risk, or cannot safely be executed.
- `MAJOR`: a material omission or design problem must be corrected before implementation.
- `MINOR`: optional improvement or deferred work that does not prevent safe implementation.

For verdicts, an unresolved finding has status `open` or `addressed`. Only `resolved` findings are closed.

After updating all findings, set review metadata:

- No unresolved `CRITICAL` or `MAJOR`, no unresolved `MINOR`: `review_status: approved`.
- No unresolved `CRITICAL` or `MAJOR`, but unresolved `MINOR`: `review_status: approved-with-notes`.
- Unresolved `CRITICAL` or `MAJOR`, before the final round: `review_status: needs-revision`.
- Unresolved `CRITICAL` or `MAJOR` at the final round: `review_status: needs-decision`.

Always set `reviewed_revision` to the `plan_revision` that was reviewed.

`MINOR` findings never sustain another review round. Backlog candidates are suggestions, not gates.

## Report

Keep evidence and resolutions concise: cite the affected criterion/location and the decisive fact, not full transcripts or repeated plan paragraphs.

After saving the annotations, report:

- the exact repository-relative plan path;
- the reviewed plan revision and review round;
- counts of unresolved findings by severity;
- the resulting review status;
- any `MINOR` findings marked as backlog candidates.

If the result is `needs-decision`, list the precise unresolved choices or evidence needed for the responsible party. Do not launch another review, revise the plan, create backlog entries, or begin implementation.
