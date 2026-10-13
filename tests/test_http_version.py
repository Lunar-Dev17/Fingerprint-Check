"""Tests for HttpVersionCheck."""

from fingerprint_check.checks.http_version import HttpVersionCheck
from tests.conftest import build_fake_request


def test_http_1_0_fails():
    check = HttpVersionCheck()
    req = build_fake_request(http_version="1.0")
    result = check.run(req)

    assert result.status == "fail"
    assert "1.0" in result.explanation


def test_http_1_1_warns():
    check = HttpVersionCheck()
    req = build_fake_request(http_version="1.1")
    result = check.run(req)

    assert result.status == "warn"
    assert "1.1" in result.explanation


def test_http_2_passes():
    check = HttpVersionCheck()
    req = build_fake_request(http_version="2.0")
    result = check.run(req)

    assert result.status == "pass"


def test_http_3_passes():
    check = HttpVersionCheck()
    req = build_fake_request(http_version="3")
    result = check.run(req)

    assert result.status == "pass"
