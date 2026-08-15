---
name: offline-user-event-os
description: Turn an offline event brief or existing event plan into a lifecycle-based operations kit covering activity-before coordination, live operations, post-event data and actual ROI, cases, supplier payment nodes, UGC, feedback, lessons, and archive readiness. Use when planning, importing, executing, reviewing, or standardizing recurring brand, community, customer, employee, or user events, especially when outputs must separate plans, actuals, simulations, and items still to validate.
---

# Offline User Event OS

Turn one event brief into a practical operating system. Keep planning, on-site execution, post-event review, and reusable lessons connected without forcing users to re-enter an existing plan.

## Workflow

1. Read `references/brief-schema.md` before preparing the brief.
2. Reuse an existing plan when available. Extract useful fields from approved documents, spreadsheets, or notes; ask only for missing information.
3. Label important figures and claims with one evidence status:
   - `PLANNED`: a future target, estimate, or approved plan.
   - `ACTUAL`: a result supported by current-event evidence.
   - `SIMULATED`: demonstration data used to test a workflow or interface.
   - `TO_VALIDATE`: an assumption or incomplete item that still needs confirmation.
4. Save the normalized brief as UTF-8 JSON. Start from `assets/brief.example.json` when useful.
5. Generate the operations kit:

```powershell
python scripts/generate_event_kit.py --brief path/to/brief.json --output path/to/output
```

The generator refuses to overwrite an existing kit. Use `--force` only after resolving the exact output directory and reviewing the generated files that will be replaced.

6. Review and edit the generated files. The kit is a working structure, not an automatic authorization to contact people, spend money, publish content, or make safety decisions.
7. Run the gates in `references/quality-gates.md` before execution, reporting, archival, or publication.

## Lifecycle outputs

### Activity before

- Event overview, objective, audience, date, location, owner, and current status.
- People coordination with owner, role, contact channel, confirmation state, and due date.
- Materials with quantity, supplier, delivery state, deadline, and contingency.
- Run of show with time, task, owner, dependency, completion state, and notes.
- User arrangements, planned budget, activity fees, and planned revenue.

### Activity during

- Fast-access contact list for core staff and suppliers.
- Current run-of-show node, live task list, incident log, owner, severity, response, and follow-up.
- Manual additions and corrections must remain possible even when the plan was imported or AI-generated.

### Activity after

- Attendance, check-in rate, satisfaction, actual revenue, actual cost, and actual ROI.
- Cases and complaints with owner, resolution, deadline, and closure proof.
- Supplier-specific payment nodes such as contract, deposit, acceptance, invoice, payment, refund, and receipt confirmation.
- UGC by channel and content type, including count, likes, saves, reward, authorization, and reuse state.
- Feedback closure, suggestions, retrospective notes, reusable lessons, and archive readiness.

## Operating rules

- Keep planned amounts separate from actual amounts. Overall reports must use actual revenue and actual cost when calculating actual ROI.
- Do not infer a result from a target. Convert `PLANNED` or `TO_VALIDATE` to `ACTUAL` only after evidence review.
- Preserve editable source records. Importing a plan must prefill the workflow, not lock it.
- Keep cancelled events distinguishable from completed archived events.
- Archive a completed event only after required data, payments, feedback, and actual ROI have been reviewed.
- Minimize personal data. Do not publish phone numbers, personal email, attendee lists, faces, IDs, raw complaints, API keys, or confidential supplier data.
- Require human approval for spending, outreach, contracts, refunds, publication, participant-data processing, and on-site safety decisions.
- Adapt venue, legal, accessibility, privacy, and emergency requirements to the real event and jurisdiction.

## Adaptation guidance

- For a portfolio case, use fictional or redacted example data and keep `SIMULATED` labels visible.
- For a live event, replace demonstration rows with approved source records and record actual changes as they happen.
- For recurring events, reuse templates and lessons while preserving event-specific people, supplier, cost, and risk data.
- For AI-assisted planning, treat generated content as a draft. Keep human review before it enters the execution workflow.
