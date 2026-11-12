"""Collect real metrics from Ruff, Radon, Coverage XML and JUnit XML."""

import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from xml.etree import ElementTree as ET

REPORTS = Path("reports")


def command_json(module: str, arguments: list[str], allowed: tuple[int, ...] = (0,)):
    result = subprocess.run(
        [sys.executable, "-m", module, *arguments],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode not in allowed:
        raise RuntimeError(result.stderr or result.stdout)
    return json.loads(result.stdout)


def functions(blocks):
    for block in blocks:
        if block["type"] in {"function", "method"}:
            yield block["complexity"]
        yield from functions(block.get("methods", []))
        yield from functions(block.get("closures", []))


def main():
    REPORTS.mkdir(exist_ok=True)
    lint = command_json(
        "ruff", ["check", "src", "tests", "scripts", "--output-format=json"], (0, 1)
    )
    complexity = command_json("radon", ["cc", "src", "-j"])
    (REPORTS / "ruff.json").write_text(json.dumps(lint, indent=2), encoding="utf-8")
    (REPORTS / "complexity.json").write_text(json.dumps(complexity, indent=2), encoding="utf-8")
    scores = [value for blocks in complexity.values() for value in functions(blocks)]
    values = {
        "lint_issues": len(lint),
        "complexity_mean": round(sum(scores) / len(scores), 3) if scores else None,
        "complexity_max": max(scores) if scores else None,
    }
    missing = []
    if (REPORTS / "coverage.xml").exists():
        root = ET.parse(REPORTS / "coverage.xml").getroot()
        lines_valid = int(root.attrib["lines-valid"])
        lines_covered = int(root.attrib["lines-covered"])
        branches_valid = int(root.attrib["branches-valid"])
        branches_covered = int(root.attrib["branches-covered"])
        values["line_coverage_percent"] = (
            round(100 * lines_covered / lines_valid, 2) if lines_valid else None
        )
        values["branch_coverage_percent"] = (
            round(100 * branches_covered / branches_valid, 2) if branches_valid else None
        )
    else:
        missing.append("coverage.xml")
    if (REPORTS / "junit.xml").exists():
        root = ET.parse(REPORTS / "junit.xml").getroot()
        suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
        counts = {
            key: sum(int(s.attrib.get(key, 0)) for s in suites)
            for key in ("tests", "failures", "errors", "skipped")
        }
        values.update(
            {
                "tests_passed": counts["tests"]
                - sum(counts[k] for k in ("failures", "errors", "skipped")),
                "tests_failed": counts["failures"],
                "tests_errors": counts["errors"],
                "tests_skipped": counts["skipped"],
                "test_seconds": round(sum(float(s.attrib.get("time", 0)) for s in suites), 3),
            }
        )
    else:
        missing.append("junit.xml")
    server = os.getenv("GITHUB_SERVER_URL", "https://github.com")
    repository = os.getenv("GITHUB_REPOSITORY")
    run_id = os.getenv("GITHUB_RUN_ID")
    run_url = f"{server}/{repository}/actions/runs/{run_id}" if repository and run_id else None
    snapshot = {
        "recorded_at_utc": datetime.now(UTC).isoformat(),
        "commit": os.getenv("GITHUB_SHA", "local-uncommitted"),
        "ref": os.getenv("GITHUB_REF", "local"),
        "pipeline_url": run_url,
        "scope": "coverage/complexity: src; lint: src/tests/scripts; tests: all tests",
        "missing_reports": missing,
        "metrics": values,
    }
    (REPORTS / "metrics.json").write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    print(json.dumps(snapshot, indent=2))
    return int(bool(missing))


if __name__ == "__main__":
    raise SystemExit(main())
