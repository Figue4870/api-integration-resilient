import responses
import pytest

from fixed.client import ResilientApiClient


@responses.activate
def test_retries_on_500_then_success():
    url = "https://example.com/data"
    responses.add(responses.GET, url, json={"error": "server"}, status=500)
    responses.add(responses.GET, url, json={"ok": True}, status=200)

    client = ResilientApiClient(max_retries=3, base_backoff_seconds=0.0, max_backoff_seconds=0.0)
    data = client.request_json("GET", url)
    assert data["ok"] is True


@responses.activate
def test_rate_limit_429_retry_after_then_success():
    url = "https://example.com/ratelimited"
    responses.add(
        responses.GET,
        url,
        json={"error": "rate limited"},
        status=429,
        headers={"Retry-After": "0"},
    )
    responses.add(responses.GET, url, json={"ok": True}, status=200)

    client = ResilientApiClient(max_retries=3, base_backoff_seconds=0.0, max_backoff_seconds=0.0, max_rate_limit_sleep_seconds=0.0)
    data = client.request_json("GET", url)
    assert data["ok"] is True


@responses.activate
def test_exhaust_retries_raises():
    url = "https://example.com/down"
    responses.add(responses.GET, url, json={"error": "server"}, status=503)
    responses.add(responses.GET, url, json={"error": "server"}, status=503)
    responses.add(responses.GET, url, json={"error": "server"}, status=503)

    client = ResilientApiClient(max_retries=2, base_backoff_seconds=0.0, max_backoff_seconds=0.0)
    with pytest.raises(Exception):
        client.request_json("GET", url)
