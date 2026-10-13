"""Check 4: Missing headers that real browsers always send."""

from typing import Any

from starlette.requests import Request

from fingerprint_check.checks.base import BaseCheck, CheckResult

# Headers that modern browsers always send on navigations and fetches
CRITICAL_BROWSER_HEADERS = [
    "accept-language",
    "accept-encoding",
]

SEC_FETCH_HEADERS = [
    "sec-fetch-dest",
    "sec-fetch-mode",
    "sec-fetch-site",
]


class MissingHeadersCheck(BaseCheck):
    """Checks for headers that real web browsers consistently include."""

    @property
    def name(self) -> str:
        return "Missing Browser Headers"

    def run(self, request: Request, client_data: dict[str, Any] | None = None) -> CheckResult:
        missing_critical = [
            h for h in CRITICAL_BROWSER_HEADERS
            if not request.headers.get(h, "").strip()
        ]
        missing_sec_fetch = [
            h for h in SEC_FETCH_HEADERS
            if not request.headers.get(h, "").strip()
        ]

        if missing_critical:
            missing_names = ", ".join(f"'{h}'" for h in missing_critical)
            return CheckResult(
                name=self.name,
                status="fail",
                explanation=(
                    f"Critical browser header(s) missing: {missing_names}. "
                    "Genuine browsers always negotiate content language and compression algorithms. "
                    "Requests lacking Accept-Language or Accept-Encoding are flagged by almost every anti-bot WAF."
                ),
                fix=(
                    "Add 'Accept-Language' (e.g. 'en-US,en;q=0.9') and "
                    "'Accept-Encoding' (e.g. 'gzip, deflate, br, zstd') headers to your client."
                ),
            )

        if missing_sec_fetch:
            missing_fetch_names = ", ".join(f"'{h}'" for h in missing_sec_fetch)
            return CheckResult(
                name=self.name,
                status="warn",
                explanation=(
                    f"Metadata Sec-Fetch headers missing: {missing_fetch_names}. "
                    "Modern browsers (Chrome, Edge, Firefox, Safari) send Sec-Fetch metadata on all subresource and document requests. "
                    "Absence of Sec-Fetch headers is a strong heuristic for non-browser HTTP clients."
                ),
                fix=(
                    "Include 'Sec-Fetch-Site: cross-site|same-origin|none', "
                    "'Sec-Fetch-Mode: navigate|cors', and 'Sec-Fetch-Dest: document|empty'."
                ),
            )

        return CheckResult(
            name=self.name,
            status="pass",
            explanation=(
                "All standard browser headers (Accept-Language, Accept-Encoding, and Sec-Fetch-*) are present."
            ),
            fix="None needed. Headers match expectations for a standard browser client.",
        )
