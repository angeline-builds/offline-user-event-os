#!/usr/bin/env python3
"""Generate a deterministic lifecycle-based offline event operations kit."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path
from typing import Any


EVIDENCE_STATUSES = {"PLANNED", "ACTUAL", "SIMULATED", "TO_VALIDATE"}
EVENT_STATUSES = {"planned", "live", "completed", "cancelled"}
ARCHIVE_STATES = {"not_ready", "ready", "archived"}

OUTPUT_NAMES = (
    "00-event-overview.md",
    "01-before-people.csv",
    "02-before-materials.csv",
    "03-before-rundown.csv",
    "04-before-budget-and-fees.csv",
    "05-during-contacts.csv",
    "06-during-operations.md",
    "07-after-data-and-roi.md",
    "08-after-suppliers.csv",
    "09-after-ugc.csv",
    "10-after-cases-and-feedback.md",
    "11-retrospective-and-archive.md",
    "data.json",
)


def require_text(data: dict[str, Any], key: str, context: str = "brief") -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context}.{key} must be a non-empty string")
    return value.strip()


def require_number(data: dict[str, Any], key: str, context: str, minimum: float = 0) -> float:
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < minimum:
        raise ValueError(f"{context}.{key} must be a number >= {minimum}")
    return float(value)


def require_integer(data: dict[str, Any], key: str, context: str, minimum: int = 0) -> int:
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{context}.{key} must be an integer >= {minimum}")
    return value


def require_object(data: dict[str, Any], key: str, context: str = "brief") -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{context}.{key} must be an object")
    return value


def require_list(data: dict[str, Any], key: str, context: str, allow_empty: bool = True) -> list[Any]:
    value = data.get(key)
    if not isinstance(value, list) or (not allow_empty and not value):
        qualifier = "a list" if allow_empty else "a non-empty list"
        raise ValueError(f"{context}.{key} must be {qualifier}")
    return value


def validate_rows(rows: list[Any], fields: tuple[str, ...], context: str) -> None:
    for index, row in enumerate(rows):
        row_context = f"{context}[{index}]"
        if not isinstance(row, dict):
            raise ValueError(f"{row_context} must be an object")
        for field in fields:
            if field not in row:
                raise ValueError(f"{row_context}.{field} is required")
            if isinstance(row[field], str) and not row[field].strip():
                raise ValueError(f"{row_context}.{field} must not be blank")


def validate_brief(data: dict[str, Any]) -> None:
    for key in ("project", "event_name", "objective", "date", "location", "owner", "audience"):
        require_text(data, key)

    status = require_text(data, "event_status")
    if status not in EVENT_STATUSES:
        raise ValueError(f"event_status must be one of {sorted(EVENT_STATUSES)}")
    evidence_status = require_text(data, "evidence_status")
    if evidence_status not in EVIDENCE_STATUSES:
        raise ValueError(f"evidence_status must be one of {sorted(EVIDENCE_STATUSES)}")
    try:
        date.fromisoformat(data["date"])
    except ValueError as exc:
        raise ValueError("date must use YYYY-MM-DD") from exc

    require_integer(data, "expected_attendance", "brief", 1)
    require_number(data, "planned_budget_cny", "brief")
    require_number(data, "planned_revenue_cny", "brief")
    guardrails = require_list(data, "guardrails", "brief", allow_empty=False)
    if not all(isinstance(item, str) and item.strip() for item in guardrails):
        raise ValueError("brief.guardrails must contain non-empty strings")

    before = require_object(data, "before")
    before_specs = {
        "people": ("name", "role", "owner", "channel", "status", "due", "note"),
        "materials": ("item", "quantity", "supplier", "status", "due", "contingency"),
        "rundown": ("time", "task", "owner", "dependency", "status", "note"),
        "user_arrangements": ("item", "owner", "status", "due", "note"),
        "budget_items": ("item", "planned_cny", "owner", "status", "note"),
        "fee_plan": ("item", "unit_price_cny", "expected_quantity", "status", "note"),
    }
    for key, fields in before_specs.items():
        rows = require_list(before, key, "brief.before")
        validate_rows(rows, fields, f"brief.before.{key}")
    for index, item in enumerate(before["budget_items"]):
        require_number(item, "planned_cny", f"brief.before.budget_items[{index}]")
    for index, item in enumerate(before["fee_plan"]):
        require_number(item, "unit_price_cny", f"brief.before.fee_plan[{index}]")
        require_integer(item, "expected_quantity", f"brief.before.fee_plan[{index}]")

    during = require_object(data, "during")
    during_specs = {
        "contacts": ("name", "role", "channel", "contact", "backup", "note"),
        "live_tasks": ("time", "task", "owner", "status", "note"),
        "incidents": ("time", "severity", "issue", "action", "owner", "follow_up", "status"),
    }
    for key, fields in during_specs.items():
        rows = require_list(during, key, "brief.during")
        validate_rows(rows, fields, f"brief.during.{key}")

    after = require_object(data, "after")
    registered = require_integer(after, "registered", "brief.after")
    checked_in = require_integer(after, "checked_in", "brief.after")
    if checked_in > registered:
        raise ValueError("brief.after.checked_in cannot exceed registered")
    satisfaction = require_number(after, "satisfaction_5", "brief.after")
    if satisfaction > 5:
        raise ValueError("brief.after.satisfaction_5 must be between 0 and 5")
    require_number(after, "actual_revenue_cny", "brief.after")
    require_number(after, "actual_cost_cny", "brief.after")
    metrics_status = require_text(after, "metrics_evidence_status", "brief.after")
    if metrics_status not in EVIDENCE_STATUSES:
        raise ValueError(f"brief.after.metrics_evidence_status must be one of {sorted(EVIDENCE_STATUSES)}")
    require_text(after, "suggestion", "brief.after")
    require_text(after, "retrospective", "brief.after")
    archive_state = require_text(after, "archive_state", "brief.after")
    if archive_state not in ARCHIVE_STATES:
        raise ValueError(f"brief.after.archive_state must be one of {sorted(ARCHIVE_STATES)}")

    after_specs = {
        "cases": ("type", "summary", "owner", "resolution", "due", "status"),
        "suppliers": ("name", "purchase_type", "current_node", "nodes", "owner", "status", "note"),
        "ugc": ("channel", "content_type", "count", "likes", "saves", "reward", "authorization", "reuse_state"),
        "feedback": ("source", "summary", "owner", "action", "status", "proof"),
    }
    for key, fields in after_specs.items():
        rows = require_list(after, key, "brief.after")
        validate_rows(rows, fields, f"brief.after.{key}")
    for index, supplier in enumerate(after["suppliers"]):
        nodes = supplier["nodes"]
        if not isinstance(nodes, list) or not nodes or not all(isinstance(node, str) and node.strip() for node in nodes):
            raise ValueError(f"brief.after.suppliers[{index}].nodes must be a non-empty string list")
        if supplier["current_node"] not in nodes:
            raise ValueError(f"brief.after.suppliers[{index}].current_node must be included in nodes")
    for index, ugc in enumerate(after["ugc"]):
        for key in ("count", "likes", "saves"):
            require_integer(ugc, key, f"brief.after.ugc[{index}]")


def safe_csv_cell(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    cleaned = value.replace("\r", " ").replace("\n", " ")
    if cleaned.startswith(("=", "+", "-", "@")):
        return "'" + cleaned
    return cleaned


def write_csv(path: Path, headers: list[str], rows: list[list[Any]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([safe_csv_cell(value) for value in headers])
        writer.writerows([[safe_csv_cell(value) for value in row] for row in rows])


def write_text(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def money(value: float) -> str:
    return f"¥{value:,.2f}"


def ratio(numerator: float, denominator: float) -> str:
    if denominator == 0:
        return "N/A"
    return f"{numerator / denominator:.1%}"


def md(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    rule = "|" + "|".join("---" for _ in headers) + "|"
    body = ["| " + " | ".join(md(value) for value in row) + " |" for row in rows]
    return "\n".join([head, rule, *body])


def generate(data: dict[str, Any], output: Path) -> list[Path]:
    output.mkdir(parents=True, exist_ok=True)
    before = data["before"]
    during = data["during"]
    after = data["after"]
    files: list[Path] = []

    check_in_rate = ratio(after["checked_in"], after["registered"])
    actual_roi = ratio(after["actual_revenue_cny"] - after["actual_cost_cny"], after["actual_cost_cny"])
    planned_roi = ratio(data["planned_revenue_cny"] - data["planned_budget_cny"], data["planned_budget_cny"])

    overview = output / "00-event-overview.md"
    write_text(
        overview,
        f"""# {data['event_name']}

> Evidence status: `{data['evidence_status']}`. Review all external actions and replace public examples with approved records.

## Event

| Field | Value |
|---|---|
| Project | {md(data['project'])} |
| Status | `{data['event_status']}` |
| Date | {data['date']} |
| Location | {md(data['location'])} |
| Owner | {md(data['owner'])} |
| Audience | {md(data['audience'])} |
| Expected attendance | {data['expected_attendance']} |
| Objective | {md(data['objective'])} |

## Planned economics

- Planned budget: {money(data['planned_budget_cny'])}
- Planned revenue: {money(data['planned_revenue_cny'])}
- Planned ROI: {planned_roi}

## Kit

1. `01-before-people.csv`
2. `02-before-materials.csv`
3. `03-before-rundown.csv`
4. `04-before-budget-and-fees.csv`
5. `05-during-contacts.csv`
6. `06-during-operations.md`
7. `07-after-data-and-roi.md`
8. `08-after-suppliers.csv`
9. `09-after-ugc.csv`
10. `10-after-cases-and-feedback.md`
11. `11-retrospective-and-archive.md`

## Guardrails

""" + "\n".join(f"- {item}" for item in data["guardrails"]),
    )
    files.append(overview)

    people = output / "01-before-people.csv"
    write_csv(people, ["姓名或角色", "职责", "负责人", "沟通渠道", "确认状态", "截止日期", "备注"], [
        [row["name"], row["role"], row["owner"], row["channel"], row["status"], row["due"], row["note"]]
        for row in before["people"]
    ])
    files.append(people)

    materials = output / "02-before-materials.csv"
    write_csv(materials, ["物料", "数量", "供应商", "到位状态", "截止日期", "备选方案"], [
        [row["item"], row["quantity"], row["supplier"], row["status"], row["due"], row["contingency"]]
        for row in before["materials"]
    ])
    files.append(materials)

    rundown = output / "03-before-rundown.csv"
    write_csv(rundown, ["时间", "任务", "负责人", "依赖", "状态", "备注"], [
        [row["time"], row["task"], row["owner"], row["dependency"], row["status"], row["note"]]
        for row in before["rundown"]
    ])
    files.append(rundown)

    budget = output / "04-before-budget-and-fees.csv"
    budget_rows = [
        ["预算", row["item"], row["planned_cny"], "", row["owner"], row["status"], row["note"]]
        for row in before["budget_items"]
    ]
    fee_rows = [
        ["收费", row["item"], row["unit_price_cny"] * row["expected_quantity"], row["unit_price_cny"], "活动负责人", row["status"], row["note"]]
        for row in before["fee_plan"]
    ]
    write_csv(budget, ["类型", "项目", "计划总额_CNY", "单价_CNY", "负责人", "状态", "备注"], budget_rows + fee_rows)
    files.append(budget)

    contacts = output / "05-during-contacts.csv"
    write_csv(contacts, ["姓名或角色", "职责", "联系渠道", "联系方式", "备份联系人", "备注"], [
        [row["name"], row["role"], row["channel"], row["contact"], row["backup"], row["note"]]
        for row in during["contacts"]
    ])
    files.append(contacts)

    live_task_table = markdown_table(
        ["时间", "现场任务", "负责人", "状态", "备注"],
        [[row["time"], row["task"], row["owner"], row["status"], row["note"]] for row in during["live_tasks"]],
    )
    incident_table = markdown_table(
        ["时间", "级别", "突发情况", "处理", "负责人", "后续", "状态"],
        [[row["time"], row["severity"], row["issue"], row["action"], row["owner"], row["follow_up"], row["status"]] for row in during["incidents"]],
    )
    operations = output / "06-during-operations.md"
    write_text(operations, f"# Activity during\n\n## Live tasks\n\n{live_task_table}\n\n## Incidents\n\n{incident_table}\n\nManual additions and edits remain allowed throughout the event.")
    files.append(operations)

    data_and_roi = output / "07-after-data-and-roi.md"
    write_text(
        data_and_roi,
        f"""# Activity after: data and actual ROI

> Metrics evidence status: `{after['metrics_evidence_status']}`

| Metric | Value |
|---|---:|
| Registered | {after['registered']} |
| Checked in | {after['checked_in']} |
| Check-in rate | {check_in_rate} |
| Satisfaction | {after['satisfaction_5']:.2f} / 5 |
| Actual revenue | {money(after['actual_revenue_cny'])} |
| Actual cost | {money(after['actual_cost_cny'])} |
| Actual ROI | {actual_roi} |

Actual ROI is calculated as `(actual revenue - actual cost) / actual cost`. Overall reports should use these actual values rather than planned amounts.
""",
    )
    files.append(data_and_roi)

    suppliers = output / "08-after-suppliers.csv"
    write_csv(suppliers, ["供应商", "采购类型", "当前节点", "适用节点", "负责人", "状态", "备注"], [
        [row["name"], row["purchase_type"], row["current_node"], " → ".join(row["nodes"]), row["owner"], row["status"], row["note"]]
        for row in after["suppliers"]
    ])
    files.append(suppliers)

    ugc = output / "09-after-ugc.csv"
    write_csv(ugc, ["渠道", "内容类型", "数量", "点赞", "收藏", "奖品", "授权", "复用状态"], [
        [row["channel"], row["content_type"], row["count"], row["likes"], row["saves"], row["reward"], row["authorization"], row["reuse_state"]]
        for row in after["ugc"]
    ])
    files.append(ugc)

    case_table = markdown_table(
        ["类型", "摘要", "负责人", "处理结果", "截止", "状态"],
        [[row["type"], row["summary"], row["owner"], row["resolution"], row["due"], row["status"]] for row in after["cases"]],
    )
    feedback_table = markdown_table(
        ["来源", "反馈", "负责人", "改进动作", "状态", "闭环证明"],
        [[row["source"], row["summary"], row["owner"], row["action"], row["status"], row["proof"]] for row in after["feedback"]],
    )
    cases = output / "10-after-cases-and-feedback.md"
    write_text(cases, f"# Cases and feedback\n\n## Cases\n\n{case_table}\n\n## Feedback closure\n\n{feedback_table}")
    files.append(cases)

    closed_suppliers = sum(row["status"] == "已闭环" for row in after["suppliers"])
    closed_cases = sum(row["status"] == "已闭环" for row in after["cases"])
    closed_feedback = sum(row["status"] == "已闭环" for row in after["feedback"])
    archive = output / "11-retrospective-and-archive.md"
    write_text(
        archive,
        f"""# Suggestions, retrospective, and archive

## Suggestion

{after['suggestion']}

## Retrospective

{after['retrospective']}

## Archive readiness

- Archive state: `{after['archive_state']}`
- Actual ROI reviewed: {actual_roi}
- Suppliers closed: {closed_suppliers} / {len(after['suppliers'])}
- Cases closed: {closed_cases} / {len(after['cases'])}
- Feedback items closed: {closed_feedback} / {len(after['feedback'])}

Use a completed-event archive for finished events and a separate cancelled-event archive for events that did not take place. Human review is required before changing this event to `archived`.
""",
    )
    files.append(archive)

    normalized = output / "data.json"
    normalized.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    files.append(normalized)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brief", required=True, type=Path, help="UTF-8 JSON brief")
    parser.add_argument("--output", required=True, type=Path, help="Output directory")
    parser.add_argument("--force", action="store_true", help="Replace known generated files in an existing kit")
    args = parser.parse_args()

    with args.brief.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    validate_brief(data)

    existing = [name for name in OUTPUT_NAMES if (args.output / name).exists()]
    if existing and not args.force:
        parser.error(f"output already contains {len(existing)} generated files; review it and pass --force to replace them")

    generated = generate(data, args.output)
    print(f"Generated {len(generated)} files in {args.output.resolve()}")
    for path in generated:
        print(path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
