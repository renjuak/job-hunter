# job_hunter/scrapers/recruitee.py
from __future__ import annotations
import httpx, json, re
from datetime import datetime, timezone
from typing import List
from job_hunter.models import JobPost

_API = "https://{slug}.recruitee.com/api/offers?limit=1000"

def _parse_ts(ts: str) -> str:
    """
    Recruitee returns e.g. '2025-05-02 12:48:04 UT'.
    Convert to timezone-aware ISO string.
    """
    try:
        # normal ISO case first
        return datetime.fromisoformat(ts).astimezone(timezone.utc).isoformat()
    except ValueError:
        pass

    # fallback for 'YYYY-MM-DD HH:MM:SS UT'
    m = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", ts)
    if m:
        dt = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
        return dt.replace(tzinfo=timezone.utc).isoformat()

    # last resort: now()
    return datetime.now(timezone.utc).isoformat()

class RecruiteeScraper:
    def __init__(self, slug: str, company: str):
        self.slug    = slug
        self.company = company

    def fetch(self) -> List[JobPost]:
        url = _API.format(slug=self.slug)
        try:
            data = httpx.get(url, timeout=10).json()["offers"]
        except Exception:
            return []

        jobs = []
        for j in data:
            posted_iso = _parse_ts(j["created_at"])
            jobs.append(
                JobPost(
                    job_id     = f"rc-{j['id']}",
                    title      = j["title"],
                    company    = self.company,
                    location   = j["city"] or "remote",
                    url        = j["careers_url"],
                    description= j.get("description", "")[:5000],
                    source     = "recruitee",
                    posted_at  = posted_iso,
                )
            )
        return jobs
