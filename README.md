# Ghost in the Tools

A small, repository-native skill set for human-guided, AI-assisted software development with OpenAI Codex.

The workflow keeps decisions and evidence in ordinary Markdown files inside the project repository. It does not require a specific terminal, session manager, orchestration framework, or automatic Git workflow.

## Workflow

```text
brainstorm
→ planning
→ independent plan-review
→ human approval
→ implementation
→ independent code-review
→ fixes and bounded re-review
→ goal-validation
→ human acceptance
→ wrap-up
→ manual commit / push / merge
```

Implementation intentionally has no dedicated skill. The developer remains responsible for architecture, final code, review decisions, and publication.

## Skills

- **`brainstorm`** — turns a rough idea into an approved, repository-grounded design and saves it under `docs/brainstorm/`.
- **`planning`** — creates an executable implementation plan with observable completion criteria under `docs/plans/`.
- **`plan-review`** — independently reviews a plan in place, using bounded review rounds.
- **`code-review`** — independently reviews the complete current change set and preserves its review artifact as workflow evidence.
- **`goal-validation`** — validates the implemented outcome against the plan, records `PASS`, `FAIL`, or `BLOCKED` evidence, and keeps the user's acceptance decision separate from the technical verdict.
- **`backlog`** — stores deferred work as standalone files under `docs/backlog/` and safely transfers accepted non-blocking findings.
- **`wrap-up`** — records the outcome, accepted limits, follow-ups, and lessons, then archives a genuinely closed plan.
- **`session-work-summary`** — briefly explains what changed in the current coding session, how it was done, and what was actually checked.

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

To make the skills repository-specific instead, copy the folders into `<repository>/.agents/skills/`.

## Operating principles

- The human controls transitions between phases.
- Planning and review happen in separate sessions.
- Review rounds are bounded; unresolved blockers eventually require a human decision.
- Goal validation starts only after code review is `approved` or `approved-with-notes`, with no unresolved blocking findings (`open` or `addressed`).
- Code approval and external acceptance are separate.
- Missing external evidence is `BLOCKED`, not an invented implementation defect.
- Human acceptance never silently converts `FAIL` or `BLOCKED` into `PASS`.
- Validation records technical status and explicit human acceptance as separate states. New or worsened failures or blockers require renewed acceptance; rejection always prevents closure.
- A failed or blocked criterion may enter backlog only after explicit `accepted_with_limitations`; its validation evidence and verdict remain unchanged.
- Before writing, wrap-up rereads the authoritative artifacts and uses available session statuses only as consistency signals. Ongoing artifact changes prevent closure; a stale `blocked` session status alone does not.
- Deferred findings are removed from review context only after a verified backlog write.
- Skills do not automatically commit, push, merge, deploy, or publish.
- Secrets are never stored in workflow artifacts.

## Repository contents

Each skill is instruction-only and consists of one `SKILL.md`. There are no hooks, executables, or bundled automation scripts.

## License

MIT. See [LICENSE](LICENSE).

## Acknowledgements

Parts of the workflow were informed by Umputun's [`cc-thingz`](https://github.com/umputun/cc-thingz) skills and practical discussions in [Radio-T](https://radio-t.com/). Individual source credits are preserved in the relevant skill metadata.
