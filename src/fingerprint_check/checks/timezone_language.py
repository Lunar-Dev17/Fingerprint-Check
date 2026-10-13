"""Check: Timezone vs Accept-Language mismatch."""

from typing import Any

from starlette.requests import Request

from fingerprint_check.checks.base import BaseCheck, CheckResult

# Language to expected timezone prefix mappings
LANGUAGE_REGION_MAP: dict[str, list[str]] = {
    "zh": ["asia/", "australia/", "america/"],  # Chinese (common in diaspora too)
    "ja": ["asia/tokyo", "asia/"],
    "ko": ["asia/seoul", "asia/"],
    "de": ["europe/berlin", "europe/vienna", "europe/zurich", "europe/"],
    "fr": ["europe/paris", "europe/brussels", "europe/zurich", "america/toronto", "america/montreal", "europe/", "america/", "africa/"],
    "ru": ["europe/moscow", "europe/", "asia/"],
    "pl": ["europe/warsaw", "europe/"],
    "it": ["europe/rome", "europe/"],
}


class TimezoneLanguageCheck(BaseCheck):
    """Detects discrepancies between client-side JavaScript timezone and HTTP Accept-Language."""

    @property
    def name(self) -> str:
        return "Timezone vs Accept-Language Mismatch"

    def run(self, request: Request, client_data: dict[str, Any] | None = None) -> CheckResult:
        if not client_data:
            return CheckResult(
                name=self.name,
                status="warn",
                explanation="No client-side JavaScript execution data was received to inspect the client timezone.",
                fix="Provide client runtime metrics by loading /test in a browser.",
            )

        timezone = str(client_data.get("timezone", "")).strip()
        accept_language = request.headers.get("accept-language", "").strip().lower()

        if not timezone:
            return CheckResult(
                name=self.name,
                status="warn",
                explanation="The client runtime failed to return a timezone from Intl.DateTimeFormat().",
                fix="Ensure your JavaScript execution environment supports Intl.DateTimeFormat.",
            )

        # Datacenter UTC indicator
        if timezone.upper() in ("UTC", "ETC/UTC", "ETC/GMT", "GMT"):
            return CheckResult(
                name=self.name,
                status="warn",
                explanation=(
                    f"Client timezone is set to '{timezone}'. Real residential and mobile browser users "
                    "virtually never use UTC as their system timezone. UTC is a telltale sign of cloud servers, "
                    "virtual machines, and datacenter proxy nodes (AWS, GCP, DigitalOcean)."
                ),
                fix="Set a realistic regional timezone (e.g. 'America/New_York' or 'Europe/London') matching your proxy location.",
            )

        if not accept_language:
            return CheckResult(
                name=self.name,
                status="warn",
                explanation="Client provided a timezone, but HTTP 'Accept-Language' header is missing.",
                fix="Send an 'Accept-Language' header that matches the client's timezone locale.",
            )

        # Parse primary language tags from Accept-Language
        langs = [part.split(";")[0].strip().lower() for part in accept_language.split(",") if part.strip()]
        primary_lang = langs[0].split("-")[0] if langs else ""
        tz_lower = timezone.lower()

        # Check for sharp contradictions (e.g. Japanese or German language with non-matching timezone)
        if primary_lang in LANGUAGE_REGION_MAP:
            valid_prefixes = LANGUAGE_REGION_MAP[primary_lang]
            matches = any(tz_lower.startswith(prefix) for prefix in valid_prefixes)
            if not matches:
                return CheckResult(
                    name=self.name,
                    status="warn",
                    explanation=(
                        f"Potential timezone and locale mismatch: primary Accept-Language is '{langs[0]}', "
                        f"but JavaScript runtime timezone is '{timezone}'. Anti-bot systems flag proxy users and scrapers "
                        "whose browser locales contradict their system timezone."
                    ),
                    fix=(
                        f"Align your client's timezone with the target locale (e.g. for '{langs[0]}', "
                        f"set timezone to one of: {', '.join(valid_prefixes[:2])})."
                    ),
                )

        return CheckResult(
            name=self.name,
            status="pass",
            explanation=f"Client timezone '{timezone}' and Accept-Language '{accept_language[:30]}' are consistent.",
            fix="None needed. Timezone and language preferences align.",
        )
