"""Check 5: HTTP version in use."""

from typing import Any

from starlette.requests import Request

from fingerprint_check.checks.base import BaseCheck, CheckResult


class HttpVersionCheck(BaseCheck):
    """Verifies that the request uses modern HTTP protocols (HTTP/2 or HTTP/3)."""

    @property
    def name(self) -> str:
        return "HTTP Version"

    def run(self, request: Request, client_data: dict[str, Any] | None = None) -> CheckResult:
        raw_version = str(request.scope.get("http_version", "1.1")).strip().lower()

        # Handle variants like "http/2", "2.0", "2", "3"
        version = raw_version.replace("http/", "").strip()

        if version in ("1.0", "0.9"):
            return CheckResult(
                name=self.name,
                status="fail",
                explanation=(
                    f"Request arrived using HTTP/{version}. Modern browsers have not used HTTP/1.0 by default "
                    "in decades. This is an immediate, high-confidence signature of automated scraping tools."
                ),
                fix="Configure your client or scraper to use HTTP/1.1 or preferably HTTP/2.",
            )

        if version == "1.1":
            return CheckResult(
                name=self.name,
                status="warn",
                explanation=(
                    "Request arrived using HTTP/1.1. While RFC-compliant, modern web browsers overwhelmingly "
                    "negotiate HTTP/2 or HTTP/3 over TLS via ALPN. Many standard scraping libraries (like Python requests) "
                    "only support HTTP/1.1, making this a common weighting factor in bot detection heuristics."
                ),
                fix=(
                    "Use an HTTP client that negotiates HTTP/2 via ALPN (e.g. `httpx` with `http2=True`, "
                    "`curl --http2`, or `curl-impersonate`)."
                ),
            )

        if version in ("2", "2.0", "3", "3.0"):
            return CheckResult(
                name=self.name,
                status="pass",
                explanation=(
                    f"Request arrived using HTTP/{version}. This matches the protocol behavior of modern web browsers."
                ),
                fix="None needed. HTTP protocol version is consistent with modern browser standards.",
            )

        # Fallback for unrecognized version strings
        return CheckResult(
            name=self.name,
            status="warn",
            explanation=f"Unusual HTTP version detected: '{raw_version}'.",
            fix="Ensure client negotiates standard HTTP/2 or HTTP/1.1.",
        )
