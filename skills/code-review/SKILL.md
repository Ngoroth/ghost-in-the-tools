---
name: code-review
description: "Use in a fresh independent session to review implemented repository changes against an approved plan and record verified findings."
license: MIT
compatibility: "Agent Skills-compatible coding agents; requires Git repository read access, permission to run project checks, and permission to write only the selected docs/reviews/ Markdown artifact."
metadata:
  author: "Daniil(Ngoroth) and Bes"
  version: "1.1.1"
---

# Code Review

Independently review an implementation against its approved plan, exact Git scope, repository contracts, and executable evidence. Record only verified, material findings. Stop after review; do not fix the code.

## Contract

- Run in a fresh session that did not implement the change. If this session authored or substantially edited it, stop and request another reviewer session.
- Session launch and communication are external. This skill uses repository artifacts and does not depend on a terminal manager, subagent system, or transport.
- Review the repository state that exists when invoked. Do not track or police changes made between workflow stages; session orchestration is external.
- Treat source, tests, configuration, plans, and backlog files as read-only. Write only the selected `docs/reviews/*.md` artifact.
- Relevant tests, builds, linters, and read-only diagnostics are allowed. Do not run deployments, destructive commands, external writes, or credentialed checks without explicit authorization.
- Do not edit source, apply fixes, stage files, commit, push, post comments, merge, switch branches, or create worktrees.
- Replace any secret or credential value in review text with `[REDACTED]`.

## Input and preflight

Require:

```text
<approved-plan-path> [base-ref]
```

The plan path must be explicit and repository-relative. Ask one concise question if it is missing or ambiguous; do not select by modification time.

1. Find the repository root, preferably with `git rev-parse --show-toplevel`.
2. Read the complete plan and applicable `AGENTS.md`, `CLAUDE.md`, README, contribution rules, and project documentation.
3. Require `review_status` to be `approved` or `approved-with-notes` and `reviewed_revision` to equal `plan_revision`. Otherwise stop: the implementation is not based on a currently approved plan.
4. Read linked brainstorm or decision records only when needed to understand the intended outcome or an invariant.
5. If a review artifact already names this plan, continue it. Never create a second lifecycle because the session changed.

## Exact review scope

A review is invalid until the complete implementation change set is known.

1. Inspect the current branch and `git status --short`.
2. Resolve an explicit `base-ref`; otherwise, on a feature branch, use the merge base with the default branch.
3. Review the complete current implementation change set: committed changes from the base through `HEAD`, staged changes, unstaged changes, and every untracked implementation file with its contents.
4. Exclude only the selected `docs/reviews/*.md` coordination artifact. Do not require implementation changes to be committed or staged before review.
5. If default-branch commits or unrelated branch history make the boundary uncertain, ask for the implementation's starting SHA. Do not guess.
6. If unrelated work cannot be separated, record a blocking scope finding instead of reviewing a convenient subset.

A dedicated feature branch or worktree is preferred because it makes this boundary deterministic without an implementation skill.

## Review artifact and state

Use one review-evidence file per plan:

```text
docs/reviews/<task-slug>.md
```

Derive the slug from the plan filename after removing its timestamp prefix. Reuse an artifact that names the same plan. Never overwrite an unrelated file; append `-2`, `-3`, and so on.

```yaml
---
plan: docs/plans/<plan>.md
plan_revision: 1
base_ref: <ref>
base_sha: <sha>
review_round: 0
max_review_rounds: 3
review_status: pending
---
```

Preserve unrelated frontmatter.

The artifact is workflow evidence. This skill may create and update it, but must not stage, commit, push, or publish it. Preserve it through goal validation and wrap-up. Wrap-up keeps it as evidence and repairs its plan reference when the plan is archived; delete it only on a separate explicit user request.

Before a round:

- Rebuild the complete current change set from Git and untracked files; do not rely on the implementation session's summary.
- If status is `needs-human-decision`, report the unresolved blockers and stop unless the user resolves them and explicitly authorizes another bounded cycle.
- If `review_round` equals `max_review_rounds` and blockers remain, set `needs-human-decision` and stop.
- Otherwise increment `review_round` once. Never exceed the cap automatically.

## Review procedure

Read the cumulative diff once, then inspect enough surrounding context to understand behavior: changed files, callers, interfaces, schemas, migrations, dependencies, tests, CI/build rules, relevant history, and project conventions. The executor's test report is a lead, not proof.

Run the strongest safe checks named by the plan and repository, focused first and broader when practical. Record exact commands and results. Never convert an unexecuted or failed check into a pass. Missing external evidence alone (for example, an unattached device, unavailable credentials, or pending human observation) is incomplete verification, not a finding. Record the missing prerequisite and affected criteria in a concise `Incomplete verification` section without a `CR-NNN` or severity. Do not lower the code-review verdict for that reason alone; goal validation owns `BLOCKED`. An actual implementation, test, or validation-procedure defect remains a finding, including missing required repository tests or a procedure that cannot validate the promised behavior. `approved` means no blocking implementation defect was found, not that the product has passed external acceptance.

When tests or CI configuration changed, inspect it first and confirm coverage, thresholds, test selection, linting, and failure behavior were not weakened.

### Round 1: complete review

Use four passes:

1. **Plan and scope fidelity** — promised behavior, acceptance coverage, missing work, unapproved approach changes, and unrelated edits.
2. **Correctness and risk** — contracts, errors, edge cases, authorization, trust boundaries, data/migrations, compatibility, concurrency, and recovery where relevant.
3. **Tests and operability** — regression evidence, failure paths, logs, metrics, rollout, rollback, and required operational checks.
4. **Simplicity and reuse** — duplicate utilities, unnecessary abstractions, dead code, and material divergence from deliberate project patterns.

Trace at least the most consequential changed path from input to observable output. For a bug fix, require a test or equivalent evidence that distinguishes pre-change failure from post-change success.

### Verify each candidate

A suspicion is not a finding. Before recording it:

1. Reopen the exact location and surrounding code.
2. Search relevant callers, contracts, tests, and prior art.
3. Demonstrate impact with a check, trace, contract contradiction, or concrete counterexample.
4. Confirm the issue was introduced, activated, or materially worsened by this implementation.
5. Deduplicate overlapping observations and keep the root cause.

Drop style preferences, generic advice, speculative risks, unchanged pre-existing issues, optional cleanup disguised as correctness, and claims contradicted by repository conventions or actual results.

### Rounds 2 and 3: convergence review

Do not restart a full review. Check only:

- each `open` or `addressed` blocker's `close_when` condition;
- the complete cumulative diff for regressions introduced by fixes;
- continued plan and acceptance-criteria coverage;
- every current committed, staged, unstaged, and untracked implementation change.

After Round 1, do not add cosmetic findings, optional refactors, or new `MINOR` preferences. A new blocker is valid only when a fix introduced it, new evidence appeared, or a demonstrably high-risk defect was missed. Mark it `late_finding: true` and explain why it is late.

## Findings

Use stable sequential IDs and severity order:

```markdown
## CR-001 — <Specific title>

- severity: MAJOR
- introduced_round: 1
- status: open
- late_finding: false
- location: `src/example.ext:42`
- evidence: <repository evidence, command result, or reproduction>
- issue: <specific defect>
- impact: <observable consequence>
- close_when: <testable closure condition>
- backlog_candidate: false
```

Rules:

- Severity is `CRITICAL`, `MAJOR`, or `MINOR`.
- Every finding needs a precise location when one exists, evidence, impact, and observable `close_when`.
- An observed implementation defect that violates a current acceptance criterion or required `Done when` cannot be `MINOR`. An unexecuted external check is not an observed failure.
- Questions are findings only when the missing decision prevents safe acceptance.
- Keep IDs stable. The implementer may mark `open` as `addressed` and add `resolution`; only the reviewer marks `resolved` or reopens with evidence.
- Do not delete findings during active review. Set `backlog_candidate: true` only for real, non-blocking work outside current acceptance scope.

## Severity, verdict, and ownership

- `CRITICAL`: unsafe to accept — data loss, exploitable security failure, broken external contract, outage-class behavior, or no safe execution path.
- `MAJOR`: material correctness, compatibility, scope, or test/validation-procedure defect in the implementation; not mere unavailability of external acceptance evidence.
- `MINOR`: real optional improvement or independently useful deferred work.

For verdicts, an unresolved finding has status `open` or `addressed`. Only `resolved` findings are closed.

After inspecting the complete current change set, choose:

- no unresolved findings → `approved`;
- only unresolved `MINOR` → `approved-with-notes`;
- unresolved `CRITICAL`/`MAJOR` before Round 3 → `needs-fixes`;
- unresolved `CRITICAL`/`MAJOR` at Round 3 → `needs-human-decision`.

`MINOR` findings never sustain another review round.

The implementation session owns source changes and may mark findings `addressed`; it cannot resolve or approve them. The reviewer owns re-verification, `resolved` or reopened status, rounds, and verdict. Prefer the same reviewer session across rounds; a replacement continues the artifact and IDs.

Do not automatically start another round. Wait until fixes are reported ready or the user explicitly requests it.

## Backlog handoff

Only an approved, non-blocking `MINOR` outside current acceptance scope may be transferred, and only after explicit user acceptance.

The backlog skill writes and verifies one standalone item containing this review path, `CR-NNN`, evidence, impact, deferral reason, and `close_when`; only then it removes that finding section, preserving following independent sections, goal validation, and human acceptance. It changes `approved-with-notes` to `approved` only when no unresolved `MINOR` remains. On failure, keep the finding. Leave no stub or pointer after successful transfer.

Never transfer `CRITICAL`, `MAJOR`, or work required by an acceptance criterion.

## Report

Keep the artifact concise: record each command/result once, reference criterion IDs and evidence locations, and describe a shared external blocker once with its affected criteria. Do not copy whole plans or raw command transcripts.

Report:

- exact review artifact and plan paths;
- plan revision, base ref/SHA, round, and status;
- unresolved finding counts by severity;
- commands actually run and their outcomes;
- incomplete verification or external evidence still needed;
- `MINOR` backlog candidates.

If status is `needs-human-decision`, list the exact unresolved risks or evidence. Do not fix code, start another round, create backlog items, run final goal validation, or wrap up.
