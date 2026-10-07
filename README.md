# Ghost in the Tools

A small, repository-native skill set for responsibility-driven, AI-assisted software development with OpenAI Codex.

The workflow keeps decisions and evidence in ordinary Markdown files inside the project repository. It does not require a specific terminal, session manager, orchestration framework, or automatic Git workflow.

## Workflow

```text
brainstorm
→ planning
→ independent plan-review
→ implementation authorization
→ implementation
→ independent code-review
→ fixes and bounded re-review
→ goal-validation
→ acceptance
→ wrap-up
→ manual commit / push / merge
```

Implementation intentionally has no dedicated skill. The user's chosen process assigns responsibility for decisions, implementation, and publication; skills do not require a particular mix of people and automated participants.

## Skills

- **`workflow-guide`** — explains how to choose and combine this skill set, checks stage prerequisites, and prepares context for another session without depending on an orchestration tool.
- **`brainstorm`** — turns a rough idea into an approved, repository-grounded design and saves it under `docs/brainstorm/`.
- **`planning`** — creates an executable implementation plan with observable completion criteria under `docs/plans/`.
- **`plan-review`** — independently reviews a plan in place, using bounded review rounds.
- **`code-review`** — independently reviews the complete current change set and preserves its review artifact as workflow evidence.
- **`goal-validation`** — validates the implemented outcome against the plan, records `PASS`, `FAIL`, or `BLOCKED` evidence, and keeps the responsible party's acceptance decision separate from the technical verdict.
- **`backlog`** — stores deferred work as standalone files under `docs/backlog/` and safely transfers accepted non-blocking findings.
- **`wrap-up`** — records the outcome, accepted limits, follow-ups, and lessons, then archives a genuinely closed plan.
- **`session-work-summary`** — briefly explains what changed in the current coding session, how it was done, and what was actually checked.
- **`skill-improvement`** — optionally reviews selected work against the skill contract and discusses evidence-supported skill changes one at a time; discussion does not authorize application.

## Install for Codex

### Linux or macOS

```bash
mkdir -p "$HOME/.agents/skills"
cp -R skills/* "$HOME/.agents/skills/"
```

### Windows PowerShell

```powershell
New-Item -ItemType Directory -Force "$HOME\.agents\skills" | Out-Null
Copy-Item -Recurse -Force ".\skills\*" "$HOME\.agents\skills\"
```

Codex detects skills automatically. If they do not appear, restart Codex. Invoke one explicitly with `$brainstorm`, `$planning`, `$plan-review`, and so on.

Use `$workflow-guide` to navigate the set, for example: “Which skill should I use next for `docs/plans/<plan>.md`, and what context does the next session need?” The guide describes the workflow and its handoffs; session launch and orchestration remain external.

To make the skills repository-specific instead, copy the folders into `<repository>/.agents/skills/`.

## Operating principles

- Required decisions belong to a responsible party identified by the user's chosen process or supplied task context, whether a person or automated participant. Skills do not assign that authority.
- Planning and review happen in separate sessions.
- Review rounds are bounded by `max_review_rounds` (default: 3); unresolved blockers at the final permitted round require a decision from the responsible party (`needs-decision`).
- Reaching the review limit prevents another round even when no blocking findings remain. Continuing requires an explicit decision from the responsible party and an updated `max_review_rounds`; `review_round` is not reset.
- Goal validation starts only after code review is `approved` or `approved-with-notes`, with no unresolved blocking findings (`open` or `addressed`).
- Code approval and external acceptance are separate.
- Progress checkboxes belong to the plan implementer and reflect completion evidence. Independent review, validation, and acceptance are complete only when their respective report or explicit decision says so; checking a box does not authorize a technical verdict, finding resolution, or acceptance.
- Missing external evidence is `BLOCKED`, not an invented implementation defect.
- Acceptance never silently converts `FAIL` or `BLOCKED` into `PASS`.
- Validation records technical status and explicit acceptance as separate states, including the decision maker, source, and scope. New or worsened failures or blockers require renewed acceptance; rejection always prevents closure.
- A failed or blocked criterion may enter backlog only after explicit `accepted_with_limitations`; its validation evidence and verdict remain unchanged.
- Before writing, wrap-up rereads the authoritative artifacts and uses available session statuses only as consistency signals. Ongoing artifact changes prevent closure; a stale `blocked` session status alone does not.
- Deferred findings are removed from review context only after a verified backlog write.
- Skills do not automatically commit, push, merge, deploy, or publish.
- Secrets are never stored in workflow artifacts.
- Applicable decisions and authorization already supplied remain valid within their scope. Missing responsibility or a required decision is reported, not replaced by invented approval; execution-environment permissions still apply.

## Repository contents

Each skill is instruction-only and consists of one `SKILL.md`. There are no hooks, executables, or bundled automation scripts.

## License

MIT. See [LICENSE](LICENSE).

## Acknowledgements

Parts of the workflow were informed by Umputun's [`cc-thingz`](https://github.com/umputun/cc-thingz) skills and practical discussions in [Radio-T](https://radio-t.com/). Individual source credits are preserved in the relevant skill metadata.
