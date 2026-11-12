import pytest

from scripts.check_commits import valid_header


@pytest.mark.parametrize(
    "header", ["feat(api): add log ingestion", "fix!: change schema", "docs: описание API"]
)
def test_valid_headers(header):
    assert valid_header(header)


@pytest.mark.parametrize("header", ["update", "feat: ", "feat: " + "x" * 100, "unknown: work"])
def test_invalid_headers(header):
    assert not valid_header(header)
