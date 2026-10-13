"""Check: navigator.plugins and navigator.languages properties."""

from typing import Any

from starlette.requests import Request

from fingerprint_check.checks.base import BaseCheck, CheckResult


class NavigatorPropertiesCheck(BaseCheck):
    """Evaluates navigator.plugins array and navigator.languages list."""

    @property
    def name(self) -> str:
        return "navigator.plugins & languages"

    def run(self, request: Request, client_data: dict[str, Any] | None = None) -> CheckResult:
        if not client_data:
            return CheckResult(
                name=self.name,
                status="warn",
                explanation="No client-side JavaScript execution data was received to inspect navigator properties.",
                fix="Visit /test inside a browser or browser automation tool.",
            )

        plugins_count = client_data.get("plugins_count", 0)
        languages = client_data.get("languages", [])

        # Check languages array
        if not languages or len(languages) == 0:
            return CheckResult(
                name=self.name,
                status="fail",
                explanation=(
                    "'navigator.languages' is empty or undefined. Real browsers always expose an array "
                    "of user locale preferences (e.g. ['en-US', 'en']). An empty languages array is a classic "
                    "footprint of unconfigured headless browsers."
                ),
                fix="Configure your browser context with a locale (e.g. in Playwright: locale='en-US').",
            )

        ua = (client_data.get("js_user_agent") or request.headers.get("user-agent", "")).lower()
        is_chromium = any(t in ua for t in ("chrome/", "chromium/", "edg/", "headlesschrome"))

        if plugins_count == 0:
            if is_chromium:
                return CheckResult(
                    name=self.name,
                    status="fail",
                    explanation=(
                        "'navigator.plugins' is empty (length 0) on a Chromium browser. "
                        "Genuine Google Chrome bundles default built-in plugins (such as PDF Viewer). "
                        "An empty PluginArray is one of the earliest and most reliable headless Chrome detection heuristics."
                    ),
                    fix=(
                        "Run Chromium with '--headless=new' or inject mock PluginArray objects matching authentic Chrome."
                    ),
                )
            return CheckResult(
                name=self.name,
                status="warn",
                explanation=(
                    "'navigator.plugins' has length 0. While modern browsers are reducing plugin exposure, "
                    "completely empty plugin arrays increase bot suspicion scores."
                ),
                fix="Ensure your browser context does not strip standard browser plugin interfaces.",
            )

        return CheckResult(
            name=self.name,
            status="pass",
            explanation=(
                f"'navigator.plugins' contains {plugins_count} plugin(s) and "
                f"'navigator.languages' contains {languages}, consistent with a legitimate user browser."
            ),
            fix="None needed. Plugins and language configurations appear authentic.",
        )
