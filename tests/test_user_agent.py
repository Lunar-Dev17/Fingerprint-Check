"""Tests for UserAgentCheck."""

from fingerprint_check.checks.user_agent import UserAgentCheck
from tests.conftest import build_fake_request

CHROME_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
FIREFOX_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"


def test_missing_user_agent_fails():
    check = UserAgentCheck()
    req = build_fake_request(headers=[])
    result = check.run(req)

    assert result.name == "User-Agent Present and Plausible"
    assert result.status == "fail"
    assert "missing" in result.explanation.lower()
    assert result.fix != ""
    assert result.fix_suggestion == result.fix


def test_bot_tokens_fail():
    check = UserAgentCheck()
    bot_uas = [
        "python-requests/2.31.0",
        "curl/7.88.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 Playwright/1.43.0",
        "Scrapy/2.11.0 (+https://scrapy.org)",
        "PostmanRuntime/7.36.0",
    ]
    for ua in bot_uas:
        req = build_fake_request(headers=[("user-agent", ua)])
        result = check.run(req)
        assert result.status == "fail", f"Expected fail for {ua}"
        assert result.fix != ""


def test_ua_mismatch_fails():
    check = UserAgentCheck()
    req = build_fake_request(headers=[("user-agent", CHROME_UA)])
    result = check.run(req, client_data={"js_user_agent": FIREFOX_UA})
    assert result.status == "fail"
    assert "mismatch" in result.explanation.lower()


def test_non_standard_or_short_ua_warns():
    check = UserAgentCheck()
    req = build_fake_request(headers=[("user-agent", "CustomBrowser/1.0 (Test)")])
    result = check.run(req)
    assert result.status == "warn"
    assert "mozilla/5.0" in result.explanation.lower()

    short_req = build_fake_request(headers=[("user-agent", "Mozilla/5.0 Short")])
    short_res = check.run(short_req)
    assert short_res.status == "warn"


def test_valid_browser_ua_passes():
    check = UserAgentCheck()
    for ua in (CHROME_UA, FIREFOX_UA):
        req = build_fake_request(headers=[("user-agent", ua)])
        result = check.run(req)
        assert result.status == "pass"
