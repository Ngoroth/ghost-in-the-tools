---
name: wrap-up
description: "Use to close an iteration: summarize lessons, capture agreed backlog work, and archive its plan."
license: MIT
compatibility: "Codex; requires repository file access and the backlog skill."
metadata:
  author: "Daniil(Ngoroth) and Bes"
  version: "1.1.1"
---

# Wrap up

Close one iteration with minimal paperwork. Use the conversation's language.

1. **Read and confirm the prior stages are settled.** Locate the repository and selected plan; read its review/validation artifact and supplied user decision. If the target is ambiguous, ask. Use existing evidence; do not rerun tests or review. Never invent acceptance or turn FAIL/BLOCKED into PASS.
   - When the environment exposes session or task statuses and the related review or validation work ran in identifiable separate sessions, use their explicitly published statuses as a consistency signal. If both stages publish statuses, require `completed`; an explicit `active` or `blocked` status stops wrap-up. A missing, idle, unknown, or unsupported status does not block closure by itself: do not require a particular terminal, session manager, or orchestration system, and keep repository artifacts authoritative.
   - Immediately before the first write, reread the complete selected plan, review/validation artifact, human-acceptance record, and any backlog items that will be reused or changed. If they changed since the initial read, reconcile the wrap-up against the new state before writing. If they continue changing or conflict, stop instead of recording a stale result.
2. **Capture agreed follow-ups.** Follow the existing `backlog` skill for explicitly requested tasks, accepted MINOR findings, and explicitly accepted validation limitations: deduplicate, write a standalone item, and verify it. Remove a source finding only for the backlog skill's authorized MINOR handoff; preserve failed or blocked validation evidence unchanged. Never hide required unfinished work in backlog outside that skill's explicit accepted-limitation rules. Mention unapproved ideas in the summary instead of creating tasks for them. Do not implement follow-ups.
3. **Write a short closing section in the plan.** Add or update one `## Wrap-up`, not a separate report:
   - **Result:** what was achieved and the existing technical verdict/evidence.
   - **Acceptance and limits:** the actual user decision, or “not supplied”; remaining checks and accepted limitations.
   - **Follow-ups:** backlog paths and any useful unapproved suggestion.
   - **Lessons:** up to three concrete observations → what to do differently next time. Omit empty or generic lessons; do not edit shared instructions or skills.
   Preserve original requirements, checkboxes, review findings, revisions, and verdicts except for the backlog skill's authorized handoff. This closing section is not a plan redesign.
4. **Archive only a closed iteration.** Move the plan to `docs/plans/completed/<same-filename>` only when existing evidence establishes completion with no unresolved required work, or the user explicitly accepted closure of this iteration with its stated limits. When present, `acceptance_status: accepted` or `accepted_with_limitations` is the structured record of that decision; `not_recorded` or `rejected` does not authorize closure over failed or blocked validation. An invocation alone is not acceptance. Never change the technical `validation_status` to justify closure. Otherwise keep the plan where it is and report what prevents closure. Never overwrite a conflicting destination. Repair affected document links, including relative links inside the moved plan and its review's plan reference; do not rewrite code or configuration. Keep the review artifact as evidence; delete it only on a separate explicit request.
5. **Verify and stop.** Check the resulting files and links. A repeated invocation updates the same closing section and reuses existing backlog items; an already archived plan stays put. If any required write or verification fails, preserve the source and report partial progress, not successful closure. Report the plan's final path, technical validation status, human acceptance status, backlog paths, and a short outcome.

Only edit the selected plan, its archival location, accepted backlog handoffs, and directly affected documentation links. No code changes, test runs, new workflow stages, branch changes, stage/commit/push/merge, or automatic cleanup. Never store secrets.
