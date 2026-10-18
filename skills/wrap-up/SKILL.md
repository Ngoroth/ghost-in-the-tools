---
name: wrap-up
description: "Use to close an iteration, capture agreed follow-ups, and automatically archive its workflow documents with one concise outcome note."
license: MIT
compatibility: "Agent Skills-compatible coding agents; requires repository access, Python 3, and the backlog skill for agreed follow-ups."
metadata:
  author: "Daniil(Ngoroth) and Bes"
  version: "2.1.1"
---

# Wrap up

Close one iteration and tidy its workflow documents without making the responsible party sort files. Use the conversation's language. This is part of closure, not a new review or acceptance stage.

Required decisions belong to the responsible party identified by the user's chosen process or supplied task context, whether a person or automated participant. Executing this skill does not confer acceptance authority. Reuse applicable decisions already supplied; report a genuinely missing decision instead of inventing it.

## 1. Establish closure before writing

Read the selected plan, its complete review/validation artifact, supplied acceptance decision, and relevant backlog items. Resolve the target from explicit context and links, never modification time. Ask only if several targets remain possible.

- Use existing evidence; do not rerun application tests or review. Do not invent acceptance, resolve review findings, tick implementation tasks, or convert `FAIL`/`BLOCKED` into `PASS`.
- Require settled code review with no unresolved blocking findings, settled validation, and completion of required work, or explicit acceptance covering every remaining failed/blocked criterion and unfinished scope. A rejection prevents closure. Invoking wrap-up is not acceptance.
- Preserve the technical verdict independently of acceptance. Missing external proof is not completion; an accepted limitation remains a limitation.
- Do not close while related work is changing the selected artifacts. Available session statuses are consistency signals, not authority; a stale `blocked` session status alone does not override the artifacts and applicable decision.
- Immediately before the first write, reread the complete plan, review/validation and acceptance record, and any backlog items to be changed. Reconcile changed evidence; stop if it remains inconsistent or active work continues.

If closure is not established, report the exact blocker and leave the workflow documents in place. Do not create an outcome note or archive unfinished work.

## 2. Preserve agreed follow-ups

Use `backlog` only for explicitly requested tasks, accepted non-blocking MINOR findings, and explicitly accepted validation limitations. Deduplicate and verify each write before an authorized source-finding removal. Preserve failed/blocked validation evidence. Do not manufacture new tasks, defer unresolved blockers to disguise completion, or implement follow-ups. Active backlog stays in `docs/backlog/`, outside the archive.

## 3. Select only this iteration's documents

Use one stable iteration ID: the selected plan's full filename stem, including its timestamp. For a previously archived iteration, reuse its existing archive ID and note; do not create another lifecycle.

Archive layout:

```text
docs/changes/<iteration-id>.md
docs/workflow/archive/<iteration-id>/
  plans/<original-plan-filename>.md
  reviews/<original-review-filename>.md
  brainstorm/<original-brainstorm-filename>.md  # when exclusively owned
```

- Select the exact plan and its linked review/validation artifact. Legacy plans under `docs/plans/completed/` can be selected explicitly; do not bulk-migrate them just because this skill runs.
- Include a linked brainstorm only when it is no longer needed by another active plan. Check active Markdown references under `docs/plans/`, excluding legacy `completed/`; if ownership is shared or uncertain, leave the brainstorm in place and link to it. Do not ask the user to classify routine unambiguous ownership.
- Do not archive application documentation, active backlog, unrelated plans/reviews, logs, transcripts, or arbitrary files. Existing loose documents are not permission for a repository-wide cleanup.
- Preserve original requirements, decisions, checkboxes, finding IDs, rounds, evidence, validation and acceptance. Change only paths needed to keep references correct. Do not add another `## Wrap-up` section to the plan: the outcome note replaces that closing summary, not the evidence.

## 4. Write one short outcome and archive automatically

Compose the outcome note as a temporary UTF-8 Markdown file outside the repository using the environment's scratch directory. Never store secrets. Include only:

- **Result:** what changed and the evidence-based technical verdict.
- **Decisions:** material rationale useful for future maintenance; omit an empty section.
- **Acceptance and limits:** actual decision, its source, remaining checks and accepted limitations. Identify still-unchecked required tasks with existing completion evidence or the explicitly accepted unfinished scope.
- **Follow-ups:** existing backlog links and at most useful unapproved suggestions, clearly marked as such.
- **Evidence:** links to the archived plan and review, plus the brainstorm (archived or shared).
- **Lessons:** up to three concrete observations only when useful; do not edit skills or shared rules.

Keep it concise; do not duplicate the plan, review rounds, raw logs, or add a separate retrospective. Links in this temporary file must be written as they should appear in `docs/changes/<iteration-id>.md`, not relative to the scratch directory.

Use the bundled helper relative to this installed skill's directory, not a guessed repository-level tools directory. This file and its `scripts/` directory must be installed together. Substitute actual paths in this command:

```text
python <wrap-up-skill-dir>/scripts/archive_iteration.py --root <repository> --id <iteration-id> --plan <plan-path> --review <review-path> --summary-file <temporary-note>
```

Add `--brainstorm <brainstorm-path>` for each exclusively owned selected brainstorm. First inspect this dry run: selected destinations, outcome note, and affected Markdown references must match the authorized iteration. Then run the same command with `--apply`; this mechanical archival is included in an authorized wrap-up and does not require another routine confirmation. The helper does not decide acceptance: the closure gate above remains mandatory.

The helper must refuse conflicting destinations and unsafe paths. It stores `.archive.json` integrity metadata inside each archive; when this iteration's link repairs affect an older archive or outcome, it verifies that complete older bundle before updating its affected integrity metadata. This is bookkeeping, not permission to rewrite historical findings or verdicts. Inspect the dry-run `limitations`: in a Git repository inbound references are scanned in tracked and non-ignored untracked Markdown only; ignored files, submodules, and symlink directories are not traversed. Outside Git, dependency/generated directories are also excluded. Do not claim those excluded references were checked. Single-line inline links and reference definitions (including blockquotes) are supported; relevant unsupported or ambiguous links cause a safe refusal. Fenced examples are preserved rather than rewritten.

Backtick and tilde fenced blocks, including those inside nested blockquotes, are excluded from both link validation and rewriting. Multiline link examples inside these blocks remain unchanged and do not block archival; live multiline links outside them still cause a safe refusal.

If Python is unavailable, the helper reports unsupported links, or a write/verification fails, preserve the source and report the exact blocker; do not substitute unverified ad-hoc deletion. Do not auto-install dependencies. Do not claim all-or-nothing crash recovery beyond the helper's documented guarantees.

## 5. Verify and stop

Read the resulting outcome and archived evidence. Verify the plan reference, technical/acceptance verdicts, backlog links, and affected document links. A successful process exit alone is not proof of semantically correct closure. Do not treat an archived location as proof of completion.

A repeated invocation reuses the same files. If they already match, report no changes. Do not overwrite conflicting summaries or silently incorporate new work into a closed iteration; a changed outcome requires an explicitly scoped correction, not another archive ID. Do not reopen or revalidate closed work merely to tidy it.

Report the outcome note, archive directory, technical validation status, acceptance status, backlog paths, and any retained shared brainstorm. Detailed evidence remains available for `skill-improvement`; new work should read the short outcome first and open archived details only when relevant.

Only write the selected outcome note, selected workflow-document archive, agreed backlog handoffs, directly affected Markdown references, and integrity metadata for verified archive bundles affected by those repairs. No product code/configuration edits, application test runs, new stages, branch changes, stage/commit/push/merge, bulk legacy cleanup, or deletion of historical evidence. Archival removes only the selected originals after verified preservation; it does not authorize permanent deletion of the archive.
