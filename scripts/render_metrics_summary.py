"""Render collected metrics as a Markdown table for GitHub Actions."""

import argparse
import json
import os
from datetime import datetime
from html import escape
from pathlib import Path

METRICS = (
    ("lint_issues", "Замечания линтера", ""),
    ("complexity_mean", "Средняя цикломатическая сложность", ""),
    ("complexity_max", "Максимальная цикломатическая сложность", ""),
    ("line_coverage_percent", "Покрытие строк", "%"),
    ("branch_coverage_percent", "Покрытие ветвей", "%"),
    ("tests_passed", "Успешные тесты", ""),
    ("tests_failed", "Упавшие тесты", ""),
    ("tests_errors", "Ошибки тестов", ""),
    ("tests_skipped", "Пропущенные тесты", ""),
    ("test_seconds", "Время тестирования", " с"),
)


def markdown_text(value: str) -> str:
    return escape(value, quote=False).replace("|", r"\|").replace("`", r"\`")


def render_summary(snapshot: dict) -> str:
    ref = snapshot["ref"].removeprefix("refs/tags/").removeprefix("refs/heads/")
    commit = snapshot["commit"][:7]
    recorded = datetime.fromisoformat(snapshot["recorded_at_utc"])
    lines = [
        "## Метрики качества",
        "",
        f"**Версия:** {markdown_text(ref)} · **Коммит:** {markdown_text(commit)}",
        f"**Дата измерения (UTC):** {recorded:%d.%m.%Y %H:%M:%S}",
        "",
    ]
    if snapshot.get("missing_reports"):
        reports = ", ".join(markdown_text(name) for name in snapshot["missing_reports"])
        lines.extend([f"> **Неполные данные:** отсутствуют отчёты {reports}.", ""])
    lines.extend(["| Метрика | Значение |", "| :--- | ---: |"])
    values = snapshot["metrics"]
    for key, label, unit in METRICS:
        value = values.get(key)
        formatted = "Нет данных" if value is None else f"{value:g}{unit}"
        lines.append(f"| {label} | {formatted} |")
    lines.extend(
        [
            "",
            "Покрытие и сложность: код приложения. Линтер: src, tests и scripts.",
            "Полный JSON и исходные отчёты доступны в артефакте **quality-reports**.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("reports/metrics.json"))
    args = parser.parse_args()
    summary = render_summary(json.loads(args.input.read_text(encoding="utf-8")))
    destination = os.getenv("GITHUB_STEP_SUMMARY")
    if destination:
        with Path(destination).open("a", encoding="utf-8", newline="\n") as output:
            output.write(summary)
    else:
        print(summary, end="")


if __name__ == "__main__":
    main()
