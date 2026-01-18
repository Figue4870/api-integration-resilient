![CI](https://github.com/Figue4870/api-integration-resilient/actions/workflows/ci.yml/badge.svg?branch=main)


# API Integration Resilient Client (Retries + Rate Limit + Pagination) + QA

A small portfolio project that demonstrates a production-style API integration:
- **Retries** with exponential backoff (handles network errors + 5xx)
- **Rate-limit handling** (handles `429` + `Retry-After` and rate limit windows)
- **Pagination** via RFC5988 `Link` header (`rel="next"`)
- **QA** with mocked tests (no external network dependency)
- Includes a **broken/naive** version vs a **fixed/resilient** version

## Why this exists
Many real APIs fail in production due to:
- transient 5xx errors
- rate limiting
- hidden pagination requirements
- fragile clients without tests

This repo shows a minimal but robust client + tests.

---

## Project structure
broken/ # naive implementation that fails on edge cases
fixed/ # resilient client + pagination + CLI demo
tests/ # pytest tests with mocked HTTP


---

## Quickstart (local)
### 1 Create venv
```bash
python -m venv .venv
```
### Activate venv

windows (powershell)
```bash
.\.venv\Scripts\Activate.ps1
```
Mac/Linux
```bash
source .venv/bin/activate
```
Install dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```
Run tests
```bash
pytest -q
```

### Demo (real API)
Fetch GitHub issues across multiple pages (limited by max_pages):

```bash
python -m fixed.cli
```

Optional: add a GitHub token to reduce rate-limit issues:

```bash
# Windows PowerShell:
$env:GITHUB_TOKEN="YOUR_TOKEN_HERE"

# Mac/Linux:
export GITHUB_TOKEN="YOUR_TOKEN_HERE"

```

## What "broken" does wrong

- Only fetches the first page
- No retries for 5xx
- No rate-limit handling
- No controlled error behavior

## What "fixed" does better
- Retries for transient errors (5xx, timeouts)
- Handles 429 using Retry-After
- Detects rate windows via X-RateLimit-Remaining / X-RateLimit-Reset
- Supports pagination via Link header
- Includes tests that simulate: pagination, 5xx, 429

## Notes
- Tests use mocked responses so they are fast and deterministic.
- No secrets are committed.
