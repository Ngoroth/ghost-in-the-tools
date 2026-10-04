---
name: workflow-guide
description: "Use to explain, select, or sequence the Ghost in the Tools skills, resume their workflow from existing artifacts, or prepare context for the next session."
license: MIT
metadata:
  author: "Daniil(Ngoroth) and Bes"
  version: "2.0.0"
---

# Workflow Guide

Guide use of the Ghost in the Tools skill set. Identify the appropriate skill, its inputs, the evidence needed to proceed, and where its responsibility ends. This guide depends only on the companion skills and their repository artifacts; it requires no particular agent, session manager, orchestration framework, or communication tool.

## Use the guide

For an explanation, describe only the relevant part of the workflow. For a concrete next step, inspect the user's request, existing decisions, and selected artifacts before recommending a skill. Do not infer the active task from the newest filename. Ask for the target when several plans or reviews could apply.

Read the selected skill's full `SKILL.md` before using it. The links below locate companion skills in this set; if installation exposes them elsewhere, resolve them through the available skill catalog. If a required skill is unavailable, report which one is missing rather than inventing its procedure. Each companion skill owns its detailed rules, formats, and write boundaries; this guide does not override them.

The guide itself does not edit workflow artifacts or start other sessions. When execution is requested, apply the selected skill within the user's authorized scope. An explanation or next-step recommendation does not authorize execution of the whole sequence. Preserve decisions and authorization already supplied; ask only for a missing decision that affects the next action.

## Decision responsibility

Every required decision has a responsible party, determined by the user's chosen process or the supplied task context. Skills do not prescribe whether that party is a person or an automated participant; executing a skill does not itself confer decision authority.

Use decisions and authorization already supplied within their stated scope. Do not request the same decision again unless new evidence invalidates it or changes its scope.

When a required decision or its responsible party is unknown, report what is missing rather than inventing approval. No participant registry or particular coordination mechanism is required.

Decision authority does not replace technical evidence, reviewer independence, or permissions imposed by the execution environment.

## Select a skill

| Need | Skill | Input and durable result |
| --- | --- | --- |
| Explore an idea or settle connected design decisions | [brainstorm](../brainstorm/SKILL.md) | Repository context and user intent → approved design or explicitly unfinished record in `docs/brainstorm/`. |
| Turn a settled approach into executable tasks | [planning](../planning/SKILL.md) | Settled scope, decisions, and optional brainstorm → one plan with observable completion criteria in `docs/plans/`. |
| Independently check a plan before implementation | [plan-review](../plan-review/SKILL.md) | Explicit plan path → review metadata and inline `PLAN-REVIEW` findings in that plan. |
| Independently check implemented changes | [code-review](../code-review/SKILL.md) | Explicit approved plan path and unambiguous Git scope → one continuing evidence artifact in `docs/reviews/`. |
| Demonstrate that the goal and required criteria are met | [goal-validation](../goal-validation/SKILL.md) | Explicit code-review artifact path → technical validation and separately recorded acceptance in that artifact. |
| Capture, list, inspect, or close deferred work | [backlog](../backlog/SKILL.md) | Requested operation and task or accepted finding → standalone items in `docs/backlog/`. Listing and inspection do not authorize implementation. |
| Close an iteration and preserve its evidence | [wrap-up](../wrap-up/SKILL.md) | Selected plan, review/validation evidence, and supplied acceptance decision → closing section, agreed follow-ups, and archival when closure conditions hold. |
| Explain the current session's result | [session-work-summary](../session-work-summary/SKILL.md) | Available conversation and tool evidence → concise chat summary, without new checks or file changes. |

Implementation and fixes have no dedicated skill in this set. They are ordinary development work under the user's request and the approved plan; neither a reviewer nor this guide takes ownership of them implicitly.

## Sequence and transitions

The full iteration follows this shape:

```text
brainstorm → planning → independent plan-review → implementation authorization
→ implementation → independent code-review → goal-validation
→ acceptance → wrap-up
```

Enter where the request and existing evidence place the task. A settled design need not be brainstormed again. A summary or backlog operation can stand alone. Do not impose the full iteration on every request, or skip a selected skill's prerequisites because an earlier stage was omitted.

- **Design to plan:** material decisions must be settled before planning writes a plan. Return connected design questions to brainstorm; do not hide them in implementation tasks.
- **Plan to implementation:** plan review must approve the current revision (`approved` or `approved-with-notes`, with `reviewed_revision` equal to `plan_revision`). Technical approval and implementation authorization from the responsible party are separate; authorization may already have been supplied for this scope. A substantive revision invalidates the previous review approval under the planning rules.
- **Review and fixes:** `needs-revision` routes to the plan author; `needs-fixes` routes to the implementer. They may mark findings `addressed`; only the independent reviewer can mark them `resolved`. Both `open` and `addressed` findings remain unresolved. Continue the same artifacts, finding IDs, and bounded review rounds. `MINOR` findings do not require another round. At `needs-decision`, surface the exact unresolved choice to the responsible party; do not reset counters or create a new artifact to bypass the limit.
- **Code review to validation:** require `approved` or `approved-with-notes` and no unresolved `CRITICAL` or `MAJOR` findings. Missing external evidence alone is incomplete verification, not an implementation defect; validation determines its effect on acceptance criteria.
- **Validation to acceptance:** `PASS`, `FAIL`, and `BLOCKED` describe evidence for each criterion. The aggregate technical status (`passed`, `failed`, or `blocked`) is separate from `acceptance_status` (`not_recorded`, `accepted`, `accepted_with_limitations`, or `rejected`). Acceptance cannot turn an unexecuted or failing check into a pass. New or worsened limitations require a decision covering them. Report failures or missing evidence so the responsible party can decide the next step; validation does not launch fixes.
- **Acceptance to closure:** use wrap-up's closure rules and reread the authoritative artifacts before writing. Rejection prevents archival; failed or blocked criteria require explicit acceptance covering every current limitation. Invoking wrap-up is not itself acceptance. Keep review and validation evidence when archiving the plan.

Publication is outside this sequence: none of these skills automatically stages, commits, pushes, merges, deploys, or publishes.

## Independent sessions and shared artifacts

Plan review requires a session that did not author or substantively revise the plan. Code review requires a fresh session that did not implement the change. Goal validation prefers a fresh session, but its essential requirement is direct verification of evidence. Changing the role label in the authoring session does not establish review independence.

Session creation, scheduling, messages, and transport belong to the surrounding environment. When preparing work for another session, provide only the relevant context:

- requested stage and companion skill;
- repository location and explicit repository-relative artifact paths;
- goal, settled constraints, applicable decisions or authorization, and the responsible party for any pending decision;
- for code review, the known base ref or starting SHA and scope boundaries;
- current revision, review round, unresolved finding IDs, and exact missing prerequisites when applicable;
- permitted writes and expected result or stopping condition, as defined by the selected skill.

The receiving session reads the actual artifacts and verifies claims; a handoff summary is not replacement evidence. A replacement reviewer continues the existing lifecycle. Avoid concurrent edits to the same plan or review artifact: finish the current writer's work before a dependent stage consumes it. Available session statuses may signal a conflict, but do not substitute for repository evidence or user decisions. No additional coordinator log or state format is required.

## Deferred work and reporting

Backlog is a side operation, not a way to bypass completion criteria. An explicitly accepted, non-blocking `MINOR` candidate can be transferred after review approval: backlog writes and verifies the item before removing the source finding. Required `FAIL` or `BLOCKED` remediation may be recorded only through the accepted-validation-limitation rules, preserving its original validation evidence and verdict.

When advising what comes next, report the current stage and supporting artifact, the recommended skill or ordinary development action, and any specific missing input or decision. Keep recommendations distinct from actions already performed. Use session-work-summary for a chat recap; use wrap-up only for the requested closure work.
