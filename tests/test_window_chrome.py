"""Tests for WindowChromeCheck."""

from fingerprint_check.checks.window_chrome import WindowChromeCheck
from tests.conftest import build_fake_request

CHROME_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36"
FIREFOX_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"


def test_missing_window_chrome_on_chrome_fails():
    check = WindowChromeCheck()
    req = build_fake_request(headers=[("user-agent", CHROME_UA)])
    result = check.run(req, client_data={"has_window_chrome": False})

    assert result.status == "fail"
    assert "window.chrome" in result.explanation


def test_missing_chrome_runtime_warns():
    check = WindowChromeCheck()
    req = build_fake_request(headers=[("user-agent", CHROME_UA)])
    result = check.run(req, client_data={"has_window_chrome": True, "has_chrome_runtime": False})

    assert result.status == "warn"
    assert "runtime" in result.explanation.lower()


def test_chrome_with_valid_window_chrome_passes():
    check = WindowChromeCheck()
    req = build_fake_request(headers=[("user-agent", CHROME_UA)])
    result = check.run(req, client_data={"has_window_chrome": True, "has_chrome_runtime": True})

    assert result.status == "pass"


def test_window_chrome_present_on_firefox_fails():
    check = WindowChromeCheck()
    req = build_fake_request(headers=[("user-agent", FIREFOX_UA)])
    result = check.run(req, client_data={"has_window_chrome": True})

    assert result.status == "fail"
    assert "Firefox" in result.explanation


def test_firefox_without_window_chrome_passes():
    check = WindowChromeCheck()
    req = build_fake_request(headers=[("user-agent", FIREFOX_UA)])
    result = check.run(req, client_data={"has_window_chrome": False})

    assert result.status == "pass"
