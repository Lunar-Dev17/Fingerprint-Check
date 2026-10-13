"""Tests for ScreenHeadlessCheck."""

from fingerprint_check.checks.screen_headless import ScreenHeadlessCheck
from tests.conftest import build_fake_request


def test_headless_ua_fails():
    check = ScreenHeadlessCheck()
    req = build_fake_request()
    result = check.run(req, client_data={
        "js_user_agent": "Mozilla/5.0 AppleWebKit/537.36 HeadlessChrome/124.0.0.0 Safari/537.36",
        "outer_width": 1920,
        "outer_height": 1080,
        "screen_width": 1920,
        "screen_height": 1080,
    })

    assert result.status == "fail"
    assert "headlesschrome" in result.explanation.lower()


def test_zero_outer_dimensions_fail():
    check = ScreenHeadlessCheck()
    req = build_fake_request()
    result = check.run(req, client_data={
        "js_user_agent": "Mozilla/5.0 Chrome/124.0.0.0 Safari/537.36",
        "outer_width": 0,
        "outer_height": 0,
        "screen_width": 1920,
        "screen_height": 1080,
    })

    assert result.status == "fail"
    assert "outerwidth" in result.explanation.lower()


def test_inner_width_greater_than_outer_width_warns():
    check = ScreenHeadlessCheck()
    req = build_fake_request()
    result = check.run(req, client_data={
        "js_user_agent": "Mozilla/5.0 Chrome/124.0.0.0 Safari/537.36",
        "outer_width": 1000,
        "outer_height": 800,
        "inner_width": 1200,
        "inner_height": 800,
        "screen_width": 1920,
        "screen_height": 1080,
        "screen_color_depth": 24,
    })

    assert result.status == "warn"
    assert "exceeds" in result.explanation.lower()


def test_default_800x600_screen_warns():
    check = ScreenHeadlessCheck()
    req = build_fake_request()
    result = check.run(req, client_data={
        "outer_width": 800,
        "outer_height": 600,
        "screen_width": 800,
        "screen_height": 600,
        "screen_color_depth": 24,
    })

    assert result.status == "warn"
    assert "800x600" in result.explanation


def test_normal_screen_and_window_passes():
    check = ScreenHeadlessCheck()
    req = build_fake_request()
    result = check.run(req, client_data={
        "outer_width": 1920,
        "outer_height": 1040,
        "inner_width": 1920,
        "inner_height": 950,
        "screen_width": 1920,
        "screen_height": 1080,
        "screen_color_depth": 24,
    })

    assert result.status == "pass"
