"""Tests for NavigatorPropertiesCheck."""

from fingerprint_check.checks.navigator_properties import NavigatorPropertiesCheck
from tests.conftest import build_fake_request


def test_empty_languages_fails():
    check = NavigatorPropertiesCheck()
    req = build_fake_request()
    result = check.run(req, client_data={"plugins_count": 3, "languages": []})

    assert result.status == "fail"
    assert "languages" in result.explanation.lower()


def test_empty_plugins_on_chromium_fails():
    check = NavigatorPropertiesCheck()
    req = build_fake_request(headers=[("user-agent", "Mozilla/5.0 Chrome/124.0.0.0 Safari/537.36")])
    result = check.run(req, client_data={"plugins_count": 0, "languages": ["en-US"]})

    assert result.status == "fail"
    assert "plugins" in result.explanation.lower()


def test_empty_plugins_on_headless_chrome_fails():
    check = NavigatorPropertiesCheck()
    req = build_fake_request(headers=[("user-agent", "Mozilla/5.0 HeadlessChrome/124.0.0.0 Safari/537.36")])
    result = check.run(req, client_data={"plugins_count": 0, "languages": ["en-US"]})

    assert result.status == "fail"
    assert "plugins" in result.explanation.lower()


def test_empty_plugins_on_non_chromium_warns():
    check = NavigatorPropertiesCheck()
    req = build_fake_request(headers=[("user-agent", "Mozilla/5.0 Firefox/125.0")])
    result = check.run(req, client_data={"plugins_count": 0, "languages": ["en-US"]})

    assert result.status == "warn"


def test_normal_plugins_and_languages_passes():
    check = NavigatorPropertiesCheck()
    req = build_fake_request(headers=[("user-agent", "Mozilla/5.0 Chrome/124.0.0.0 Safari/537.36")])
    result = check.run(req, client_data={
        "plugins_count": 5,
        "languages": ["en-US", "en"],
    })

    assert result.status == "pass"
