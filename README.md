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
