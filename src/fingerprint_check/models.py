"""Data models for report response."""

from pydantic import BaseModel, Field

from fingerprint_check.checks.base import CheckResult


class ReportSummary(BaseModel):
    """Aggregated summary of check statuses."""

    total: int = Field(description="Total number of checks executed")
    passed: int = Field(description="Count of checks that passed")
    warned: int = Field(description="Count of checks that yielded warnings")
    failed: int = Field(description="Count of checks that failed")


class ReportResponse(BaseModel):
    """Full bot fingerprint analysis report."""

    summary: ReportSummary
    checks: list[CheckResult]
