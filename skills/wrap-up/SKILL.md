---
name: wrap-up
description: "Use to close an iteration: summarize lessons, capture agreed backlog work, and archive its plan."
license: MIT
compatibility: "Codex; requires repository file access and the backlog skill."
metadata:
  author: "Daniil(Ngoroth) and Bes"
  version: "2.0.0"
---

# Wrap up

Close one iteration with minimal paperwork. Use the conversation's language.

Required decisions belong to the responsible party identified by the user's chosen process or supplied task context, whether a person or automated participant. Executing this skill does not confer acceptance authority; report missing responsibility or decisions and reuse applicable decisions already supplied.

1. **Read and confirm the prior stages are settled.** Locate the repository and selected plan; read its review/validation artifact and supplied acceptance decision. If the target is ambiguous, ask. Use existing evidence; do not rerun tests or review. Never invent acceptance or turn FAIL/BLOCKED into PASS.
   - Use available session statuses only as consistency signals. Do not close while related work is still changing the selected artifacts. A stale `blocked` status alone does not prevent closure when the artifacts and explicit acceptance decision establish it. Repository artifacts remain authoritative; no session-manager integration is required.
   - Immediately before the first write, reread the complete selected plan, review/validation artifact, acceptance record, and any backlog items that will be reused or changed. If they changed since the initial read, reconcile the wrap-up against the new state before writing. If they continue changing or conflict, stop instead of recording a stale result.
2. **Capture agreed follow-ups.** Follow the existing `backlog` skill for explicitly requested tasks, accepted MINOR findings, and explicitly accepted validation limitations: deduplicate, write a standalone item, and verify it. Remove a source finding only for the backlog skill's authorized MINOR handoff; preserve failed or blocked validation evidence unchanged. Never hide required unfinished work in backlog outside that skill's explicit accepted-limitation rules. Mention unapproved ideas in the summary instead of creating tasks for them. Do not implement follow-ups.
3. **Write a short closing section in the plan.** Add or update one `## Wrap-up`, not a separate report:
   - **Result:** what was achieved and the existing technical verdict/evidence.
   - **Acceptance and limits:** the actual decision from the responsible party, or “not supplied”; remaining checks and accepted limitations.
   - **Follow-ups:** backlog paths and any useful unapproved suggestion.
   - **Lessons:** up to three concrete observations → what to do differently next time. Omit empty or generic lessons; do not edit shared instructions or skills.
   Preserve original requirements, checkboxes, review findings, revisions, and verdicts except for the backlog skill's authorized handoff. This closing section is not a plan redesign.
4. **Archive only a closed iteration.** Never archive when `acceptance_status` is `rejected` or the supplied acceptance decision rejects closure. Otherwise move the plan to `docs/plans/completed/<same-filename>` only when existing evidence establishes completion with no unresolved required work, or explicit acceptance by the responsible party covers every current failed or blocked criterion and its limitation. An invocation alone is not acceptance. Never change the technical `validation_status` to justify closure. Otherwise keep the plan where it is and report what prevents closure. Never overwrite a conflicting destination. Repair affected document links, including relative links inside the moved plan and its review's plan reference; do not rewrite code or configuration. Keep the review artifact as evidence; delete it only on a separate explicit request authorized by the responsible party.
5. **Verify and stop.** Check the resulting files and links. A repeated invocation updates the same closing section and reuses existing backlog items; an already archived plan stays put. If any required write or verification fails, preserve the source and report partial progress, not successful closure. Report the plan's final path, technical validation status, acceptance status, backlog paths, and a short outcome.

Only edit the selected plan, its archival location, accepted backlog handoffs, and directly affected documentation links. No code changes, test runs, new workflow stages, branch changes, stage/commit/push/merge, or automatic cleanup. Never store secrets.
