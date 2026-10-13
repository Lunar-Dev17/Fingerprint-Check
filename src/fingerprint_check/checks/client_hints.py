"""Check 2: UA vs sec-ch-ua / sec-ch-ua-platform consistency."""

import re
from typing import Any

from starlette.requests import Request

from fingerprint_check.checks.base import BaseCheck, CheckResult


class ClientHintsCheck(BaseCheck):
    """Evaluates consistency between User-Agent and Client Hints (sec-ch-ua, sec-ch-ua-platform)."""

    @property
    def name(self) -> str:
        return "User-Agent vs Client Hints Consistency"

    def run(self, request: Request, client_data: dict[str, Any] | None = None) -> CheckResult:
        ua = request.headers.get("user-agent", "").strip()
        if not ua and client_data:
            ua = str(client_data.get("js_user_agent", "")).strip()

        sec_ch_ua = request.headers.get("sec-ch-ua")
        sec_ch_ua_platform = request.headers.get("sec-ch-ua-platform")
        sec_ch_ua_mobile = request.headers.get("sec-ch-ua-mobile")

        if not ua:
            return CheckResult(
                name=self.name,
                status="fail",
                explanation="Cannot verify Client Hints consistency without a User-Agent header.",
                fix="Send a valid User-Agent header alongside matching Client Hints.",
            )

        ua_lower = ua.lower()

        # Determine browser family
        is_firefox = "firefox/" in ua_lower
        is_safari_only = "safari/" in ua_lower and "chrome/" not in ua_lower and "chromium/" not in ua_lower
        is_chromium = (
            any(t in ua_lower for t in ("chrome/", "chromium/", "edg/", "headlesschrome"))
            and not is_firefox
        )

        has_any_client_hints = bool(sec_ch_ua or sec_ch_ua_platform or sec_ch_ua_mobile)

        # Case 1: Claims to be Chrome/Chromium/Edge, but sec-ch-ua is absent
        if is_chromium and not sec_ch_ua:
            return CheckResult(
                name=self.name,
                status="fail",
                explanation=(
                    "The User-Agent claims to be a modern Chromium browser, but 'sec-ch-ua' Client Hints are missing. "
                    "Modern Chromium browsers (version 89+) always send Client Hints. "
                    "This mismatch is a primary signature of scrapers spoofing only the User-Agent header in HTTP libraries."
                ),
                fix=(
                    "Add 'sec-ch-ua', 'sec-ch-ua-mobile', and 'sec-ch-ua-platform' headers matching your Chromium version, "
                    "or avoid overriding the User-Agent without updating client hints."
                ),
            )

        # Case 2: Claims to be Firefox or Safari, but any Client Hints were provided
        if (is_firefox or is_safari_only) and has_any_client_hints:
            browser_name = "Firefox" if is_firefox else "Safari"
            return CheckResult(
                name=self.name,
                status="fail",
                explanation=(
                    f"The User-Agent claims to be {browser_name}, but Chromium Client Hints "
                    f"were provided. {browser_name} does not send Client Hints. "
                    "Sending Chromium client hints with a non-Chromium User-Agent is an unmistakable spoofing anomaly."
                ),
                fix=f"Remove 'sec-ch-ua', 'sec-ch-ua-mobile', and 'sec-ch-ua-platform' headers when mimicking {browser_name}.",
            )

        # Case 3: Version consistency between User-Agent and sec-ch-ua
        if sec_ch_ua and is_chromium:
            ua_ver_match = re.search(r"(?:edg|headlesschrome|chromium|chrome)/(\d+)", ua_lower)
            if ua_ver_match:
                ua_major = ua_ver_match.group(1)
                brand_versions = re.findall(r'"([^"]+)";\s*v="?(\d+)"?', sec_ch_ua)
                for brand, ver in brand_versions:
                    brand_lower = brand.lower()
                    if ("chrome" in brand_lower or "chromium" in brand_lower or "edge" in brand_lower) and "not" not in brand_lower:
                        if ver != ua_major:
                            return CheckResult(
                                name=self.name,
                                status="fail",
                                explanation=(
                                    f"Version mismatch: User-Agent declares version {ua_major}, "
                                    f"but 'sec-ch-ua' brand '{brand}' declares version {ver}. "
                                    "Anti-bot platforms immediately flag version discrepancies between the User-Agent and Client Hints."
                                ),
                                fix=(
                                    f"Ensure the major version in your User-Agent matches the version declared in 'sec-ch-ua' "
                                    f"(expected brand version: {ua_major})."
                                ),
                            )

        # Case 4: Platform check if sec-ch-ua-platform is present
        if sec_ch_ua_platform is not None:
            clean_ch_platform = sec_ch_ua_platform.strip().strip('"').lower()

            ua_os: str | None = None
            if "windows" in ua_lower or "win64" in ua_lower or "wow64" in ua_lower:
                ua_os = "windows"
            elif "macintosh" in ua_lower or "mac os x" in ua_lower:
                ua_os = "macos"
            elif "cros" in ua_lower:
                ua_os = "chrome os"
            elif "android" in ua_lower:
                ua_os = "android"
            elif "iphone" in ua_lower or "ipad" in ua_lower:
                ua_os = "ios"
            elif "linux" in ua_lower:
                ua_os = "linux"

            if ua_os and clean_ch_platform:
                norm_ch = "macos" if clean_ch_platform in ("mac os x", "macos", "mac") else clean_ch_platform
                norm_ua = ua_os

                if norm_ch != norm_ua:
                    return CheckResult(
                        name=self.name,
                        status="fail",
                        explanation=(
                            f"Operating system mismatch: User-Agent indicates {ua_os.capitalize()} "
                            f"but 'sec-ch-ua-platform' specifies {sec_ch_ua_platform}. "
                            "Anti-bot platforms immediately identify conflicting OS claims as automated spoofing."
                        ),
                        fix=(
                            f"Align 'sec-ch-ua-platform' with the OS in your User-Agent "
                            f"(expected: \"{ua_os.capitalize() if ua_os != 'macos' else 'macOS'}\")."
                        ),
                    )

        # Case 5: Mobile flag check if sec-ch-ua-mobile is present
        if sec_ch_ua_mobile is not None:
            clean_mobile = sec_ch_ua_mobile.strip().strip('"')
            is_mobile_ua = any(token in ua_lower for token in ["mobile", "android", "iphone", "ipad"])

            if clean_mobile == "?1" and not is_mobile_ua:
                return CheckResult(
                    name=self.name,
                    status="warn",
                    explanation=(
                        "'sec-ch-ua-mobile' is set to '?1' (mobile), but the User-Agent reflects a desktop browser."
                    ),
                    fix="Set 'sec-ch-ua-mobile: ?0' for desktop user agents.",
                )
            if clean_mobile == "?0" and is_mobile_ua:
                return CheckResult(
                    name=self.name,
                    status="warn",
                    explanation=(
                        "'sec-ch-ua-mobile' is set to '?0' (desktop), but the User-Agent reflects a mobile browser."
                    ),
                    fix="Set 'sec-ch-ua-mobile: ?1' for mobile user agents.",
                )

        # Case 6: sec-ch-ua is present but sec-ch-ua-platform is missing
        if sec_ch_ua and not sec_ch_ua_platform:
            return CheckResult(
                name=self.name,
                status="warn",
                explanation=(
                    "'sec-ch-ua' is present, but 'sec-ch-ua-platform' is missing. "
                    "Standard Chromium requests send both headers together."
                ),
                fix="Include 'sec-ch-ua-platform' (e.g. '\"Windows\"') when sending 'sec-ch-ua'.",
            )

        return CheckResult(
            name=self.name,
            status="pass",
            explanation="User-Agent and Client Hints (sec-ch-ua, sec-ch-ua-platform) are mutually consistent.",
            fix="None needed. Keep User-Agent and Client Hints synchronized when rotating fingerprints.",
        )
