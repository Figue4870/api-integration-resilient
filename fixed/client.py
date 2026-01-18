import time
from typing import Any, Dict, Optional

import requests


class ResilientApiClient:
    def __init__(
        self,
        base_headers: Optional[Dict[str, str]] = None,
        timeout_seconds: float = 10.0,
        max_retries: int = 5,
        base_backoff_seconds: float = 0.5,
        max_backoff_seconds: float = 8.0,
        max_rate_limit_sleep_seconds: float = 30.0,
    ):
        self.session = requests.Session()
        self.base_headers = base_headers or {}
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.base_backoff_seconds = base_backoff_seconds
        self.max_backoff_seconds = max_backoff_seconds
        self.max_rate_limit_sleep_seconds = max_rate_limit_sleep_seconds

    def request_json(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        all_headers = dict(self.base_headers)
        if headers:
            all_headers.update(headers)

        attempt = 0
        while attempt <= self.max_retries:
            try:
                resp = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    headers=all_headers,
                    timeout=self.timeout_seconds,
                )

                if self._should_wait_for_rate_limit(resp):
                    self._sleep_for_rate_limit(resp)
                    attempt += 1
                    continue

                if self._is_retryable_status(resp.status_code):
                    wait_s = self._compute_backoff_seconds(attempt, resp)
                    time.sleep(wait_s)
                    attempt += 1
                    continue

                resp.raise_for_status()
                return resp.json()

            except (requests.Timeout, requests.ConnectionError):
                if attempt >= self.max_retries:
                    raise
                wait_s = self._compute_backoff_seconds(attempt, None)
                time.sleep(wait_s)
                attempt += 1

        raise RuntimeError("Unexpected: exceeded retries loop without returning")

    def _is_retryable_status(self, status_code: int) -> bool:
        return status_code in (429, 500, 502, 503, 504)

    def _compute_backoff_seconds(self, attempt: int, resp: Optional[requests.Response]) -> float:
        # Si la API manda Retry-After, lo respetamos (muy típico con 429)
        if resp is not None:
            ra = resp.headers.get("Retry-After")
            if ra is not None:
                try:
                    ra_s = float(ra)
                    return min(max(ra_s, 0.0), self.max_backoff_seconds)
                except ValueError:
                    pass

        # Backoff exponencial simple
        wait_s = self.base_backoff_seconds * (2 ** attempt)
        if wait_s > self.max_backoff_seconds:
            wait_s = self.max_backoff_seconds
        return wait_s

    def _should_wait_for_rate_limit(self, resp: requests.Response) -> bool:
        if resp.status_code == 429:
            return True

        remaining = resp.headers.get("X-RateLimit-Remaining")
        reset = resp.headers.get("X-RateLimit-Reset")
        if remaining == "0" and reset is not None:
            return True

        return False

    def _sleep_for_rate_limit(self, resp: requests.Response) -> None:
        # 1) Si hay Retry-After, es lo más directo
        ra = resp.headers.get("Retry-After")
        if ra is not None:
            try:
                ra_s = float(ra)
                time.sleep(min(max(ra_s, 0.0), self.max_rate_limit_sleep_seconds))
                return
            except ValueError:
                pass

        # 2) Si hay ventana de reset (unix epoch)
        reset = resp.headers.get("X-RateLimit-Reset")
        if reset is not None:
            try:
                reset_ts = float(reset)
                now_ts = time.time()
                wait_s = reset_ts - now_ts + 1.0
                if wait_s < 0:
                    wait_s = 0.0
                time.sleep(min(wait_s, self.max_rate_limit_sleep_seconds))
                return
            except ValueError:
                pass

        # 3) Fallback: duerme un poquito
        time.sleep(1.0)
