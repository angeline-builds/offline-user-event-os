# Offline User Event OS

**English** | [简体中文](README.zh-CN.md)

A reusable Codex Skill that turns an offline event brief or an existing event plan into a lifecycle-based operations kit. It is designed for recurring brand, community, customer, employee, and user events.

> This is an independent portfolio project. It is not affiliated with or endorsed by any model provider, collaboration platform, or event-services company.

## Why this project exists

Event teams often plan in documents, execute through scattered messages, and rebuild the same reporting tables afterward. This Skill keeps the original plan editable while connecting preparation, live operations, actual results, lessons, and archive readiness in one repeatable workflow.

It organizes work around three stages:

- Activity before: people, materials, run of show, user arrangements, budget, fees, and planned revenue.
- Activity during: contacts, live tasks, incidents, changes, and follow-up.
- Activity after: attendance, satisfaction, actual revenue and cost, actual ROI, cases, supplier payment nodes, UGC, feedback, lessons, and archive readiness.

The included example is fictional and marked `SIMULATED`. It contains no real contact details, API credentials, participant records, or supplier data.

## Evidence labels

- `PLANNED`: a future target or approved plan.
- `ACTUAL`: a result supported by current-event evidence.
- `SIMULATED`: fictional data used for demonstration or testing.
- `TO_VALIDATE`: an incomplete item that still requires confirmation.

## Install

Copy the `offline-user-event-os` directory into your Codex skills directory, then start a new Codex session:

- Windows: `%USERPROFILE%\.codex\skills\offline-user-event-os`
- macOS / Linux: `~/.codex/skills/offline-user-event-os`

## Use

Invoke the Skill explicitly:

```text
Use $offline-user-event-os to turn this event brief into a lifecycle-based operations kit.
```

To test the deterministic generator directly:

```powershell
python offline-user-event-os/scripts/generate_event_kit.py `
  --brief offline-user-event-os/assets/brief.example.json `
  --output generated/example
```

The generator creates 13 editable Markdown, CSV, and JSON files. It refuses to overwrite an existing kit unless `--force` is supplied.

Validate the repository without additional packages:

```powershell
python scripts/validate_skill.py
```

## Structure

```text
.
├── .github/workflows/validate.yml
├── README.md
├── README.zh-CN.md
├── LICENSE
├── SECURITY.md
├── scripts/validate_skill.py
└── offline-user-event-os/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── assets/brief.example.json
    ├── references/
    │   ├── brief-schema.md
    │   └── quality-gates.md
    └── scripts/generate_event_kit.py
```

## Safety and limitations

- Generated plans are drafts and do not authorize spending, outreach, contracts, publication, refunds, data processing, or safety-critical decisions.
- Keep planned figures separate from actual results.
- Never publish API keys, phone numbers, personal email, participant lists, raw complaints, payment details, confidential contracts, or identifying faces.
- Use redacted or fictional data in public examples.
- Adapt legal, privacy, accessibility, venue, and emergency requirements to the real event and jurisdiction.

## License

This project is available under the [MIT License](LICENSE).
