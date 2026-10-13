"""Check: window.chrome presence in Chrome-based UAs."""

from typing import Any

from starlette.requests import Request

from fingerprint_check.checks.base import BaseCheck, CheckResult


class WindowChromeCheck(BaseCheck):
    """Verifies that window.chrome is present and properly structured in Chromium browsers."""

    @property
    def name(self) -> str:
        return "window.chrome Presence"

    def run(self, request: Request, client_data: dict[str, Any] | None = None) -> CheckResult:
        if not client_data:
            return CheckResult(
                name=self.name,
                status="warn",
                explanation="No client-side JavaScript execution data was received to inspect window.chrome.",
                fix="Load /test in a browser runtime to evaluate window.chrome properties.",
            )

        ua = (client_data.get("js_user_agent") or request.headers.get("user-agent", "")).lower()
        has_window_chrome = client_data.get("has_window_chrome", False)
        has_chrome_runtime = client_data.get("has_chrome_runtime", False)

        is_firefox = "firefox/" in ua
        is_safari_only = "safari/" in ua and "chrome/" not in ua and "chromium/" not in ua
        is_chromium = (
            any(t in ua for t in ("chrome/", "chromium/", "edg/", "headlesschrome"))
            and not is_firefox
        )

        if is_chromium:
            if not has_window_chrome:
                return CheckResult(
                    name=self.name,
                    status="fail",
                    explanation=(
                        "The User-Agent claims to be a Chromium-based browser, but 'window.chrome' is completely "
                        "absent from the JavaScript runtime. Genuine Google Chrome and Edge always expose the 'window.chrome' "
                        "object. Headless Chromium, Puppeteer, and Playwright without stealth omit this by default."
                    ),
                    fix=(
                        "Launch Chromium with stealth plugins or inject 'window.chrome = { runtime: {} }' "
                        "before any page scripts execute."
                    ),
                )

            if not has_chrome_runtime:
                return CheckResult(
                    name=self.name,
                    status="warn",
                    explanation=(
                        "'window.chrome' is defined, but standard sub-properties like 'window.chrome.runtime' are missing. "
                        "Sophisticated anti-bot engines probe nested chrome properties to expose naive mocks."
                    ),
                    fix="Ensure 'window.chrome.runtime', 'window.chrome.csi', and 'window.chrome.loadTimes' are accurately emulated.",
                )

            return CheckResult(
                name=self.name,
                status="pass",
                explanation="'window.chrome' is present and structured properly for a Chromium browser.",
                fix="None needed. Chrome runtime object looks authentic.",
            )

        if is_firefox or is_safari_only:
            browser_name = "Firefox" if is_firefox else "Safari"
            if has_window_chrome:
                return CheckResult(
                    name=self.name,
                    status="fail",
                    explanation=(
                        f"The User-Agent claims to be {browser_name}, but 'window.chrome' is defined in the JavaScript runtime. "
                        f"{browser_name} does not define 'window.chrome'. This contradiction reveals naive header or runtime spoofing."
                    ),
                    fix=f"Do not inject 'window.chrome' when emulating {browser_name}.",
                )
            return CheckResult(
                name=self.name,
                status="pass",
                explanation=f"'window.chrome' is absent, as expected for {browser_name}.",
                fix="None needed.",
            )

        return CheckResult(
            name=self.name,
            status="pass",
            explanation="Runtime window properties are consistent with declared browser identity.",
            fix="None needed.",
        )
