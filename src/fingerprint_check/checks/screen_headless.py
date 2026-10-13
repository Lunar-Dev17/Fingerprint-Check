"""Check: Headless indicators in UA and screen/window sizes."""

from typing import Any

from starlette.requests import Request

from fingerprint_check.checks.base import BaseCheck, CheckResult


class ScreenHeadlessCheck(BaseCheck):
    """Detects headless browser indicators in User-Agent and screen/window dimensions."""

    @property
    def name(self) -> str:
        return "Headless Screen & Dimension Anomalies"

    def run(self, request: Request, client_data: dict[str, Any] | None = None) -> CheckResult:
        if not client_data:
            return CheckResult(
                name=self.name,
                status="warn",
                explanation="No client-side JavaScript execution data was received to inspect screen and window dimensions.",
                fix="Load /test in a browser runtime to evaluate viewport and screen dimensions.",
            )

        # 1. User-Agent headless tokens in JavaScript navigator.userAgent
        js_ua = str(client_data.get("js_user_agent", "")).lower()
        server_ua = request.headers.get("user-agent", "").lower()
        combined_ua = f"{js_ua} {server_ua}"

        if "headlesschrome" in combined_ua or "headless" in combined_ua:
            return CheckResult(
                name=self.name,
                status="fail",
                explanation=(
                    "The User-Agent explicitly contains 'HeadlessChrome' or 'Headless'. "
                    "Unconfigured headless Chromium includes 'HeadlessChrome' in its default User-Agent string, "
                    "which is immediately blocked by virtually all bot mitigation rules."
                ),
                fix=(
                    "Launch Chromium with the newer headless mode ('--headless=new') or override the User-Agent "
                    "to remove the 'HeadlessChrome' substring."
                ),
            )

        # 2. Window outer dimensions
        outer_w = client_data.get("outer_width", 0)
        outer_h = client_data.get("outer_height", 0)

        if outer_w <= 0 and outer_h <= 0:
            return CheckResult(
                name=self.name,
                status="fail",
                explanation=(
                    "'window.outerWidth' and 'window.outerHeight' are both 0. "
                    "Real desktop browsers have an outer window frame with dimensions larger than 0. "
                    "Zero outer dimensions are a classic signature of headless browsers operating without a window manager."
                ),
                fix="Launch Chromium with '--headless=new' or configure a window size using '--window-size=1920,1080'.",
            )

        # 3. Viewport inner vs outer dimension anomaly
        inner_w = client_data.get("inner_width", 0)
        if outer_w > 0 and inner_w > outer_w:
            return CheckResult(
                name=self.name,
                status="warn",
                explanation=(
                    f"Dimension anomaly: 'window.innerWidth' ({inner_w}) exceeds 'window.outerWidth' ({outer_w}). "
                    "In physical browser windows, outer frame dimensions are always equal to or larger than inner viewport dimensions."
                ),
                fix="Ensure outer window size accommodates inner viewport dimensions.",
            )

        # 4. Screen dimensions
        screen_w = client_data.get("screen_width", 0)
        screen_h = client_data.get("screen_height", 0)

        if screen_w <= 0 or screen_h <= 0:
            return CheckResult(
                name=self.name,
                status="fail",
                explanation="'window.screen.width' or 'window.screen.height' is 0, indicating an unrendered virtual environment.",
                fix="Set a valid screen resolution on the virtual display or browser context.",
            )

        if screen_w == 800 and screen_h == 600:
            return CheckResult(
                name=self.name,
                status="warn",
                explanation=(
                    "Screen resolution is exactly 800x600. While valid, 800x600 is the default viewport size "
                    "of legacy headless Chromium and Puppeteer. Modern desktop users almost never browse at 800x600."
                ),
                fix="Set a realistic desktop resolution (e.g. 1920x1080, 1440x900, or 1366x768).",
            )

        # 5. Color depth
        color_depth = client_data.get("screen_color_depth", 24)
        if color_depth < 24:
            return CheckResult(
                name=self.name,
                status="warn",
                explanation=(
                    f"Screen color depth is {color_depth}-bit. Modern consumer displays operate at 24-bit or 32-bit color depth. "
                    "Sub-24-bit depths indicate legacy Xvfb virtual framebuffers or misconfigured headless drivers."
                ),
                fix="Configure your virtual framebuffer / browser to 24-bit color depth (e.g. 'xvfb-run -s \"-screen 0 1920x1080x24\"').",
            )

        return CheckResult(
            name=self.name,
            status="pass",
            explanation=(
                f"Screen dimensions ({screen_w}x{screen_h}), outer window ({outer_w}x{outer_h}), "
                f"and color depth ({color_depth}-bit) are consistent with a real desktop browser display."
            ),
            fix="None needed. Screen metrics appear authentic.",
        )
