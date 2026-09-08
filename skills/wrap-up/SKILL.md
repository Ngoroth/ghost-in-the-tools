---
name: wrap-up
description: "Use to close an iteration: summarize lessons, capture agreed backlog work, and archive its plan."
license: MIT
compatibility: "Codex; requires repository file access and the backlog skill."
metadata:
  author: "Daniil(Ngoroth) and Bes"
  version: "1.0.0"
---

# Wrap up

Close one iteration with minimal paperwork. Use the conversation's language.

1. **Read.** Locate the repository and selected plan; read its review/validation artifact and supplied user decision. If the target is ambiguous, ask. Use existing evidence; do not rerun tests or review. Never invent acceptance or turn FAIL/BLOCKED into PASS.
2. **Capture agreed follow-ups.** Follow the existing `backlog` skill for explicitly requested tasks and accepted MINOR findings: deduplicate, write a standalone item, verify it, then remove only the transferred finding. Never hide required unfinished work in backlog. Mention unapproved ideas in the summary instead of creating tasks for them. Do not implement follow-ups.
3. **Write a short closing section in the plan.** Add or update one `## Wrap-up`, not a separate report:
   - **Result:** what was achieved and the existing technical verdict/evidence.
   - **Acceptance and limits:** the actual user decision, or “not supplied”; remaining checks and accepted limitations.
   - **Follow-ups:** backlog paths and any useful unapproved suggestion.
   - **Lessons:** up to three concrete observations → what to do differently next time. Omit empty or generic lessons; do not edit shared instructions or skills.
   Preserve original requirements, checkboxes, review findings, revisions, and verdicts except for the backlog skill's authorized handoff. This closing section is not a plan redesign.
4. **Archive only a closed iteration.** Move the plan to `docs/plans/completed/<same-filename>` only when existing evidence establishes completion with no unresolved required work, or the user explicitly accepted closure of this iteration with its stated limits. An invocation alone is not acceptance. Otherwise keep the plan where it is and report what prevents closure. Never overwrite a conflicting destination. Repair affected document links, including relative links inside the moved plan and its review's plan reference; do not rewrite code or configuration. Keep the review artifact as evidence; delete it only on a separate explicit request.
5. **Verify and stop.** Check the resulting files and links. A repeated invocation updates the same closing section and reuses existing backlog items; an already archived plan stays put. If any required write or verification fails, preserve the source and report partial progress, not successful closure. Report the plan's final path, backlog paths, and a short outcome.

Only edit the selected plan, its archival location, accepted backlog handoffs, and directly affected documentation links. No code changes, test runs, new workflow stages, branch changes, stage/commit/push/merge, or automatic cleanup. Never store secrets.
