"""Check: navigator.webdriver presence."""

from typing import Any

from starlette.requests import Request

from fingerprint_check.checks.base import BaseCheck, CheckResult


class WebdriverCheck(BaseCheck):
    """Detects whether navigator.webdriver is set by browser automation frameworks."""

    @property
    def name(self) -> str:
        return "navigator.webdriver Flag"

    def run(self, request: Request, client_data: dict[str, Any] | None = None) -> CheckResult:
        if not client_data:
            return CheckResult(
                name=self.name,
                status="warn",
                explanation="No client-side JavaScript execution data was received to evaluate navigator.webdriver.",
                fix="Execute JavaScript in a real or emulated browser to evaluate client properties.",
            )

        webdriver = client_data.get("webdriver")
        webdriver_raw = client_data.get("webdriver_raw")

        is_flagged = (
            webdriver is True
            or webdriver_raw is True
            or str(webdriver).strip().lower() in ("true", "1")
            or str(webdriver_raw).strip().lower() in ("true", "1")
        )

        if is_flagged:
            return CheckResult(
                name=self.name,
                status="fail",
                explanation=(
                    "The client runtime has 'navigator.webdriver = true'. "
                    "The W3C WebDriver specification mandates that automation tools (Playwright, Puppeteer, Selenium) "
                    "expose this flag. Major anti-bot systems (Cloudflare, Akamai, DataDome, Kasada) treat this "
                    "as a 100% conclusive bot indicator."
                ),
                fix=(
                    "In Playwright / Puppeteer, launch with the argument '--disable-blink-features=AutomationControlled', "
                    "or integrate an anti-detection stealth plugin (such as 'playwright-stealth')."
                ),
            )

        return CheckResult(
            name=self.name,
            status="pass",
            explanation="'navigator.webdriver' is false or undefined, consistent with human browser sessions.",
            fix="None needed. Keep automation flags disabled.",
        )
