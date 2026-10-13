"""Shared test fixtures and helpers for fingerprint-check tests."""

from typing import Iterable

import pytest
from starlette.requests import Request


def build_fake_request(
    headers: Iterable[tuple[str, str]] | dict[str, str] | None = None,
    http_version: str = "2.0",
    method: str = "GET",
    path: str = "/report",
) -> Request:
    """Construct a genuine Starlette Request instance with explicit headers and http_version."""
    if headers is None:
        raw_headers = []
    elif isinstance(headers, dict):
        raw_headers = [(k.encode("latin-1"), v.encode("latin-1")) for k, v in headers.items()]
    else:
        raw_headers = [(k.encode("latin-1"), v.encode("latin-1")) for k, v in headers]

    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "headers": raw_headers,
        "http_version": http_version,
    }
    return Request(scope=scope)


@pytest.fixture
def make_request():
    """Factory fixture for fake requests."""
    return build_fake_request
