import os
from typing import Optional

import httpx


def fetch_github_file(repo: str, path: str) -> Optional[str]:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return None
    url = f"https://api.github.com/repos/Works-by-Worrell/{repo}/contents/{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.raw",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    with httpx.Client() as client:
        try:
            resp = client.get(url, headers=headers)
            if resp.status_code == 200:
                return resp.text
            return None
        except httpx.HTTPError:
            return None
