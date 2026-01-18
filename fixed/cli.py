import os
from typing import Any, Dict, Optional

import requests

from fixed.client import ResilientApiClient
from fixed.pagination import parse_link_header, extract_items


def fetch_all_pages_issues(
    client: ResilientApiClient,
    owner: str,
    repo: str,
    per_page: int = 50,
    max_pages: int = 5,
) -> int:
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    params: Dict[str, Any] = {"per_page": per_page, "state": "open"}

    total = 0
    page_count = 0

    while url is not None and page_count < max_pages:
        payload = client.request_json("GET", url, params=params)
        items, _meta = extract_items(payload)
        total += len(items)
        page_count += 1

        # En la siguiente request a GitHub, params ya vienen embebidos en el Link next,
        # así que params debe ser None
        params = None

        # IMPORTANTE: para leer headers, hacemos una request “normal” con session
        # porque request_json ya devuelve JSON. Para no complicarlo, repetimos pero HEAD.
        # GitHub no siempre soporta HEAD igual, así que hacemos GET mínimo.
        resp = client.session.get(url, params=None, headers=client.base_headers, timeout=client.timeout_seconds)
        link = resp.headers.get("Link")
        if link:
            links = parse_link_header(link)
            url = links.get("next")
        else:
            url = None

    return total


def build_headers() -> Dict[str, str]:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


if __name__ == "__main__":
    client = ResilientApiClient(base_headers=build_headers(), timeout_seconds=10.0)
    total = fetch_all_pages_issues(client, "psf", "requests", per_page=50, max_pages=3)
    print(f"Fetched issues across pages (up to max_pages=3): {total}")
