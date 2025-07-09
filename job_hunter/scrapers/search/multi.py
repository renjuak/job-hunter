"""
Multi-vendor public search:
    • Greenhouse       (boards-api)
    • Lever            (undocumented query API)
    • Ashby (stub)

Call search_all_boards(title_kw, loc_kw) → list[JobPost]
"""

from __future__ import annotations
import httpx, urllib.parse, re
from datetime import datetime, timezone
from typing import List, Set
from job_hunter.models import JobPost


# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #
def _to_dt(ts) -> datetime:
    """
    Accept:
      • int / float (Unix-ms or s)
      • ISO-8601 string with or without Z
      • already-datetime
    Return tz-aware datetime (UTC).  datetime.min on failure.
    """
    if isinstance(ts, datetime):
        return ts.astimezone(timezone.utc)
    if isinstance(ts, (int, float)):
        # assume ms if > 1e10
        if ts > 10_000_000_000:
            ts /= 1000
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    if isinstance(ts, str):
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.min.replace(tzinfo=timezone.utc)


# ------------------------------------------------------------------ #
# Greenhouse search
# ------------------------------------------------------------------ #
def _greenhouse(title: str, loc: str) -> List[JobPost]:
    slugs = [
        "openai", "datadog", "stripe", "anthropic", "scaleai",
        "deepmind", "databricks", "figma", "notion",
    ]
    jobs: list[JobPost] = []
    for slug in slugs:
        qs  = urllib.parse.urlencode({"title": title})
        url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true&{qs}"
        try:
            data = httpx.get(url, timeout=8).json()["jobs"]
        except Exception:
            continue

        for j in data:
            loc_txt = (j.get("location", {}).get("name") or "").lower()
            if loc.lower() not in loc_txt:
                continue

            posted = _to_dt(j.get("updated_at") or j.get("created_at"))

            jobs.append(
                JobPost(
                    job_id   = f"gh-{j['id']}",
                    title    = j["title"],
                    company  = slug,
                    location = j["location"]["name"],
                    url      = j["absolute_url"],
                    description = re.sub(r"<[^>]+>", "", j["content"])[:5000],
                    source   = "gh-search",
                    posted_at= posted.isoformat(),
               )
            )
            
    return jobs


# ------------------------------------------------------------------ #
# Lever search
# ------------------------------------------------------------------ #
def _lever(title: str, loc: str) -> List[JobPost]:
    qs  = urllib.parse.urlencode({"query": title, "location": loc, "mode": "json"})
    url = f"https://api.lever.co/v0/postings?{qs}"
    try:
        data = httpx.get(url, timeout=8).json()
    except Exception:
        return []

    jobs: list[JobPost] = []
    for j in data:
        if not isinstance(j, dict):          # ← skip malformed rows
            continue
        posted = _to_dt(j.get("created"))
        jobs.append(
                JobPost(
                    job_id   = f"gh-{j['id']}",
                    title    = j["title"],
                    company  = slug,
                    location = j["location"]["name"],
                    url      = j["absolute_url"],
                    description = re.sub(r"<[^>]+>", "", j["content"])[:5000],
                    source   = "gh-search",
                    posted_at= posted.isoformat(),
               )
            )
    return jobs


# ------------------------------------------------------------------ #
# Ashby (stub for future)
# ------------------------------------------------------------------ #
def _ashby(title: str, loc: str) -> List[JobPost]:
    return []


# ------------------------------------------------------------------ #
# Public API
# ------------------------------------------------------------------ #
_VENDOR_FUNCS = [_greenhouse, _lever, _ashby]


def search_all_boards(title_kw: str, loc_kw: str) -> List[JobPost]:
    """
    Aggregate & de-duplicate results across all vendor search APIs.
    """
    seen: Set[str] = set()
    results: List[JobPost] = []
    for fn in _VENDOR_FUNCS:
        for job in fn(title_kw, loc_kw):
            if job.job_id in seen:
                continue
            seen.add(job.job_id)
            results.append(job)
    return results
