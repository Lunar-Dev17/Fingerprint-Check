"""End-to-end test using Playwright headless Chromium against the /test page."""

import socket
import threading
import time

import pytest
import uvicorn
from playwright.sync_api import sync_playwright

from fingerprint_check.main import app


def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def server_url():
    port = get_free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Wait for server to start
    time.sleep(1)
    yield f"http://127.0.0.1:{port}"

    server.should_exit = True
    thread.join(timeout=2)


def test_plain_headless_chromium_is_flagged(server_url: str):
    """Ensure plain headless Chromium visiting /test gets flagged by client and server checks."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(f"{server_url}/test")
        page.wait_for_selector("#report-summary", state="visible", timeout=15000)

        report = page.evaluate("() => window.__report__")
        browser.close()

    assert report is not None
    summary = report["summary"]
    checks = report["checks"]

    # Merged report should contain 10 checks
    assert summary["total"] == 10
    assert summary["failed"] > 0

    check_map = {c["name"]: c for c in checks}

    # In plain headless Chromium without stealth, navigator.webdriver is true
    assert check_map["navigator.webdriver Flag"]["status"] == "fail"

    # window.chrome is missing or incomplete
    assert check_map["window.chrome Presence"]["status"] in ("fail", "warn")

    # Plugins are typically empty or missing
    assert check_map["navigator.plugins & languages"]["status"] in ("fail", "warn")
