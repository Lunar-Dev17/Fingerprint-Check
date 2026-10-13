"""Tests for HeaderOrderCheck."""

from fingerprint_check.checks.header_order import HeaderOrderCheck
from tests.conftest import build_fake_request


def test_alphabetical_headers_fail():
    check = HeaderOrderCheck()
    # Headers arranged in strict alphabetical order
    alpha_headers = [
        ("accept", "text/html"),
        ("accept-encoding", "gzip, deflate"),
        ("accept-language", "en-US,en;q=0.9"),
        ("host", "example.com"),
        ("sec-ch-ua", '"Chromium";v="124"'),
        ("user-agent", "Mozilla/5.0"),
    ]
    req = build_fake_request(headers=alpha_headers)
    result = check.run(req)

    assert result.status == "fail"
    assert "alphabetical" in result.explanation.lower()


def test_chrome_order_passes():
    check = HeaderOrderCheck()
    # Canonical Chrome order
    chrome_headers = [
        ("host", "example.com"),
        ("connection", "keep-alive"),
        ("sec-ch-ua", '"Chromium";v="124", "Google Chrome";v="124"'),
        ("sec-ch-ua-mobile", "?0"),
        ("sec-ch-ua-platform", '"Windows"'),
        ("upgrade-insecure-requests", "1"),
        ("user-agent", "Mozilla/5.0"),
        ("accept", "text/html,application/xhtml+xml"),
        ("sec-fetch-site", "none"),
        ("sec-fetch-mode", "navigate"),
        ("sec-fetch-user", "?1"),
        ("sec-fetch-dest", "document"),
        ("accept-encoding", "gzip, deflate, br"),
        ("accept-language", "en-US,en;q=0.9"),
    ]
    req = build_fake_request(headers=chrome_headers)
    result = check.run(req)

    assert result.status == "pass"
    assert "matches chrome" in result.explanation.lower()


def test_inverted_order_fails_or_warns():
    check = HeaderOrderCheck()
    # Completely reversed order
    reversed_headers = [
        ("accept-language", "en-US,en;q=0.9"),
        ("accept-encoding", "gzip, deflate, br"),
        ("sec-fetch-dest", "document"),
        ("sec-fetch-mode", "navigate"),
        ("sec-fetch-site", "none"),
        ("accept", "text/html"),
        ("user-agent", "Mozilla/5.0"),
        ("sec-ch-ua", '"Chromium";v="124"'),
        ("host", "example.com"),
    ]
    req = build_fake_request(headers=reversed_headers)
    result = check.run(req)

    assert result.status in ("fail", "warn")


def test_too_few_headers_warns():
    check = HeaderOrderCheck()
    req = build_fake_request(headers=[("host", "example.com")])
    result = check.run(req)
    assert result.status == "warn"
