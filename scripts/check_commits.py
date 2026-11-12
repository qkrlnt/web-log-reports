"""Check a commit message file or all non-merge commits in a Git range."""

import argparse
import re
import subprocess
from pathlib import Path

HEADER = re.compile(
    r"(?:feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(?:\([a-z0-9_-]+\))?!?: \S[^\r\n]*"
)


def valid_header(header: str) -> bool:
    return len(header) <= 100 and HEADER.fullmatch(header) is not None


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", type=Path)
    group.add_argument("--range", dest="revision")
    args = parser.parse_args()
    if args.file:
        lines = args.file.read_text(encoding="utf-8-sig").splitlines()
        headers = [lines[0] if lines else ""]
    else:
        result = subprocess.run(
            ["git", "log", "--no-merges", "--format=%s", args.revision],
            check=True,
            text=True,
            encoding="utf-8",
            capture_output=True,
        )
        headers = result.stdout.splitlines()
    invalid = [header for header in headers if not valid_header(header)]
    for header in invalid:
        print(f"Invalid Conventional Commit header: {header!r}")
    print(f"Checked {len(headers)} commit message(s)")
    return int(bool(invalid))


if __name__ == "__main__":
    raise SystemExit(main())
