<div align="center">

# 🕵️ fingerprint-check

**A self-hosted diagnostic tool that tells web scraper and headless browser developers what makes their bots look like bots.**

[![CI](https://github.com/your-username/fingerprint-check/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/fingerprint-check/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 💡 What It Is

`fingerprint-check` is a self-hosted web service and Python framework designed for scraper developers, security researchers, and automation engineers. It inspects incoming HTTP requests, header sequences, and client-side JavaScript execution metrics to tell you **exactly which browser fingerprint signals and headless leaks are flagging your scraper**.

Every detection check returns:
- **`name`**: Descriptive check title
- **`status`**: `pass` | `warn` | `fail`
- **`explanation`**: Technical explanation of why modern anti-bot systems (Cloudflare, Akamai, DataDome, Kasada) flag the heuristic
- **`fix`**: Concrete remediation advice for Puppeteer, Playwright, curl, and Python HTTP clients

---

## 🎯 Why It Exists

Modern bot detection has evolved beyond naive IP rate limiting. Today, bot mitigation engines employ passive and active fingerprinting:
1. **Header Anomalies**: Automated libraries send headers alphabetically, omit standard compression/locale negotiation, or send Chrome User-Agents without Chromium Client Hints (`sec-ch-ua`).
2. **Headless Browser Leaks**: Out-of-the-box headless Chromium leaks `navigator.webdriver = true`, defines empty `navigator.plugins`, omits `window.chrome`, and reports `0x0` outer window dimensions.
3. **Environmental Mismatches**: Scrapers using residential proxies often forget to align browser timezones (`Intl.DateTimeFormat`) with the HTTP `Accept-Language` header.

Public fingerprint test sites often require third-party network access, lack actionable guidance, or fail to explain *how* to resolve the flag. `fingerprint-check` gives developers a **local, self-hosted testing ground** with clear fix suggestions for every failure.

---

## 📦 Installation

### Prerequisites

- Python 3.11+
- Virtual environment tool

### Setup

```bash
# Clone the repository
git clone https://github.com/your-username/fingerprint-check.git
cd fingerprint-check

# Create and activate a virtual environment
python -m venv .venv

# On Linux / macOS:
source .venv/bin/activate
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Install package and development dependencies
pip install -e ".[dev]"

# Install Playwright browser binaries
playwright install chromium
```

---

## 🚀 Usage

### 1. Start the Server

```bash
uvicorn fingerprint_check.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Available Endpoints

| Endpoint | Method | Format | Description |
|---|---|---|---|
| `/test` | `GET` | HTML | Interactive browser testing page. Collects JavaScript runtime metrics and displays visual check cards. |
| `/report` | `GET`, `POST` | HTML / JSON | Unified report endpoint. Returns interactive dark-theme HTML when opened in a browser, or JSON when requested with `Accept: application/json`. |
| `/health` | `GET` | JSON | Simple liveness health check (`{"status": "ok"}`). |

### 3. Usage Examples

#### Run Plain Headless Chromium Audit (Example Script)

We provide an automated demonstration script in [`examples/run_headless_check.py`](examples/run_headless_check.py) that launches default headless Chromium with Playwright and prints color-coded detection results:

```bash
python examples/run_headless_check.py
```

#### Inspect Headers with `curl` (JSON Response)

```bash
curl -H "Accept: application/json" http://localhost:8000/report
```

#### Inspect Headers in a Web Browser (HTML Report)

Visit `http://localhost:8000/report` directly in Chrome, Firefox, or Safari to see the minimal dark-theme report with overall score and expandable remediation cards.

#### Test a Scraper with Python `httpx`

```python
import httpx

# Test how anti-bot systems see your scraper client
response = httpx.get("http://localhost:8000/report")
report = response.json()

print(f"Total: {report['summary']['total']}")
for check in report["checks"]:
    if check["status"] != "pass":
        print(f"[{check['status'].upper()}] {check['name']}: {check['fix']}")
```

---

## 📊 Sample Report

### JSON Response (`/report`)

```json
{
  "summary": {
    "total": 10,
    "passed": 4,
    "warned": 2,
    "failed": 4
  },
  "checks": [
    {
      "name": "User-Agent Present and Plausible",
      "status": "fail",
      "explanation": "The User-Agent contains known automated tool/bot token 'headlesschrome'. WAFs, CDNs, and anti-bot systems automatically flag or block requests with default library signatures.",
      "fix": "Replace the default scraper/library User-Agent with a modern browser User-Agent string, and ensure headless browser flags (such as HeadlessChrome or Playwright) are masked or stripped.",
      "fix_suggestion": "Replace the default scraper/library User-Agent with a modern browser User-Agent string, and ensure headless browser flags (such as HeadlessChrome or Playwright) are masked or stripped."
    },
    {
      "name": "navigator.webdriver Flag",
      "status": "fail",
      "explanation": "The client runtime has 'navigator.webdriver = true'. The W3C WebDriver specification mandates that automation tools (Playwright, Puppeteer, Selenium) expose this flag. Major anti-bot systems treat this as a 100% conclusive bot indicator.",
      "fix": "In Playwright / Puppeteer, launch with the argument '--disable-blink-features=AutomationControlled', or integrate an anti-detection stealth plugin (such as 'playwright-stealth').",
      "fix_suggestion": "In Playwright / Puppeteer, launch with the argument '--disable-blink-features=AutomationControlled', or integrate an anti-detection stealth plugin (such as 'playwright-stealth')."
    },
    {
      "name": "window.chrome Presence",
      "status": "fail",
      "explanation": "The User-Agent claims to be a Chromium-based browser, but 'window.chrome' is completely absent from the JavaScript runtime. Genuine Google Chrome and Edge always expose the 'window.chrome' object. Headless Chromium omits this by default.",
      "fix": "Launch Chromium with stealth plugins or inject 'window.chrome = { runtime: {} }' before any page scripts execute.",
      "fix_suggestion": "Launch Chromium with stealth plugins or inject 'window.chrome = { runtime: {} }' before any page scripts execute."
    },
    {
      "name": "HTTP Version",
      "status": "warn",
      "explanation": "Request arrived using HTTP/1.1. While RFC-compliant, modern web browsers overwhelmingly negotiate HTTP/2 or HTTP/3 over TLS via ALPN.",
      "fix": "Use an HTTP client that negotiates HTTP/2 via ALPN (e.g. `httpx` with `http2=True` or `curl-impersonate`).",
      "fix_suggestion": "Use an HTTP client that negotiates HTTP/2 via ALPN (e.g. `httpx` with `http2=True` or `curl-impersonate`)."
    }
  ]
}
```

---

## 🛠️ Included Checks

| Check Name | Target | Flagged Conditions |
|---|---|---|
| **User-Agent Present & Plausible** | HTTP Header | Missing UA, bot tokens (`HeadlessChrome`, `requests/`, `curl`, `playwright`), malformed structure. |
| **UA vs Client Hints Consistency** | HTTP Headers | Chrome UA without `sec-ch-ua`, Firefox UA sending Chrome hints, OS mismatch (`Windows` vs `macOS`). |
| **Header Order (Chrome Comparison)** | Raw Wire Order | Alphabetical header sorting, scrambled sequence, inverted Chrome header orders. |
| **Missing Browser Headers** | HTTP Headers | Missing `Accept-Language`, missing `Accept-Encoding`, missing `Sec-Fetch-*` metadata. |
| **HTTP Version** | Protocol Scope | Obsolete `HTTP/1.0` (fail) or non-multiplexed `HTTP/1.1` (warn). |
| **`navigator.webdriver` Flag** | JS Runtime | `navigator.webdriver === true`. |
| **`navigator.plugins` & `languages`** | JS Runtime | Empty plugin array in Chromium, empty preferred language list. |
| **Timezone vs `Accept-Language`** | Cross-Check | Datacenter `UTC` timezone, mismatch between client timezone and language locale. |
| **`window.chrome` Presence** | JS Runtime | Missing `window.chrome` in Chromium, or presence in Firefox/Safari. |
| **Headless Screen & Dimension Anomalies** | JS Runtime | `outerWidth === 0 && outerHeight === 0`, default `800x600` viewport, low color depth. |

---

## ➕ Adding a New Check

Adding detection checks takes three quick steps:

1. **Create the check file** under `src/fingerprint_check/checks/my_check.py`:
   ```python
   from typing import Any
   from starlette.requests import Request
   from fingerprint_check.checks.base import BaseCheck, CheckResult

   class MyCheck(BaseCheck):
       @property
       def name(self) -> str:
           return "My Custom Heuristic Check"

       def run(self, request: Request, client_data: dict[str, Any] | None = None) -> CheckResult:
           if condition_fails:
               return CheckResult(
                   name=self.name,
                   status="fail",
                   explanation="Why anti-bot engines flag this condition.",
                   fix="How scraper developers can resolve it.",
               )
           return CheckResult(
               name=self.name,
               status="pass",
               explanation="Consistent with legitimate browsers.",
               fix="None needed.",
           )
   ```

2. **Register the check** in [`src/fingerprint_check/checks/__init__.py`](src/fingerprint_check/checks/__init__.py):
   ```python
   from fingerprint_check.checks.my_check import MyCheck

   SERVER_CHECKS.append(MyCheck())  # or CLIENT_CHECKS.append(MyCheck())
   ```

3. **Add unit tests** in `tests/test_my_check.py` and run `pytest -v`.

For full development details, consult the [Contributing Guide](CONTRIBUTING.md).

---

## 🗺️ Roadmap

- [ ] **TLS / JA3 / JA4 Fingerprinting**: Capture raw TLS Client Hello ciphers, extension order, elliptic curves, and signature algorithms to detect Python SSL / OpenSSL vs BoringSSL signatures.
- [ ] **Canvas 2D Noise & Hash Check**: Evaluate 2D canvas drawing geometry and text metrics rendering consistency.
- [ ] **WebGL Vendor & Renderer String Inspection**: Detect unmasked software renderers (`SwiftShader`, `llvmpipe`, `Mesa OffScreen`) vs native hardware GPUs (NVIDIA, Apple, Intel, AMD).
- [ ] **AudioContext Fingerprint**: Inspect Web Audio API frequency analysis synthesis to flag headless audio stubs.
- [ ] **Font Enumeration & System Font Consistency**: Detect missing system font discrepancies between declared OS and installed system typography.
- [ ] **HTTP/2 Frame & Window Fingerprinting**: Analyze Akamai-style H2 settings frame sequence and stream priority frames.

---

## 🧪 Testing & Linting

```bash
# Run Ruff lint check
ruff check .

# Run complete test suite (50+ tests)
pytest -v
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
