# Contributing to fingerprint-check

Thank you for your interest in contributing to **fingerprint-check**! We welcome bug fixes, documentation improvements, and new bot detection checks from the web scraping and security communities.

---

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Git

### Initial Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/fingerprint-check.git
   cd fingerprint-check
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # On macOS / Linux:
   python3 -m venv .venv
   source .venv/bin/activate

   # On Windows (PowerShell):
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. **Install the package in editable mode with development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install Playwright browsers for end-to-end testing**:
   ```bash
   playwright install chromium
   ```

---

## Adding a New Check

`fingerprint-check` uses a modular plugin architecture. Every check inherits from `BaseCheck` in [`src/fingerprint_check/checks/base.py`](src/fingerprint_check/checks/base.py).

### Step 1: Create the Check Module

Add a new file in `src/fingerprint_check/checks/<your_check_name>.py`:

```python
"""Check: Example check description."""

from typing import Any
from starlette.requests import Request
from fingerprint_check.checks.base import BaseCheck, CheckResult


class MyCustomCheck(BaseCheck):
    """Detects suspicious or anomalous client behavior."""

    @property
    def name(self) -> str:
        return "Custom Anomaly Detection Check"

    def run(self, request: Request, client_data: dict[str, Any] | None = None) -> CheckResult:
        # 1. Analyze request headers or client_data
        header_val = request.headers.get("x-custom-header")

        # 2. Evaluate condition
        if not header_val:
            return CheckResult(
                name=self.name,
                status="fail",  # or "warn" or "pass"
                explanation=(
                    "The client omitted 'X-Custom-Header'. Anti-bot systems monitor this header "
                    "to identify automated clients."
                ),
                fix="Ensure your scraper sets 'X-Custom-Header: value'.",
            )

        return CheckResult(
            name=self.name,
            status="pass",
            explanation="Header is present and well-formed.",
            fix="None needed.",
        )
```

### Step 2: Register the Check

Add your new check to [`src/fingerprint_check/checks/__init__.py`](src/fingerprint_check/checks/__init__.py):

```python
from fingerprint_check.checks.my_custom_check import MyCustomCheck

# If it evaluates incoming HTTP headers / ASGI scope:
SERVER_CHECKS.append(MyCustomCheck())

# If it evaluates browser JavaScript runtime data:
CLIENT_CHECKS.append(MyCustomCheck())
```

### Step 3: Write Unit Tests

Add a dedicated test file under `tests/test_my_custom_check.py`:

```python
from fingerprint_check.checks.my_custom_check import MyCustomCheck
from tests.conftest import build_fake_request


def test_missing_header_fails():
    check = MyCustomCheck()
    req = build_fake_request(headers=[])
    result = check.run(req)

    assert result.status == "fail"
    assert result.fix != ""


def test_valid_header_passes():
    check = MyCustomCheck()
    req = build_fake_request(headers=[("x-custom-header", "valid")])
    result = check.run(req)

    assert result.status == "pass"
```

---

## Code Quality & Testing

Before submitting a pull request, ensure your code passes both the linter and test suite:

1. **Run the linter**:
   ```bash
   ruff check .
   ```
   To automatically format and resolve fixable issues:
   ```bash
   ruff check --fix .
   ```

2. **Run the test suite**:
   ```bash
   pytest -v
   ```

3. **Run the Playwright headless demonstration**:
   ```bash
   python examples/run_headless_check.py
   ```

---

## Pull Request Guidelines

- Keep pull requests focused on a single feature, check, or bug fix.
- Ensure new checks include meaningful `explanation` and `fix` strings.
- Provide unit tests verifying both `pass`, `warn`, and `fail` paths.
- Ensure CI tests pass across all supported Python versions (3.11, 3.12, 3.13).
