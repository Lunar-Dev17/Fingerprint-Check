"""Tests for combined server & client-side report and /test endpoint."""

from fastapi.testclient import TestClient

from fingerprint_check.main import app

client = TestClient(app)


def test_test_page_serves_html():
    response = client.get("/test")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "fingerprint-check" in response.text
    assert "report-summary" in response.text
    assert "checks-container" in response.text
    assert "collectClientMetrics" in response.text


def test_report_endpoint_merges_server_and_client_checks():
    client_payload = {
        "webdriver": True,
        "plugins_count": 0,
        "languages": ["en-US"],
        "timezone": "UTC",
        "has_window_chrome": False,
        "has_chrome_runtime": False,
        "outer_width": 0,
        "outer_height": 0,
        "screen_width": 800,
        "screen_height": 600,
        "js_user_agent": "Mozilla/5.0 AppleWebKit/537.36 HeadlessChrome/124.0.0.0 Safari/537.36",
    }

    headers = {
        "user-agent": "Mozilla/5.0 AppleWebKit/537.36 HeadlessChrome/124.0.0.0 Safari/537.36",
        "accept-language": "en-US,en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
    }

    response = client.post("/report", json=client_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()

    # Total should be 10 (5 server checks + 5 client checks merged)
    assert data["summary"]["total"] == 10
    check_names = {c["name"] for c in data["checks"]}

    # Server checks
    assert "User-Agent Present and Plausible" in check_names
    assert "User-Agent vs Client Hints Consistency" in check_names
    assert "Header Order (Chrome Comparison)" in check_names
    assert "Missing Browser Headers" in check_names
    assert "HTTP Version" in check_names

    # Client checks
    assert "navigator.webdriver Flag" in check_names
    assert "navigator.plugins & languages" in check_names
    assert "Timezone vs Accept-Language Mismatch" in check_names
    assert "window.chrome Presence" in check_names
    assert "Headless Screen & Dimension Anomalies" in check_names

    # Headless flagged checks should fail
    check_map = {c["name"]: c for c in data["checks"]}
    assert check_map["navigator.webdriver Flag"]["status"] == "fail"
    assert check_map["Headless Screen & Dimension Anomalies"]["status"] == "fail"
    assert check_map["window.chrome Presence"]["status"] == "fail"
