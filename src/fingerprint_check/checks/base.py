"""Base models and abstract class for fingerprint-check checks."""

from abc import ABC, abstractmethod
from typing import Any, Literal

from pydantic import BaseModel, Field
from starlette.requests import Request

CheckStatus = Literal["pass", "warn", "fail"]


class CheckResult(BaseModel):
    """Result of an individual bot detection check."""

    name: str = Field(description="Name of the check")
    status: CheckStatus = Field(description="Result status: pass, warn, or fail")
    explanation: str = Field(description="Why this check matters for bot detection")
    fix: str = Field(description="Actionable suggestion to fix or avoid detection")
    fix_suggestion: str = Field(default="", description="Alias for fix suggestion")

    def model_post_init(self, __context: object) -> None:
        """Ensure fix_suggestion matches fix if not explicitly set."""
        if not self.fix_suggestion:
            self.fix_suggestion = self.fix


class BaseCheck(ABC):
    """Abstract base class for all bot detection checks."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Display name / identifier for this check."""
        ...

    @abstractmethod
    def run(self, request: Request, client_data: dict[str, Any] | None = None) -> CheckResult:
        """Run the check against the incoming HTTP request and optional client JS data.

        Args:
            request: The Starlette/FastAPI request object.
            client_data: Optional dictionary containing client-side JavaScript metrics.

        Returns:
            CheckResult containing name, status, explanation, and fix suggestion.
        """
        ...
