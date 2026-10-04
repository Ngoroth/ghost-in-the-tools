---
name: goal-validation
description: "Use after code review to validate current repository behavior against an approved plan's goal and every observable completion criterion."
license: MIT
compatibility: "Agent Skills-compatible coding agents; requires repository read access, permission to run safe project checks, and permission to update only the selected docs/reviews/ Markdown artifact."
metadata:
  author: "Daniil(Ngoroth) and Bes"
  version: "2.0.0"
---

# Goal Validation

Independently demonstrate whether the current implementation achieves the plan's original goal and observable completion criteria. Validate outcomes rather than reviewing code quality again.

## Contract

- Prefer a fresh session that did not implement the change. Regardless of session history, verify evidence directly instead of trusting summaries.
- Validate the repository state that exists when invoked. Do not track or compare states between workflow stages; orchestration is external.
- Required decisions belong to the responsible party identified by the user's chosen process or supplied task context, whether a person or automated participant. Executing this skill does not confer acceptance authority; report missing responsibility or decisions and reuse applicable decisions already supplied.
- Treat source, tests, configuration, the plan, and review findings as read-only. Write only validation state, `acceptance_status`, and, when explicitly supplied, the acceptance decision in the selected `docs/reviews/*.md` artifact.
- Safe tests, builds, linters, local execution, and read-only diagnostics are allowed. Do not deploy, mutate external systems, use credentials, or perform destructive checks without explicit authorization.
- Do not edit implementation files, apply fixes, stage, commit, push, post comments, merge, create backlog items, or start another workflow stage.
- Replace any secret or credential value in validation evidence with `[REDACTED]`.

## Input and preflight

Require one explicit repository-relative path:

```text
<review-artifact-path>
```

It must identify the existing `docs/reviews/<task-slug>.md` created by code review. If the path is missing or ambiguous, ask one concise question; do not select a file by modification time.

1. Find the repository root, preferably with `git rev-parse --show-toplevel`.
2. Read the complete review artifact and obtain its `plan` path.
3. Read the complete plan plus applicable `AGENTS.md`, `CLAUDE.md`, README, contribution rules, and relevant product or operational documentation.
4. Extract the original `Goal`, every `Acceptance criteria` item, every task-level `Done when`, `Final validation`, and relevant `Post-completion` actions.
5. Require the code-review artifact's `review_status` to be `approved` or `approved-with-notes`, with no `open` or `addressed` `CRITICAL` or `MAJOR` findings. Otherwise stop and report that code review is not settled; do not write validation state. Read the remaining findings as context, but do not repeat code review.

## Validation scope

Validate the current repository and working tree, including committed, staged, unstaged, and untracked implementation files when relevant to observable behavior.

Keep each plan criterion traceable to its source. Merge only exact duplicates; do not silently omit a criterion because another check seems similar.

Validate only the agreed current scope. Do not turn optional improvements, excluded work, or unrelated pre-existing problems into failures. Report manual deployment or external-system actions separately unless the plan explicitly makes them acceptance criteria.

## Procedure

### 1. Build the criterion inventory

Create a checklist containing:

- the overall user-visible goal;
- every acceptance criterion;
- every task-level `Done when` condition;
- every required final-validation check.

For each item, reference its plan ID (or section/task anchor) and briefly name the observable claim without copying the whole criterion. Reuse one evidence entry for checks that establish multiple criteria; retain traceability to every required item. If the plan is genuinely too ambiguous to determine success, mark that item `BLOCKED` and explain the missing decision or oracle.

### 2. Choose the strongest available oracle

Prefer direct evidence in this order when applicable:

1. end-to-end or user-visible behavior;
2. integration or API behavior;
3. focused automated tests or a regression reproduction;
4. build, lint, type, schema, migration, or configuration checks;
5. direct inspection of a concrete artifact or contract;
6. an explicitly identified manual or external check.

A lower-level passing test does not prove a higher-level claim unless their connection is explicit.

### 3. Execute and inspect

Run the strongest safe checks available in the current environment. Record exact commands and their outcomes. Inspect generated output, responses, logs, or artifacts when the criterion depends on them.

Never mark an unexecuted check as passed. A claimed executor result is a lead, not evidence. If a required check cannot run, record the exact environmental or external dependency instead of guessing.

### 4. Exercise the overall outcome

Where practical, perform at least one representative path from input or user action to the promised observable result. Confirm that passing individual tasks actually composes into the original goal.

### 5. Classify the result

Use only:

- `PASS` — the claim is demonstrated by concrete evidence;
- `FAIL` — observed behavior or evidence contradicts the claim;
- `BLOCKED` — no failure was demonstrated, but required evidence is unavailable.

Set the overall `validation_status`:

- `failed` if the overall goal or any required criterion is `FAIL`;
- otherwise `blocked` if any required criterion is `BLOCKED`;
- otherwise `passed` only when the overall goal and every required criterion are `PASS`.

## Validation artifact

In the selected review artifact, add or update:

```yaml
validation_status: passed | failed | blocked
acceptance_status: not_recorded | accepted | accepted_with_limitations | rejected
```

`validation_status` is the evidence-based technical verdict. `acceptance_status` records the responsible party's explicit decision applicable to the current result; record the decision maker, its source, and the accepted scope, and use `not_recorded` when no applicable decision has been supplied. Preserve the acceptance record. On later validation runs, retain `accepted`/`accepted_with_limitations` only if all current `FAIL`/`BLOCKED` results are covered by that decision. New or worsened failures or blockers require a new decision: set `acceptance_status` to `not_recorded` and explain what changed. Preserve `rejected` until the responsible party changes it. For legacy artifacts, apply the same rules to an explicit decision in the existing acceptance record; otherwise use `not_recorded`.

Append one validation block at the end of the file. On a later run, replace the existing block between the markers instead of accumulating attempt history:

```markdown
<!-- GOAL-VALIDATION:START -->
## Goal validation

**Status:** passed | failed | blocked

### Overall goal
- PASS | FAIL | BLOCKED — <observable outcome>
  - Evidence: <command, result, behavior, or exact missing prerequisite>

### Criteria
- PASS | FAIL | BLOCKED — `<source criterion>`
  - Evidence: <concise concrete evidence>

### Commands
- `<exact command>` — <exit/result>

### Manual or external actions
- <remaining action, or `None`>
<!-- GOAL-VALIDATION:END -->
```

Include every criterion exactly once. Keep evidence concise but sufficient to reproduce or inspect. Describe each shared missing prerequisite once with the affected criterion IDs; criterion counts are coverage counts, not independent defect counts. Preserve all review findings, unrelated frontmatter, and any acceptance record outside the validation markers.

## Acceptance is separate

The responsible party may accept or reject a prototype or iteration independently of the technical verdict. This decision is not evidence that checks passed: do not convert `BLOCKED` or `FAIL` to `PASS` or weaken the original criteria merely because the iteration is accepted. Use supplied observations only for claims they actually establish, clearly attributing their source.

When the responsible party explicitly supplies an acceptance decision, update `acceptance_status` and append or update a short `## Acceptance` section outside the validation markers in the same review artifact:

- `accepted` — the responsible party accepts an iteration whose validation passed and states no additional limitation;
- `accepted_with_limitations` — the responsible party accepts closure while validation is failed or blocked, or while explicitly acknowledging a waived or deferred limitation;
- `rejected` — the responsible party does not accept the iteration;
- `not_recorded` — no explicit decision applies to the current result.

Record the decision maker, decision source, and accepted scope, any explicitly accepted failed or blocked criteria, unexecuted checks, and deferred concerns. Do not infer waivers or acceptance from a vague positive comment. Preserve this record on later validation runs. Recording a decision does not authorize cleanup, implementation, commit, or publication.

If the responsible party asks to "make it pass" because they accept a known failure or missing check, preserve the evidence-based `validation_status`, record the appropriate acceptance status, and explain both results together. An `accepted` or `accepted_with_limitations` decision means the iteration may proceed to wrap-up; it does not mean validation passed.

## Report and stop

Report:

- review artifact and plan paths;
- overall `validation_status`;
- `acceptance_status` and whether the iteration may proceed to wrap-up;
- counts of `PASS`, `FAIL`, and `BLOCKED` criteria;
- exact failed or blocked criteria and what evidence or action is missing;
- commands actually run and their outcomes;
- remaining manual or external actions.

A validation failure is an acceptance result, not a code-review finding. Do not assign severity, create `CR-NNN`, edit the implementation, decide whether another review is needed, or launch fixes automatically. The responsible party determines the next workflow step.

Stop after recording and reporting the result. Making acceptance decisions, commit, publication, backlog transfer, retrospective, and cleanup are outside this skill; only recording an explicitly supplied decision is allowed as described above.
