from datetime import timedelta

import pytest

from web_log_reports.parser import parse_line

LINE = '127.0.0.1 - - [12/Nov/2026:10:00:00 +0400] "GET / HTTP/1.1" 200 123'


def test_parse_common_log():
    record = parse_line(LINE)
    assert (record.ip, record.method, record.path) == ("127.0.0.1", "GET", "/")
    assert (record.status, record.size) == (200, 123)
    assert record.timestamp.utcoffset() == timedelta(hours=4)


def test_parse_combined_log_without_response_size():
    record = parse_line(LINE.replace("200 123", '404 - "-" "Browser/1.0"'))
    assert (record.status, record.size) == (404, 0)


@pytest.mark.parametrize(
    "line",
    ["broken log", LINE.replace("200 123", "700 123"), LINE.replace("12/Nov", "99/Nov")],
)
def test_reject_invalid_record(line):
    with pytest.raises(ValueError):
        parse_line(line)
