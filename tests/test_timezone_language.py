"""Tests for TimezoneLanguageCheck."""

from fingerprint_check.checks.timezone_language import TimezoneLanguageCheck
from tests.conftest import build_fake_request


def test_utc_timezone_warns():
    check = TimezoneLanguageCheck()
    req = build_fake_request(headers=[("accept-language", "en-US,en;q=0.9")])
    result = check.run(req, client_data={"timezone": "UTC"})

    assert result.status == "warn"
    assert "utc" in result.explanation.lower()


def test_timezone_locale_mismatch_warns():
    check = TimezoneLanguageCheck()
    # German language with Asian timezone
    req = build_fake_request(headers=[("accept-language", "de-DE,de;q=0.9")])
    result = check.run(req, client_data={"timezone": "Asia/Shanghai"})

    assert result.status == "warn"
    assert "mismatch" in result.explanation.lower()


def test_aligned_timezone_and_language_passes():
    check = TimezoneLanguageCheck()
    req = build_fake_request(headers=[("accept-language", "de-DE,de;q=0.9")])
    result = check.run(req, client_data={"timezone": "Europe/Berlin"})

    assert result.status == "pass"


def test_no_client_data_warns():
    check = TimezoneLanguageCheck()
    req = build_fake_request(headers=[("accept-language", "en-US")])
    result = check.run(req, client_data=None)

    assert result.status == "warn"
