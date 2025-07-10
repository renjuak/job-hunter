from __future__ import annotations
import httpx, re
from datetime import datetime, timezone
from typing import List
from job_hunter.models import JobPost

class LeverScraper:
    """
    Works for any public Lever board slug.
    Example slug: 'canva' → https://jobs.lever.co/canva.json
    """
    def __init__(self, slug: str, company: str):
        self.slug    = slug
        self.company = company

    def fetch(self) -> List[JobPost]:
        url  = f"https://jobs.lever.co/{self.slug}.json"
        try:
            data = httpx.get(url, timeout=10).json()
        except Exception:
            return []

        jobs=[]
        for j in data:
            posted = datetime.fromtimestamp(j["createdAt"]/1000, tz=timezone.utc)
            jobs.append(
                JobPost(
                    job_id   = f"lv-{j['id']}",
                    title    = j["text"],
                    company  = self.company,
                    location = j.get("categories",{}).get("location","Remote"),
                    url      = j["hostedUrl"],
                    description = j.get("description","")[:5000],
                    source   = "lever",
                    posted_at= posted.isoformat(),
                )
            )
        return jobs
