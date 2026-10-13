"""Check registry and runner for fingerprint-check."""

from typing import Any, Sequence

from starlette.requests import Request

from fingerprint_check.checks.base import BaseCheck, CheckResult, CheckStatus
from fingerprint_check.checks.client_hints import ClientHintsCheck
from fingerprint_check.checks.header_order import HeaderOrderCheck
from fingerprint_check.checks.http_version import HttpVersionCheck
from fingerprint_check.checks.missing_headers import MissingHeadersCheck
from fingerprint_check.checks.navigator_properties import NavigatorPropertiesCheck
from fingerprint_check.checks.screen_headless import ScreenHeadlessCheck
from fingerprint_check.checks.timezone_language import TimezoneLanguageCheck
from fingerprint_check.checks.user_agent import UserAgentCheck
from fingerprint_check.checks.webdriver import WebdriverCheck
from fingerprint_check.checks.window_chrome import WindowChromeCheck

# Server-side HTTP request checks
SERVER_CHECKS: list[BaseCheck] = [
    UserAgentCheck(),
    ClientHintsCheck(),
    HeaderOrderCheck(),
    MissingHeadersCheck(),
    HttpVersionCheck(),
]

# Client-side JavaScript evaluation checks
CLIENT_CHECKS: list[BaseCheck] = [
    WebdriverCheck(),
    NavigatorPropertiesCheck(),
    TimezoneLanguageCheck(),
    WindowChromeCheck(),
    ScreenHeadlessCheck(),
]

# All available checks combined
ALL_CHECKS: list[BaseCheck] = SERVER_CHECKS + CLIENT_CHECKS
DEFAULT_CHECKS: list[BaseCheck] = SERVER_CHECKS


def run_all_checks(
    request: Request,
    client_data: dict[str, Any] | None = None,
    checks: Sequence[BaseCheck] | None = None,
) -> list[CheckResult]:
    """Execute checks against the incoming HTTP request and optional client JS data.

    Args:
        request: The Starlette/FastAPI request object.
        client_data: Optional dictionary containing client-side JavaScript metrics.
        checks: Optional custom list of checks. If None, runs ALL_CHECKS when client_data is
            provided (merging server and client checks), or SERVER_CHECKS when client_data is None.

    Returns:
        List of CheckResult objects in order of execution.
    """
    if checks is None:
        active_checks = ALL_CHECKS if client_data is not None else SERVER_CHECKS
    else:
        active_checks = checks

    return [check.run(request, client_data=client_data) for check in active_checks]


__all__ = [
    "BaseCheck",
    "CheckResult",
    "CheckStatus",
    "SERVER_CHECKS",
    "CLIENT_CHECKS",
    "ALL_CHECKS",
    "DEFAULT_CHECKS",
    "run_all_checks",
    "UserAgentCheck",
    "ClientHintsCheck",
    "HeaderOrderCheck",
    "MissingHeadersCheck",
    "HttpVersionCheck",
    "WebdriverCheck",
    "NavigatorPropertiesCheck",
    "TimezoneLanguageCheck",
    "WindowChromeCheck",
    "ScreenHeadlessCheck",
]
