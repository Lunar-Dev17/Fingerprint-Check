"""Check 1: User-Agent presence and plausibility."""

import re
from typing import Any

from starlette.requests import Request

from fingerprint_check.checks.base import BaseCheck, CheckResult

KNOWN_BOT_PATTERNS = [
    r"python-requests",
    r"requests/\d",
    r"aiohttp",
    r"httpx",
    r"scrapy",
    r"urllib",
    r"curl/\d",
    r"wget/\d",
    r"got/\d",
    r"axios",
    r"node-fetch",
    r"go-http-client",
    r"postmanruntime",
    r"postman",
    r"headlesschrome",
    r"phantomjs",
    r"puppeteer",
    r"playwright",
    r"selenium",
    r"webdriver",
    r"electron",
]


class UserAgentCheck(BaseCheck):
    """Verifies that the User-Agent header is present, realistic, and free of bot tokens."""

    @property
    def name(self) -> str:
        return "User-Agent Present and Plausible"

    def run(self, request: Request, client_data: dict[str, Any] | None = None) -> CheckResult:
        ua = request.headers.get("user-agent", "").strip()
        js_ua = str(client_data.get("js_user_agent", "")).strip() if client_data else ""

        if not ua and js_ua:
            ua = js_ua

        if not ua:
            return CheckResult(
                name=self.name,
                status="fail",
                explanation=(
                    "The User-Agent header is completely missing or empty. "
                    "All standard web browsers send a User-Agent identifying the client. "
                    "Missing this header is an immediate high-confidence bot indicator for WAFs."
                ),
                fix="Set a realistic browser User-Agent header (e.g. from an up-to-date Chrome, Firefox, or Safari).",
            )

        # Cross-check HTTP header against client JS navigator.userAgent
        if ua and js_ua and ua != js_ua:
            return CheckResult(
                name=self.name,
                status="fail",
                explanation=(
                    "User-Agent mismatch: HTTP wire header does not match client JavaScript navigator.userAgent. "
                    "Anti-bot systems compare the wire header against the DOM property to expose scrapers "
                    "that only spoof headers."
                ),
                fix="Synchronize the HTTP User-Agent header with JavaScript 'navigator.userAgent'.",
            )

        ua_lower = ua.lower()
        for pattern in KNOWN_BOT_PATTERNS:
            match = re.search(pattern, ua_lower)
            if match:
                token = match.group(0)
                return CheckResult(
                    name=self.name,
                    status="fail",
                    explanation=(
                        f"The User-Agent contains known automated tool/bot token '{token}'. "
                        "WAFs, CDNs, and anti-bot systems automatically flag or block requests with default library signatures."
                    ),
                    fix=(
                        "Replace the default scraper/library User-Agent with a modern browser User-Agent string, "
                        "and ensure headless browser flags (such as HeadlessChrome or Playwright) are masked or stripped."
                    ),
                )

        if not ua.startswith("Mozilla/5.0"):
            return CheckResult(
                name=self.name,
                status="warn",
                explanation=(
                    "The User-Agent does not start with the standard 'Mozilla/5.0' prefix used by virtually all modern browsers. "
                    "Non-standard formatting triggers heuristic bot scoring in anomaly detection systems."
                ),
                fix="Ensure your User-Agent starts with 'Mozilla/5.0' and adheres to standard browser formatting.",
            )

        if len(ua) < 30:
            return CheckResult(
                name=self.name,
                status="warn",
                explanation=(
                    f"The User-Agent is unusually short ({len(ua)} characters). "
                    "Modern browser User-Agents typically contain platform, engine, and version identifiers."
                ),
                fix="Use a complete, authentic User-Agent copied from a modern desktop or mobile browser.",
            )

        return CheckResult(
            name=self.name,
            status="pass",
            explanation="User-Agent is present, well-formed, and free of known automated bot tokens.",
            fix="None needed. Keep the User-Agent updated with current browser releases.",
        )
