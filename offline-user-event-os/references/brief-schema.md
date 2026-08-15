# Brief data contract

Prepare one UTF-8 JSON object. The generator is intentionally strict so that missing lifecycle data is visible instead of silently invented.

## Top-level fields

| Field | Type | Rule |
|---|---|---|
| `project` | string | Project or workspace name |
| `event_name` | string | Human-facing event title |
| `event_status` | string | `planned`, `live`, `completed`, or `cancelled` |
| `objective` | string | Observable event objective |
| `date` | string | ISO date `YYYY-MM-DD` |
| `location` | string | Venue or explicit `待确认` |
| `owner` | string | Accountable event owner or role |
| `audience` | string | Primary participant group |
| `expected_attendance` | integer | Planned attendance, greater than zero |
| `planned_budget_cny` | number | Planned cost, zero or greater |
| `planned_revenue_cny` | number | Planned income, zero or greater |
| `evidence_status` | string | One of the evidence statuses below |
| `before` | object | Activity-before workstreams |
| `during` | object | Live operations workstreams |
| `after` | object | Post-event review and archive data |
| `guardrails` | array | At least one privacy, safety, approval, or publication boundary |

## Evidence statuses

Use only `PLANNED`, `ACTUAL`, `SIMULATED`, or `TO_VALIDATE`.

## `before`

All six fields are required arrays:

- `people`: `name`, `role`, `owner`, `channel`, `status`, `due`, `note`
- `materials`: `item`, `quantity`, `supplier`, `status`, `due`, `contingency`
- `rundown`: `time`, `task`, `owner`, `dependency`, `status`, `note`
- `user_arrangements`: `item`, `owner`, `status`, `due`, `note`
- `budget_items`: `item`, `planned_cny`, `owner`, `status`, `note`
- `fee_plan`: `item`, `unit_price_cny`, `expected_quantity`, `status`, `note`

Each array may be empty when not applicable, but no field may be omitted.

## `during`

All three fields are required arrays:

- `contacts`: `name`, `role`, `channel`, `contact`, `backup`, `note`
- `live_tasks`: `time`, `task`, `owner`, `status`, `note`
- `incidents`: `time`, `severity`, `issue`, `action`, `owner`, `follow_up`, `status`

Use redacted or fictional contact details in public examples.

## `after`

Required scalar fields:

- `registered`
- `checked_in`
- `satisfaction_5`
- `actual_revenue_cny`
- `actual_cost_cny`
- `metrics_evidence_status`
- `suggestion`
- `retrospective`
- `archive_state`: `not_ready`, `ready`, or `archived`

Required arrays:

- `cases`: `type`, `summary`, `owner`, `resolution`, `due`, `status`
- `suppliers`: `name`, `purchase_type`, `current_node`, `nodes`, `owner`, `status`, `note`
- `ugc`: `channel`, `content_type`, `count`, `likes`, `saves`, `reward`, `authorization`, `reuse_state`
- `feedback`: `source`, `summary`, `owner`, `action`, `status`, `proof`

For each supplier, `nodes` is a non-empty array selected for that supplier. Typical nodes include `合同`, `定金`, `验收`, `发票`, `付款`, `退还押金`, and `到账确认`.

## Validation rules

- `checked_in` cannot exceed `registered`.
- `satisfaction_5` must be between 0 and 5.
- Planned and actual money values cannot be negative.
- Count, like, and save values cannot be negative.
- If `event_status` is not `completed`, post-event numbers may remain zero and `metrics_evidence_status` should normally remain `TO_VALIDATE`, `PLANNED`, or `SIMULATED`.
- The generator calculates check-in rate and actual ROI. It returns `N/A` when the denominator is zero.
