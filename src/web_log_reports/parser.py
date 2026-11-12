"""Parse Common Log Format and Combined Log Format access records."""

import re
from dataclasses import dataclass
from datetime import datetime

PATTERN = re.compile(
    r"(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] "
    r'"(?P<method>[A-Z]+) (?P<path>\S+) HTTP/\d(?:\.\d)?" '
    r"(?P<status>\d{3}) (?P<size>\d+|-)"
    r'(?: "[^"\r\n]*" "[^"\r\n]*")?'
)


@dataclass(frozen=True)
class LogRecord:
    ip: str
    timestamp: datetime
    method: str
    path: str
    status: int
    size: int


def parse_line(line: str) -> LogRecord:
    match = PATTERN.fullmatch(line.strip())
    if match is None:
        raise ValueError("Unsupported access log format")
    status = int(match["status"])
    if not 100 <= status <= 599:
        raise ValueError("Invalid HTTP status")
    return LogRecord(
        ip=match["ip"],
        timestamp=datetime.strptime(match["time"], "%d/%b/%Y:%H:%M:%S %z"),
        method=match["method"],
        path=match["path"],
        status=status,
        size=0 if match["size"] == "-" else int(match["size"]),
    )
