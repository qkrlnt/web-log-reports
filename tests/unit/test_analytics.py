from web_log_reports.analytics import summarize
from web_log_reports.parser import parse_line


def test_empty_statistics():
    assert summarize([]) == {"requests": 0, "errors": 0, "error_rate_percent": 0.0, "bytes_sent": 0}


def test_statistics_include_client_and_server_errors():
    records = [
        parse_line(f'127.0.0.1 - - [12/Nov/2026:10:00:00 +0400] "GET / HTTP/1.1" {s} 10')
        for s in [200, 404, 500]
    ]
    assert summarize(records) == {
        "requests": 3,
        "errors": 2,
        "error_rate_percent": 66.67,
        "bytes_sent": 30,
    }
