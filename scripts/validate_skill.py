#!/usr/bin/env python3
"""Validate the public Skill bundle without third-party dependencies."""

from __future__ import annotations

import json
import locale
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "offline-user-event-os"
GENERATOR = SKILL / "scripts" / "generate_event_kit.py"
BRIEF = SKILL / "assets" / "brief.example.json"

REQUIRED_FILES = (
    ROOT / "README.md",
    ROOT / "README.zh-CN.md",
    ROOT / "LICENSE",
    ROOT / "SECURITY.md",
    SKILL / "SKILL.md",
    SKILL / "agents" / "openai.yaml",
    BRIEF,
    SKILL / "references" / "brief-schema.md",
    SKILL / "references" / "quality-gates.md",
    GENERATOR,
)

EXPECTED_OUTPUTS = {
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
}


def fail(message: str) -> None:
    raise SystemExit(f"Validation failed: {message}")


def run_generator(output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GENERATOR), "--brief", str(BRIEF), "--output", str(output)],
        text=True,
        encoding=locale.getpreferredencoding(False),
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def main() -> int:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.is_file()]
    if missing:
        fail("missing required files: " + ", ".join(missing))

    skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    if not skill_text.startswith("---\n"):
        fail("SKILL.md must start with YAML frontmatter")
    if "name: offline-user-event-os" not in skill_text:
        fail("SKILL.md has the wrong name")
    if "description:" not in skill_text:
        fail("SKILL.md must include a description")

    agent_text = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
    if "$offline-user-event-os" not in agent_text:
        fail("agents/openai.yaml must invoke the Skill by name")

    brief = json.loads(BRIEF.read_text(encoding="utf-8"))
    if brief.get("evidence_status") != "SIMULATED":
        fail("the public example must be marked SIMULATED")
    if brief.get("after", {}).get("metrics_evidence_status") != "SIMULATED":
        fail("example metrics must be marked SIMULATED")

    with tempfile.TemporaryDirectory(prefix="offline-event-os-") as temp_dir:
        output = Path(temp_dir) / "generated"
        result = run_generator(output)
        if result.returncode != 0:
            fail("example generation failed")
        actual = {path.name for path in output.iterdir() if path.is_file()}
        if actual != EXPECTED_OUTPUTS:
            fail("generated file set does not match the contract")

        second = run_generator(output)
        if second.returncode == 0:
            fail("the overwrite guard did not block an existing kit")

    print("Validation passed: structure, simulated example, generator, and overwrite guard.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
