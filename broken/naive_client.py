import requests

def fetch_first_page_issues(owner: str, repo: str, per_page: int = 30) -> list:
    """
    NAIVE:
    - No maneja paginación (solo trae la primera página)
    - No maneja 429 (rate limit) ni 5xx con retries
    - No maneja errores de red
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    params = {"per_page": per_page, "state": "open"}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    issues = fetch_first_page_issues("psf", "requests", per_page=30)
    print(f"Fetched issues: {len(issues)} (ONLY FIRST PAGE)")
