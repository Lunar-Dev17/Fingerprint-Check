"""Tests for ClientHintsCheck."""

from fingerprint_check.checks.client_hints import ClientHintsCheck
from tests.conftest import build_fake_request

CHROME_WIN_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
CHROME_MAC_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
HEADLESS_CHROME_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/124.0.0.0 Safari/537.36"
FIREFOX_WIN_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
SAFARI_MAC_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"


def test_missing_sec_ch_ua_for_chrome_fails():
    check = ClientHintsCheck()
    req = build_fake_request(headers=[("user-agent", CHROME_WIN_UA)])
    result = check.run(req)

    assert result.status == "fail"
    assert "sec-ch-ua" in result.explanation


def test_missing_sec_ch_ua_for_headless_chrome_fails():
    check = ClientHintsCheck()
    req = build_fake_request(headers=[("user-agent", HEADLESS_CHROME_UA)])
    result = check.run(req)

    assert result.status == "fail"
    assert "sec-ch-ua" in result.explanation


def test_sec_ch_ua_present_for_firefox_or_safari_fails():
    check = ClientHintsCheck()

    # Firefox with Chrome client hints
    req_ff = build_fake_request(headers=[
        ("user-agent", FIREFOX_WIN_UA),
        ("sec-ch-ua", '"Chromium";v="124", "Google Chrome";v="124"'),
    ])
    result_ff = check.run(req_ff)
    assert result_ff.status == "fail"
    assert "Firefox" in result_ff.explanation

    # Firefox with only sec-ch-ua-platform
    req_ff_plat = build_fake_request(headers=[
        ("user-agent", FIREFOX_WIN_UA),
        ("sec-ch-ua-platform", '"Windows"'),
    ])
    result_ff_plat = check.run(req_ff_plat)
    assert result_ff_plat.status == "fail"
    assert "Firefox" in result_ff_plat.explanation

    # Safari with Chrome client hints
    req_safari = build_fake_request(headers=[
        ("user-agent", SAFARI_MAC_UA),
        ("sec-ch-ua", '"Chromium";v="124", "Google Chrome";v="124"'),
    ])
    result_safari = check.run(req_safari)
    assert result_safari.status == "fail"
    assert "Safari" in result_safari.explanation


def test_version_mismatch_fails():
    check = ClientHintsCheck()
    # UA declares Chrome/124, but sec-ch-ua declares version 110
    req = build_fake_request(headers=[
        ("user-agent", CHROME_WIN_UA),
        ("sec-ch-ua", '"Chromium";v="110", "Google Chrome";v="110"'),
        ("sec-ch-ua-platform", '"Windows"'),
    ])
    result = check.run(req)
    assert result.status == "fail"
    assert "Version mismatch" in result.explanation
    assert "124" in result.explanation
    assert "110" in result.explanation


def test_platform_mismatch_fails():
    check = ClientHintsCheck()
    # Windows in UA, but macOS in sec-ch-ua-platform
    req = build_fake_request(headers=[
        ("user-agent", CHROME_WIN_UA),
        ("sec-ch-ua", '"Chromium";v="124", "Google Chrome";v="124"'),
        ("sec-ch-ua-platform", '"macOS"'),
    ])
    result = check.run(req)
    assert result.status == "fail"
    assert "mismatch" in result.explanation.lower()
    assert "Windows" in result.explanation


def test_mobile_mismatch_warns():
    check = ClientHintsCheck()
    # Desktop UA with mobile hint
    req = build_fake_request(headers=[
        ("user-agent", CHROME_WIN_UA),
        ("sec-ch-ua", '"Chromium";v="124"'),
        ("sec-ch-ua-platform", '"Windows"'),
        ("sec-ch-ua-mobile", "?1"),
    ])
    result = check.run(req)
    assert result.status == "warn"
    assert "mobile" in result.explanation.lower()


def test_consistent_chrome_passes():
    check = ClientHintsCheck()
    req = build_fake_request(headers=[
        ("user-agent", CHROME_WIN_UA),
        ("sec-ch-ua", '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"'),
        ("sec-ch-ua-platform", '"Windows"'),
        ("sec-ch-ua-mobile", "?0"),
    ])
    result = check.run(req)
    assert result.status == "pass"


def test_consistent_firefox_no_hints_passes():
    check = ClientHintsCheck()
    req = build_fake_request(headers=[
        ("user-agent", FIREFOX_WIN_UA),
    ])
    result = check.run(req)
    assert result.status == "pass"
