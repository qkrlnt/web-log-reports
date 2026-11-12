"""Basic statistics for parsed access records."""

from collections.abc import Sequence

from web_log_reports.parser import LogRecord


def summarize(records: Sequence[LogRecord]) -> dict[str, int | float]:
    total = len(records)
    errors = sum(record.status >= 400 for record in records)
    return {
        "requests": total,
        "errors": errors,
        "error_rate_percent": round(100 * errors / total, 2) if total else 0.0,
        "bytes_sent": sum(record.size for record in records),
    }
