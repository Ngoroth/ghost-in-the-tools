---
name: goal-validation
description: "Use after code review to validate current repository behavior against an approved plan's goal and every observable completion criterion."
license: MIT
compatibility: "Agent Skills-compatible coding agents; requires repository read access, permission to run safe project checks, and permission to update only the selected docs/reviews/ Markdown artifact."
metadata:
  author: "Daniil(Ngoroth) and Bes"
  version: "1.0.1"
---

# Goal Validation

Independently demonstrate whether the current implementation achieves the plan's original goal and observable completion criteria. Validate outcomes rather than reviewing code quality again.

## Contract

- Prefer a fresh session that did not implement the change. Regardless of session history, verify evidence directly instead of trusting summaries.
- Validate the repository state that exists when invoked. Do not track or compare states between workflow stages; orchestration is external.
- Treat source, tests, configuration, the plan, and review findings as read-only. Write only validation state and, when explicitly requested, the supplied human-acceptance record in the selected `docs/reviews/*.md` artifact.
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
5. Read code-review status and findings as context, but do not repeat code review or police the order in which the user invokes stages.

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
```

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

Include every criterion exactly once. Keep evidence concise but sufficient to reproduce or inspect. Describe each shared missing prerequisite once with the affected criterion IDs; criterion counts are coverage counts, not independent defect counts. Preserve all review findings, unrelated frontmatter, and any human-acceptance record outside the validation markers.

## Human acceptance is separate

A user may accept a prototype or iteration while checks remain unexecuted. This is a human decision, not evidence that those checks passed: do not convert `BLOCKED` or `FAIL` to `PASS` or weaken the original criteria merely because the user accepts the iteration. Use specific user-reported observations only for claims they actually establish, clearly attributing the evidence.

If the user explicitly asks to record an acceptance/closure decision, append or update a short `## Human acceptance` section outside the validation markers in the same review artifact: the decision and accepted scope, any explicitly waived/unexecuted checks, and deferred concerns. Do not infer waivers or acceptance from a vague positive comment. Preserve this record on later validation runs. Recording a decision does not authorize cleanup, implementation, commit, or publication.

## Report and stop

Report:

- review artifact and plan paths;
- overall `validation_status`;
- counts of `PASS`, `FAIL`, and `BLOCKED` criteria;
- exact failed or blocked criteria and what evidence or action is missing;
- commands actually run and their outcomes;
- remaining manual or external actions.

A validation failure is an acceptance result, not a code-review finding. Do not assign severity, create `CR-NNN`, edit the implementation, decide whether another review is needed, or launch fixes automatically. The user manages the next workflow step.

Stop after recording and reporting the result. Making the human acceptance decision, commit, publication, backlog transfer, retrospective, and cleanup are outside this skill; only recording an explicitly supplied decision is allowed as described above.
