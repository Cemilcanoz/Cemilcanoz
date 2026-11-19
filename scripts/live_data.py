"""Fetch public GitHub stats for the live card and save data/live.json.

Uses GITHUB_TOKEN (set automatically in GitHub Actions). Locally it falls
back to `gh auth token`. Only public data is requested.

    python scripts/live_data.py && python scripts/build_svgs.py
"""
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

USER = "Cemilcanoz"
OUT = Path(__file__).resolve().parent.parent / "data" / "live.json"
WEEKS = 26


def _token() -> str:
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        return tok
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()


TOKEN = _token()


def api(path: str, body: dict | None = None):
    url = path if path.startswith("http") else f"https://api.github.com{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "profile-live-card",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def search_count(q: str) -> int:
    return api("/search/issues?" + urllib.parse.urlencode({"q": q, "per_page": 1}))["total_count"]


def main() -> None:
    d: dict = {"updated": dt.date.today().isoformat()}
    d["open_prs"] = search_count(f"author:{USER} type:pr is:open is:public -user:{USER}")
    d["merged_prs"] = search_count(f"author:{USER} type:pr is:merged is:public")
    d["public_repos"] = api(f"/users/{USER}")["public_repos"]
    try:
        d["release"] = api(f"/repos/{USER}/codex-history/releases/latest")["tag_name"]
    except Exception:
        d["release"] = None
    repos = api(f"/users/{USER}/repos?sort=pushed&per_page=5&type=owner")
    repo = next((r for r in repos if r["name"] != USER), repos[0] if repos else None)
    if repo:
        d["last_push"] = f"{repo['name']} · {repo['pushed_at'][:10]}"
    q = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
          totalContributions weeks{contributionDays{contributionCount}}}}}}"""
    cal = api("https://api.github.com/graphql", {"query": q, "variables": {"login": USER}})
    cal = cal["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [sum(day["contributionCount"] for day in w["contributionDays"]) for w in cal["weeks"]]
    d["weeks"] = weeks[-WEEKS:]
    d["total"] = cal["totalContributions"]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in d.items() if k != "weeks"}))


if __name__ == "__main__":
    main()
