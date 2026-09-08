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
- **`code-review`** — independently reviews the complete current change set: committed changes relative to a base ref, staged, unstaged, and relevant untracked files.
- **`goal-validation`** — validates the implemented outcome against the plan and records `PASS`, `FAIL`, or `BLOCKED` evidence.
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
- Code approval and external acceptance are separate.
- Missing external evidence is `BLOCKED`, not an invented implementation defect.
- Human acceptance never silently converts `FAIL` or `BLOCKED` into `PASS`.
- Deferred findings are removed from review context only after a verified backlog write.
- Skills do not automatically commit, push, merge, deploy, or publish.
- Secrets are never stored in workflow artifacts.

## Repository contents

Each skill is instruction-only and consists of one `SKILL.md`. There are no hooks, executables, or bundled automation scripts.

## License

MIT. See [LICENSE](LICENSE).

## Acknowledgements

Parts of the workflow were informed by Umputun's [`cc-thingz`](https://github.com/umputun/cc-thingz) skills and practical discussions in [Radio-T](https://radio-t.com/). Individual source credits are preserved in the relevant skill metadata.
