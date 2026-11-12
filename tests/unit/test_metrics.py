import json

import pytest

from scripts import collect_metrics


@pytest.fixture
def reports(tmp_path, monkeypatch):
    monkeypatch.setattr(collect_metrics, "REPORTS", tmp_path)
    for key in (
        "GITHUB_SERVER_URL",
        "GITHUB_REPOSITORY",
        "GITHUB_RUN_ID",
        "GITHUB_SHA",
        "GITHUB_REF",
    ):
        monkeypatch.delenv(key, raising=False)
    (tmp_path / "coverage.xml").write_text(
        '<coverage lines-valid="10" lines-covered="8" branches-valid="4" branches-covered="2"/>',
        encoding="utf-8",
    )
    (tmp_path / "junit.xml").write_text(
        '<testsuites><testsuite tests="4" failures="1" errors="1" '
        'skipped="1" time="0.25"/></testsuites>',
        encoding="utf-8",
    )

    def analyzer(module, arguments, allowed=(0,)):
        if module == "ruff":
            return [{"code": "F401"}, {"code": "E501"}]
        return {
            "src/example.py": [
                {"type": "function", "complexity": 2},
                {"type": "function", "complexity": 4},
            ]
        }

    monkeypatch.setattr(collect_metrics, "command_json", analyzer)
    return tmp_path


def test_github_metadata_and_independent_metric_counts(reports, monkeypatch):
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.example.test")
    monkeypatch.setenv("GITHUB_REPOSITORY", "student/web-log-reports")
    monkeypatch.setenv("GITHUB_RUN_ID", "12345")
    monkeypatch.setenv("GITHUB_SHA", "a" * 40)
    monkeypatch.setenv("GITHUB_REF", "refs/tags/stage/baseline")
    assert collect_metrics.main() == 0
    snapshot = json.loads((reports / "metrics.json").read_text(encoding="utf-8"))
    assert snapshot["pipeline_url"] == (
        "https://github.example.test/student/web-log-reports/actions/runs/12345"
    )
    assert snapshot["commit"] == "a" * 40
    assert snapshot["ref"] == "refs/tags/stage/baseline"
    assert snapshot["metrics"] == {
        "lint_issues": 2,
        "complexity_mean": 3.0,
        "complexity_max": 4,
        "line_coverage_percent": 80.0,
        "branch_coverage_percent": 50.0,
        "tests_passed": 1,
        "tests_failed": 1,
        "tests_errors": 1,
        "tests_skipped": 1,
        "test_seconds": 0.25,
    }


def test_local_run_does_not_claim_to_be_github_run(reports):
    assert collect_metrics.main() == 0
    snapshot = json.loads((reports / "metrics.json").read_text(encoding="utf-8"))
    assert snapshot["pipeline_url"] is None
    assert snapshot["commit"] == "local-uncommitted"
    assert snapshot["ref"] == "local"


def test_missing_coverage_fails_instead_of_inventing_values(reports):
    (reports / "coverage.xml").unlink()
    assert collect_metrics.main() == 1
    snapshot = json.loads((reports / "metrics.json").read_text(encoding="utf-8"))
    assert snapshot["missing_reports"] == ["coverage.xml"]
    assert "line_coverage_percent" not in snapshot["metrics"]
    assert "branch_coverage_percent" not in snapshot["metrics"]
