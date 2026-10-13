"""Check 3: Header order compared to a real Chrome request."""

from typing import Any

from starlette.requests import Request

from fingerprint_check.checks.base import BaseCheck, CheckResult

# Canonical order of common headers emitted by desktop Google Chrome during navigation/fetch
CHROME_REFERENCE_ORDER = [
    "host",
    "connection",
    "sec-ch-ua",
    "sec-ch-ua-mobile",
    "sec-ch-ua-platform",
    "upgrade-insecure-requests",
    "user-agent",
    "accept",
    "sec-fetch-site",
    "sec-fetch-mode",
    "sec-fetch-user",
    "sec-fetch-dest",
    "referer",
    "accept-encoding",
    "accept-language",
    "cookie",
    "priority",
]


class HeaderOrderCheck(BaseCheck):
    """Compares the incoming request's header sequence against a genuine Chrome browser."""

    @property
    def name(self) -> str:
        return "Header Order (Chrome Comparison)"

    def _extract_header_order(self, request: Request) -> list[str]:
        raw_headers = request.scope.get("headers")
        if raw_headers is not None:
            return [name.decode("latin-1").lower() for name, _ in raw_headers]
        # Fallback if scope['headers'] is absent in a mock
        return [k.lower() for k in request.headers.keys()]

    def run(self, request: Request, client_data: dict[str, Any] | None = None) -> CheckResult:
        all_headers = self._extract_header_order(request)

        # Filter down to headers present in Chrome reference list
        filtered = [h for h in all_headers if h in CHROME_REFERENCE_ORDER]
        # Deduplicate while preserving order
        unique_headers = list(dict.fromkeys(filtered))

        # Check for alphabetical ordering (dead giveaway of sorting middlewares or libraries)
        if len(unique_headers) >= 4 and unique_headers == sorted(unique_headers):
            return CheckResult(
                name=self.name,
                status="fail",
                explanation=(
                    "The headers were received in strict alphabetical order. "
                    "Real browsers never send headers in alphabetical order. "
                    "This is an immediate fingerprint of automated HTTP clients, proxy middlewares, or header normalization."
                ),
                fix=(
                    "Do not sort headers alphabetically. Emit headers in the exact sequence "
                    "used by Chrome (Client Hints -> User-Agent -> Accept -> Sec-Fetch-* -> Accept-Encoding/Language)."
                ),
            )

        if len(unique_headers) < 3:
            return CheckResult(
                name=self.name,
                status="warn",
                explanation=(
                    f"Only {len(unique_headers)} standard browser headers were provided. "
                    "There are not enough headers to reliably verify browser-native ordering."
                ),
                fix="Include standard browser headers (Accept, Accept-Language, Accept-Encoding, Client Hints, Sec-Fetch-*).",
            )

        # Calculate concordance (pairwise agreement with Chrome reference order)
        concordant = 0
        total_pairs = 0
        ref_index = {h: i for i, h in enumerate(CHROME_REFERENCE_ORDER)}

        for i in range(len(unique_headers)):
            for j in range(i + 1, len(unique_headers)):
                h1, h2 = unique_headers[i], unique_headers[j]
                total_pairs += 1
                if ref_index[h1] < ref_index[h2]:
                    concordant += 1

        concordance = concordant / total_pairs if total_pairs > 0 else 0.0

        if concordance >= 0.80:
            return CheckResult(
                name=self.name,
                status="pass",
                explanation=(
                    f"Header ordering matches Chrome's native emission order "
                    f"({int(concordance * 100)}% concordance)."
                ),
                fix="None needed. Header sequence is consistent with a real Chrome browser.",
            )

        if concordance >= 0.50:
            return CheckResult(
                name=self.name,
                status="warn",
                explanation=(
                    f"Header ordering deviates noticeably from Chrome's native sequence "
                    f"({int(concordance * 100)}% concordance). "
                    "Anti-bot engines (like Cloudflare, Akamai, and DataDome) use passive header-order fingerprinting."
                ),
                fix=(
                    "Reorder your request headers to follow Chrome's standard layout "
                    "(e.g., host -> client hints -> user-agent -> accept -> sec-fetch-* -> accept-encoding -> accept-language)."
                ),
            )

        return CheckResult(
            name=self.name,
            status="fail",
            explanation=(
                f"Header ordering severely contradicts Chrome's native sequence "
                f"({int(concordance * 100)}% concordance). "
                "Passive fingerprinting filters flag this ordering as an artificial HTTP client."
            ),
            fix=(
                "Use an HTTP client that preserves exact header ordering (such as curl-impersonate or tls-client) "
                "configured to mirror Chrome's order."
            ),
        )
