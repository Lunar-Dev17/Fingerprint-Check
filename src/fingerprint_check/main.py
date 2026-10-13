"""Main entry point for fingerprint-check FastAPI application."""

from typing import Any

from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.requests import Request

from fingerprint_check.checks import run_all_checks
from fingerprint_check.models import ReportResponse, ReportSummary
from fingerprint_check.report_template import render_report_html
from fingerprint_check.test_page import TEST_PAGE_HTML

app = FastAPI(
    title="fingerprint-check",
    version="0.1.0",
    description="A self-hosted tool that tells web scraper developers what makes their scraper or headless browser look like a bot.",
)


def should_render_html(request: Request) -> bool:
    """Determine whether to render HTML or return JSON based on query param and Accept header."""
    fmt = request.query_params.get("format", "").lower()
    if fmt == "html":
        return True
    if fmt == "json":
        return False

    accept = request.headers.get("accept", "")
    if "application/json" in accept and "text/html" not in accept:
        return False
    if "text/html" in accept:
        return True
    return False


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/test", response_class=HTMLResponse)
def test_page() -> HTMLResponse:
    """Interactive client-side JavaScript evaluation page."""
    return HTMLResponse(content=TEST_PAGE_HTML)


@app.get("/report")
@app.post("/report")
async def report(request: Request) -> Response:
    """Analyze incoming request and optional JavaScript client metrics and return a bot report.

    Renders clean, dependency-free HTML when visited in a browser (or Accept: text/html).
    Returns JSON when Accept: application/json (or requested via format=json / standard API client).
    """
    client_data: dict[str, Any] | None = None
    if request.method == "POST":
        try:
            body = await request.json()
            if isinstance(body, dict):
                client_data = body
        except Exception:
            pass

    results = run_all_checks(request, client_data=client_data)
    passed = sum(1 for r in results if r.status == "pass")
    warned = sum(1 for r in results if r.status == "warn")
    failed = sum(1 for r in results if r.status == "fail")

    report_data = ReportResponse(
        summary=ReportSummary(
            total=len(results),
            passed=passed,
            warned=warned,
            failed=failed,
        ),
        checks=results,
    )

    if should_render_html(request):
        return HTMLResponse(content=render_report_html(report_data))

    return JSONResponse(content=report_data.model_dump())
