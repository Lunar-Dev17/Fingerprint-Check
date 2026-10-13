"""Tests for MissingHeadersCheck."""

from fingerprint_check.checks.missing_headers import MissingHeadersCheck
from tests.conftest import build_fake_request


def test_missing_critical_headers_fails():
    check = MissingHeadersCheck()
    # Missing both accept-language and accept-encoding
    req = build_fake_request(headers=[
        ("user-agent", "Mozilla/5.0"),
        ("sec-fetch-dest", "document"),
    ])
    result = check.run(req)

    assert result.status == "fail"
    assert "critical" in result.explanation.lower()
    assert "accept-language" in result.explanation.lower()


def test_empty_header_value_fails():
    check = MissingHeadersCheck()
    # Header present but empty string
    req = build_fake_request(headers=[
        ("user-agent", "Mozilla/5.0"),
        ("accept-language", "   "),
        ("accept-encoding", "gzip, deflate"),
    ])
    result = check.run(req)

    assert result.status == "fail"
    assert "accept-language" in result.explanation.lower()


def test_missing_sec_fetch_warns():
    check = MissingHeadersCheck()
    # Has accept-language & accept-encoding, but lacks sec-fetch-*
    req = build_fake_request(headers=[
        ("user-agent", "Mozilla/5.0"),
        ("accept-language", "en-US,en;q=0.9"),
        ("accept-encoding", "gzip, deflate, br"),
    ])
    result = check.run(req)

    assert result.status == "warn"
    assert "sec-fetch" in result.explanation.lower()


def test_all_standard_headers_pass():
    check = MissingHeadersCheck()
    req = build_fake_request(headers=[
        ("user-agent", "Mozilla/5.0"),
        ("accept-language", "en-US,en;q=0.9"),
        ("accept-encoding", "gzip, deflate, br"),
        ("sec-fetch-dest", "document"),
        ("sec-fetch-mode", "navigate"),
        ("sec-fetch-site", "none"),
    ])
    result = check.run(req)

    assert result.status == "pass"
