---
name: brainstorm
description: "Use when brainstorming a repo change; guides and records."
license: MIT
compatibility: "OpenAI Codex; requires repository file access and preferably git."
metadata:
  author: "Daniil(Ngoroth) and Bes"
  version: "2.0.0"
---

# Brainstorm

Turn a rough idea into a repository-grounded design through a concise, collaborative dialogue. Do not turn the brainstorm into implementation.

## Rules

- Treat the repository as read-only until the final brainstorm record is written.
- Required decisions belong to the responsible party identified by the user's chosen process or supplied task context, whether a person or automated participant. Executing this skill does not confer that authority; report missing responsibility or decisions and reuse applicable decisions already supplied.
- Use plain language in the user dialogue. Explain proposals through what the user will do, what result they will get, and the consequences of each choice. Use technical terms only when needed to make a decision, and briefly explain them. Make questions answerable without knowing the project's internal architecture.
- Ask at most one question per message, only when its answer can materially change the design. Prefer 2-4 choices when useful and put the recommendation first.
- Reuse information and decisions already provided; do not ask for the same information or approval again unless new evidence changes it.
- Distinguish repository facts, agent recommendations, and decisions from the responsible party.
- Keep scope minimal and apply YAGNI.
- Do not modify code, tests, configuration, or plans. Do not commit, push, or implement under this skill; subsequent work requires applicable authorization from the responsible party.

## Workflow

### 1. Understand

1. Find the repository root, preferably with `git rev-parse --show-toplevel`. If no repository can be identified, ask for its path.
2. Read applicable instructions and relevant context: `AGENTS.md`, `CLAUDE.md` when present, README/docs, nearby code and tests, and useful recent commits.
3. Briefly restate the goal, known constraints, success criteria, and important unknowns.

### 2. Clarify

- Ask only questions whose answers can materially change the design.
- Focus on scope, users, integration points, compatibility, failure behavior, and verification.
- Establish the intended quality level when it affects the design: technical prototype, personal-use tool, or release-ready product. For UI work, agree on interface language, the main user flow, and a lightweight sketch or reference when needed. For quality-sensitive output, agree on representative examples and an acceptable outcome. Do not invent approval or require irrelevant design documents.
- Challenge assumptions politely.
- Resolve high-impact ambiguity before proposing a design. Record intentionally deferred details as open questions.

### 3. Explore approaches

1. Present 2-3 genuinely different approaches when alternatives exist.
2. Lead with the recommended approach and explain why it best fits the constraints.
3. Summarize the meaningful benefits, costs, and risks of each option. When costs affect the choice, describe the scope of changes, dependencies, resource needs, recurring operations, and maintenance burden. Distinguish one-time preparation from work repeated on each use, and identify what can be reused. Do not estimate implementation or execution time. State the basis and uncertainty of any quantitative resource or monetary estimate; do not invent precision or run expensive experiments solely to produce an estimate.
4. Obtain the approach decision from the responsible party, who may select, combine, or reject the options. Use an already supplied decision when applicable. Never treat a recommendation as an approved decision.

### 4. Validate the design

Present one short, coherent section at a time and confirm it before continuing. Cover only relevant areas, such as components, flows, contracts, persistence, failures, security, observability, testing, and rollout.

Each section should explain a coherent design decision and its practical consequences. State exactly what the responsible party is being asked to confirm. Do not split a connected decision into trivial confirmations or ask again about an already approved decision unless new evidence changes it.

Track approved decisions, rejected alternatives and reasons, risks, and open questions. Backtrack when an authorized correction changes an assumption.

### 5. Save the result

The brainstorm is complete only when the responsible party explicitly approves the overall design or authorizes finalizing the record. Save before offering a next action.

1. Create `docs/brainstorm/` under the repository root.
2. Write exactly one file for the session:
   `docs/brainstorm/YYYY-MM-DD-HHMM-<topic-slug>.md`.
3. Use the user's local date and time when available. Use a short lowercase ASCII kebab-case slug.
4. Never overwrite an unrelated file; append `-2`, `-3`, and so on when needed.
5. Write in the brainstorm's language and preserve technical identifiers exactly.
6. Save the settled result and rationale, not a transcript. Preserve any material cost and reuse tradeoffs discussed with the user.
7. If the same conversation continues the same brainstorm, update the same file and add or refresh `Updated`. A separate topic gets a new file.

Use this compact structure:

```markdown
# <Topic>

**Status:** Finalized | Draft with open questions
**Created:** YYYY-MM-DD HH:MM <timezone if known>
**Updated:** <only when revised>

## Summary
<Selected direction and why.>

## Goal and success criteria
- Intended quality level and observable success: ...

## Context and constraints
- ...

## Approaches considered
- **Selected:** ...
- **Rejected or deferred:** ... — reason

## Decisions and design
- **Decision:** ... — rationale

## Risks and open questions
- ...

## Next step
<One action or “Not selected during this brainstorm.”>
```

If no approach was selected, use `Draft with open questions` and do not invent a decision.

## Verification

After writing, verify that:

- the file exists under `docs/brainstorm/` in the correct repository;
- it accurately records approved decisions and unresolved questions;
- no source or configuration files were changed;
- the user receives the exact repository-relative path.

Do not claim the result was saved until these checks pass.
