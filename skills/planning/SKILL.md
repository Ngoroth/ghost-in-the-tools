---
name: planning
description: "Use when writing a repo implementation plan; saves it."
license: MIT
compatibility: "OpenAI Codex; requires repository file access and preferably git."
metadata:
  author: "Daniil(Ngoroth) and Bes"
  version: "1.2.0"
---

# Planning

Create a concrete implementation plan grounded in the current repository. Planning ends with a saved plan; it does not include implementation.

## Rules

- Treat the repository as read-only except for the final plan file under `docs/plans/`.
- Reuse approved decisions from the conversation and any relevant brainstorm record. Do not reopen settled questions without new evidence.
- Ask exactly one meaningful question per message and only when the answer can change the plan.
- Write a plan only after every material decision that can change its scope, approach, task graph, dependencies, compatibility, failure behavior, or acceptance criteria is settled. Do not use the plan to make those decisions later.
- A plan must be linear and executable as written. Do not include alternative approaches, `TBD`, "choose during implementation", decision gates, or conditional task branches whose outcome changes downstream implementation.
- Distinguish repository facts, agent recommendations, assumptions, and user decisions.
- Prefer the smallest solution that satisfies the acceptance criteria. Apply YAGNI and avoid premature abstraction.
- Never require the implementer to guess when work is complete. Give every task explicit, observable completion criteria.
- Keep plan authorship separate from review: the planning session changes plan content, while an independent review session changes only review metadata and `PLAN-REVIEW` annotations.
- Do not modify source, tests, or configuration. Do not commit, push, or implement unless separately requested after the plan is saved.

## Workflow

### 1. Understand the work

1. Find the repository root, preferably with `git rev-parse --show-toplevel`. If it cannot be identified, ask for its path.
2. Read applicable instructions and relevant context: `AGENTS.md`, `CLAUDE.md` when present, README/docs, related brainstorm records, nearby code and tests, build configuration, and useful recent commits.
3. Inspect enough context to identify real file paths, existing patterns, dependencies, and verification commands. Do not invent them.
4. Briefly summarize the goal, scope, acceptance criteria, constraints, and any decisions that still prevent planning.

### 2. Pass the decision-readiness gate

Ask one question at a time when required. Prefer 2-4 concrete choices and put the recommendation first.

Clarify only material gaps such as:

- intended behavior and explicit non-goals;
- compatibility or migration requirements;
- error and edge-case behavior;
- testing expectations and the intended quality level (reuse the brainstorm decision);
- rollout or external dependencies.

Before writing, confirm that the selected scope and approach already determine:

- component boundaries and integration points;
- technology, provider, dependency, protocol, data-format, and version choices that affect the tasks;
- compatibility, migration, persistence, security, privacy, and failure behavior where relevant;
- rollout, rollback, external prerequisites, verification strategy, and the observable quality bar.

Resolve a single isolated gap by asking the user one focused question. When several connected decisions remain, alternatives require design tradeoffs, or feasibility evidence is missing, recommend `$brainstorm` and stop without creating a plan. State exactly which decisions or evidence the brainstorm must settle.

If the user intentionally defers a material decision, do not move it into the plan. Explain that planning is blocked until the decision is made or the undecided work is removed from the plan's scope.

### 3. Select the approach

If the approach was already approved during brainstorming, use it unless repository evidence contradicts it.

Otherwise, when meaningful alternatives exist:

1. Present 2-3 genuinely different approaches.
2. Lead with the recommendation and summarize benefits, costs, and risks.
3. Let the user select, combine, or reject them before writing the final plan.

Skip artificial alternatives when there is one clear path or the user already specified the implementation method.

Do not save a plan until one approach is selected and every material consequence for the task graph and acceptance criteria is resolved. Repository inspection may establish facts, but implementation must not be tasked with discovering which architecture, dependency, provider, model, schema, migration strategy, or product behavior the plan should use.

### 4. Write the plan

Create exactly one file for the planning session:

`docs/plans/YYYY-MM-DD-HHMM-<task-slug>.md`

- Use the user's local date and time when available.
- Use a short lowercase ASCII kebab-case slug.
- Never overwrite an unrelated file; append `-2`, `-3`, and so on when needed.
- If the same conversation revises the same plan, update the same file and refresh `Updated`. After review has started, also follow the review-revision rules below.
- Write in the conversation's language and preserve technical identifiers exactly.

Each task should be one small, reviewable logical unit. Order tasks by dependency. Include exact paths and commands supported by repository evidence. Do not guess, use placeholders, or defer material choices to the implementer. State what observable result makes each task complete.

Tasks may describe already-decided runtime behavior such as error handling, retries, or a fixed fallback. They must not branch into competing implementation paths or ask the implementer to select one. If feasibility of the chosen approach is not established and failure would require a different plan, stop and resolve that feasibility before writing this implementation plan.

For every code-changing task, include tests or explain why no automated test applies. Keep manual or external actions separate from repository implementation tasks.

Task-level `Done when` describes completion of that implementation unit and its repository-local verification. Put required device checks, external-system checks, and human judgments in a separate part of `Final validation`, with their prerequisite and evidence needed; do not repeat the same external blocker inside every task. These checks remain required for overall acceptance unless the user explicitly decides otherwise.

Use short identifiers for acceptance criteria and final checks. Reference them rather than restating the same requirement in multiple sections. Carry the agreed quality level, UI/language decisions, and representative quality examples into observable criteria; do not equate a successful build with acceptable usability or output quality.

Use this structure:

```markdown
---
plan_revision: 1
review_round: 0
max_review_rounds: 3
review_status: pending
reviewed_revision: null
---
# <Title> Implementation Plan

**Status:** Ready
**Created:** YYYY-MM-DD HH:MM <timezone if known>
**Updated:** <only when revised>
**Source brainstorm:** <path, if applicable>

## Goal
<Outcome and problem being solved.>

## Scope
- **In:** ...
- **Out:** ...

## Context and constraints
- ...

## Selected approach
<Approach and rationale.>

## Acceptance criteria
- [ ] ...

## Implementation steps

### Task 1: <Specific outcome>
**Objective:** ...
**Files:**
- Create: `path`
- Modify: `path`
- Test: `path`
**Depends on:** None | Task N
**Done when:** <Observable completion criteria; no judgment left to the implementer.>

- [ ] implement the scoped change
- [ ] handle specified errors and edge cases
- [ ] add or update relevant tests
- [ ] run `<exact command>`
- [ ] verify `<observable result>`

## Final validation
- [ ] run relevant focused tests
- [ ] run the broader required checks
- [ ] verify every acceptance criterion
- [ ] review the final diff for scope and regressions

### Required external or human checks (when applicable)
- [ ] <ID>: <observable outcome> — prerequisite: <device/access/person>; evidence: <observation or record>

## Risks and mitigations
- <Known residual risk and the already-selected mitigation or stopping condition.>

## Post-completion
<Manual, deployment, or external-system actions; no implementation checkboxes.>
```

Omit inapplicable fields rather than filling them with fiction. Add short code or contract examples only when they remove real ambiguity.

Do not create or save a draft plan with unresolved material decisions. Ask the next focused question or recommend `$brainstorm` instead.

### 5. Revise after independent review

When revising a plan that contains `PLAN-REVIEW` findings:

1. Change the plan's substantive content only when addressing a finding or an explicitly approved scope change.
2. For each addressed finding, change its `status` from `open` to `addressed` and add a concise `resolution` stating where the plan changed. Do not mark it `resolved`; only the independent reviewer does that.
3. Do not delete review blocks while revising the plan or alter their ID, severity, evidence, issue, impact, or `close_when` fields. The only deletion allowed is a separate post-review handoff performed by the backlog skill after it has preserved an explicitly accepted `MINOR` candidate in `docs/backlog/`.
4. Increment `plan_revision` exactly once for the revision pass, regardless of how many findings were addressed.
5. Set `review_status: pending` and `reviewed_revision: null`. Do not change `review_round`; the reviewer owns that counter.
6. A substantive edit after `approved` or `approved-with-notes` invalidates approval in the same way.
7. Never defer a current acceptance criterion or an open `CRITICAL`/`MAJOR` finding to backlog. After the current revision is approved, a non-blocking `MINOR` marked `backlog_candidate: true` may be filed with the backlog skill only after explicit user approval. Once the backlog file is safely written, that skill removes the complete finding block from the plan so deferred work no longer consumes plan context.

Review annotations alone do not increment `plan_revision`. If `review_status` is `needs-human-decision`, obtain the required human decision before another substantive revision or review attempt.

### 6. Review and report

Before reporting completion, verify that:

- the plan exists under `docs/plans/` in the correct repository;
- tasks are ordered, scoped, and independently verifiable;
- the plan contains one selected approach and a linear task graph, with no unresolved alternatives, decision gates, placeholders, or implementation-time choices that could change downstream work;
- every task has explicit, observable completion criteria;
- file paths and commands come from repository evidence or an explicitly confirmed prerequisite;
- code-changing tasks include appropriate testing;
- all acceptance criteria are covered;
- every material decision that affects the plan is recorded as settled context rather than an open question for the implementer;
- the plan contains no unnecessary features or unrelated cleanup;
- no project files other than the plan were changed.

Report the exact repository-relative path. Do not automatically commit, review, or execute the plan.
