---
name: backlog
description: "Use to capture, list, inspect, or close deferred repository work in docs/backlog/, with one Markdown file per task."
license: MIT
compatibility: "Agent Skills-compatible coding agents; requires access to a Git repository and permission to edit docs/backlog/ plus remove accepted MINOR findings from their source review artifacts."
metadata:
  author: "Daniil(Ngoroth) and Bes"
  version: "1.3.0"
---

# Backlog

Maintain a small repository-local backlog under `docs/backlog/`. Each file represents exactly one real task that is worth remembering but is not part of the work being completed now.

## Rules

- Store one task per Markdown file: `docs/backlog/<task-slug>.md`.
- A backlog item never gates the current plan or implementation.
- Do not use backlog to hide a missing acceptance criterion, unresolved `CRITICAL`/`MAJOR` review finding, or work required for the current task to be complete. The only exception is the explicit accepted-validation-limitation handoff below, which preserves the failed or blocked verdict rather than disguising it.
- Do not implement an item merely because it was captured, listed, or inspected. Implementation requires a separate explicit request.
- Treat the repository as read-only except for files under `docs/backlog/` and the narrow review-handoff edit described below.
- Do not modify source, tests, configuration, brainstorms, or substantive plan text. During an accepted review handoff, modify only the source plan-review annotation or code-review finding being transferred and, when applicable, its review status. Do not commit or push.
- Never store secrets or credentials. Replace encountered values with `[REDACTED]`.

## Locate the repository

Find the repository root, preferably with `git rev-parse --show-toplevel`. If it cannot be identified, ask for its path and do not create files elsewhere.

Use paths relative to that root. Do not switch branches, create worktrees, or move the user's checkout.

## Add an item

When the user explicitly asks to add deferred work, or explicitly accepts a backlog candidate from review:

1. Confirm that the item is real, actionable, and outside the current task's required scope.
2. If the request contains multiple independent tasks, create one file for each. Do not bundle them.
3. Read existing `docs/backlog/*.md` files before writing. Compare the actual claimed work, not only filenames or locations.
4. If the same task already exists, report its path. Update it only when the new information materially improves its accuracy; never create a duplicate.
5. Create `docs/backlog/` only when at least one item will be written.
6. Use a short lowercase ASCII kebab-case slug that names the task, not merely the affected file.
7. If an unrelated file already uses the slug, append `-2`, `-3`, and so on rather than overwriting it.
8. Use the user's local date when available.
9. Write enough context for a future session to understand and verify the task without access to the current conversation.

Use this format:

```markdown
---
added: YYYY-MM-DD
source: <repository-relative review artifact and finding ID, issue, or user request; omit if unavailable>
where: <repository-relative path[:line] or symbol; omit if not anchored>
---
# <Concrete task title>

<What is wrong or worth doing, its observable impact, and the evidence that it is real.>

## Why deferred
<Why this is not required or appropriate in the current work.>

## Done when
- [ ] <Observable completion criterion.>
- [ ] <Relevant verification command or result, when known.>
```

Omit optional frontmatter fields rather than inventing values. Preserve exact identifiers and commands. Do not paste conversation transcripts.

## Review findings

A `MINOR` finding marked `backlog_candidate: true` may become a backlog item only when the user explicitly accepts it. Supported sources are:

- a `PR-NNN` `PLAN-REVIEW` block in an approved plan;
- a `CR-NNN` finding section in an approved code-review artifact under `docs/reviews/`.

When filing one:

- require the source review to be complete with `review_status: approved-with-notes` or `approved`, and require no open `CRITICAL` or `MAJOR` findings;
- for a plan review, also require `reviewed_revision` to equal `plan_revision`;
- copy the finding's substance, not its review markup;
- record the source artifact path and finding ID in `source`;
- preserve evidence, impact, and `close_when` as backlog context and `Done when` criteria;
- create one backlog file per accepted finding;
- never file current-scope `CRITICAL` or `MAJOR` findings;
- write or update the backlog item first and verify that the complete deferred task is preserved there;
- only after that write succeeds, remove the finding completely from its source: the entire `PLAN-REVIEW` comment block for `PR-NNN`, or the selected `## CR-NNN` section only for `CR-NNN`. Its boundary is the earliest subsequent same-or-higher-level Markdown heading (whether a finding or another section), `<!-- GOAL-VALIDATION:START -->`, or end of file. Preserve the boundary and all following content, especially goal validation and human acceptance. If the section boundary is ambiguous, stop without deleting;
- leave all surrounding plan content and unrelated review findings unchanged; verify that following validation/acceptance sections survive the transfer unchanged;
- if the accepted finding was already represented by an existing backlog item, make sure that item preserves enough context to stand alone before removing the source finding;
- if any backlog write or verification fails, leave the source finding intact and report the blocker. Do not delete or replace a conflicting existing file/directory to force a write; preserve it and request the missing decision.
- after removing the finding, change `review_status: approved-with-notes` to `approved` only when no other open `MINOR` findings remain; otherwise keep `approved-with-notes`;
- for a plan review, do not increment `plan_revision` or change `reviewed_revision`, because removing a transferred annotation does not alter reviewed plan content;
- for a code review, do not change `review_round`, because removing a transferred review finding does not alter implementation content.

The backlog file is the sole durable record after a successful transfer. Do not leave a stub, tombstone, resolved block, or pointer in the source review artifact: that would retain the context clutter this handoff is intended to remove.

## Accepted validation limitations

A required acceptance criterion that is `FAIL` or `BLOCKED` may be captured as future backlog work only after the user has explicitly accepted closure with that limitation. This is a deferral record, not a review-finding transfer.

Require all of the following:

- the source `docs/reviews/*.md` artifact has `acceptance_status: accepted_with_limitations`;
- its `## Human acceptance` section explicitly identifies the affected criterion and accepts closure despite that result;
- the user explicitly asks to defer or backlog the remediation;
- no unresolved `CRITICAL` or `MAJOR` code-review finding is being disguised as the validation limitation.

Create or reuse a standalone backlog item using the ordinary add-item rules. Record the source review path, criterion ID, technical `validation_status`, decisive failure or blocker evidence, accepted limitation, deferral reason, and observable completion criteria. Do not remove or rewrite the criterion in the goal-validation block, change `validation_status`, or imply that acceptance made it pass. The validation artifact remains the durable evidence of the result; the backlog item records only the future remediation. If any prerequisite is missing or ambiguous, leave the validation artifact unchanged and ask for the missing decision.

## List items

When asked to show the backlog:

1. Read every `docs/backlog/*.md` file in full.
2. If the directory is absent or contains no item files, report that the backlog is empty; do not create an empty directory.
3. For an item with `where`, verify that the referenced path or symbol still exists and still supports the claim. Mark stale locations rather than silently repairing or discarding the item.
4. Report every item with its title, path, added date, location when present, and a one-sentence summary.
5. Sort oldest first unless the user requests another order.

Do not silently triage, rewrite, implement, or delete items while listing them.

## Inspect one item

When given a slug or path, read that item and verify its current repository context. Report:

- what the task requires;
- whether its evidence and location remain current;
- its observable completion criteria;
- known dependencies or blockers.

If no exact item matches, say so and list the available slugs. Do not guess the nearest filename.

## Close or drop an item

Delete an item only when the user explicitly requests one of these outcomes:

- **completed:** verify the recorded `Done when` criteria against the repository where possible, then delete the file;
- **dropped:** delete it because the user has decided not to keep the task.

If completion cannot be verified, report what is missing and leave the file intact. Deleting the backlog file does not authorize a commit or push.

## Report

After any write or deletion, report the exact repository-relative paths changed and the reason for each. For a review handoff, report both the backlog path and the source review artifact whose finding was removed. Do not claim an item was saved or removed until both filesystem operations succeed.
