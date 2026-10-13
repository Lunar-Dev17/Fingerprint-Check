"""Integration tests for the /report endpoint with JSON and HTML content negotiation."""

from fastapi.testclient import TestClient

from fingerprint_check.main import app

client = TestClient(app)


def test_report_endpoint_get_structure_json():
    # Explicit or default Accept returns JSON
    response = client.get("/report", headers={"Accept": "application/json"})
    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", "")

    data = response.json()
    assert "summary" in data
    assert "checks" in data

    summary = data["summary"]
    assert "total" in summary
    assert "passed" in summary
    assert "warned" in summary
    assert "failed" in summary
    assert summary["total"] == len(data["checks"])
    assert summary["passed"] + summary["warned"] + summary["failed"] == summary["total"]

    for check in data["checks"]:
        assert "name" in check
        assert check["status"] in ("pass", "warn", "fail")
        assert "explanation" in check
        assert "fix" in check
        assert "fix_suggestion" in check


def test_report_endpoint_renders_html_for_browser():
    # Browser navigation sends Accept with text/html
    browser_accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    response = client.get("/report", headers={"Accept": browser_accept})

    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")

    html_content = response.text
    # Verifies score card
    assert "score-card" in html_content
    assert "score-val" in html_content
    assert "/ 100" in html_content

    # Verifies color-coded pass/warn/fail pills and badges
    assert "pill-pass" in html_content
    assert "pill-warn" in html_content
    assert "pill-fail" in html_content
    assert "status-badge" in html_content

    # Verifies expandable explanations (<details> and <summary>)
    assert "<details" in html_content
    assert "<summary" in html_content
    assert "Why it matters" in html_content
    assert "Remediation Suggestion" in html_content

    # Verifies minimal dark theme
    assert "#0d1117" in html_content


def test_report_endpoint_format_query_param():
    # ?format=html override
    resp_html = client.get("/report?format=html")
    assert resp_html.status_code == 200
    assert "text/html" in resp_html.headers.get("content-type", "")
    assert "<details" in resp_html.text

    # ?format=json override
    resp_json = client.get("/report?format=json")
    assert resp_json.status_code == 200
    assert "application/json" in resp_json.headers.get("content-type", "")
    assert "summary" in resp_json.json()


def test_report_endpoint_post_supported():
    response = client.post("/report")
    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["total"] >= 5


def test_report_with_browser_headers():
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "accept-language": "en-US,en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "Accept": "application/json",
    }
    response = client.get("/report", headers=headers)
    assert response.status_code == 200
    data = response.json()

    check_map = {c["name"]: c for c in data["checks"]}
    assert check_map["User-Agent Present and Plausible"]["status"] == "pass"
    assert check_map["User-Agent vs Client Hints Consistency"]["status"] == "pass"
    assert check_map["Missing Browser Headers"]["status"] == "pass"
