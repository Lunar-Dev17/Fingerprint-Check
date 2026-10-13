"""Tests for WebdriverCheck."""

from fingerprint_check.checks.webdriver import WebdriverCheck
from tests.conftest import build_fake_request


def test_webdriver_true_fails():
    check = WebdriverCheck()
    req = build_fake_request()
    result = check.run(req, client_data={"webdriver": True})

    assert result.status == "fail"
    assert "navigator.webdriver" in result.explanation
    assert result.fix != ""


def test_webdriver_false_passes():
    check = WebdriverCheck()
    req = build_fake_request()
    result = check.run(req, client_data={"webdriver": False})

    assert result.status == "pass"


def test_no_client_data_warns():
    check = WebdriverCheck()
    req = build_fake_request()
    result = check.run(req, client_data=None)

    assert result.status == "warn"
