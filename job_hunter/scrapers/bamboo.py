# job_hunter/scrapers/bamboo.py
from __future__ import annotations
import httpx
from datetime import datetime, timezone
from typing import List
from job_hunter.models import JobPost

_API = "https://api.bamboohr.com/api/gateway.php/{slug}/v1/jobs/"

class BambooScraper:
    def __init__(self, slug: str, company: str):
        self.slug    = slug
        self.company = company

    def fetch(self) -> List[JobPost]:
        url = _API.format(slug=self.slug)
        try:
            data = httpx.get(url, timeout=8).json()["jobs"]
        except Exception:
            return []

        jobs=[]
        for j in data:
            # BambooHR fields are lowercase
            posted = datetime.fromisoformat(j["publishedDate"]).astimezone(timezone.utc)
            jobs.append(
                JobPost(
                    job_id     = f"bh-{j['id']}",
                    title      = j["jobOpeningName"],
                    company    = self.company,
                    location   = j.get("location","remote"),
                    url        = j["jobOpeningUrl"],
                    description= j.get("jobOpeningDescription","")[:5000],
                    source     = "bamboo",
                    posted_at  = posted.isoformat(),
                )
            )
        return jobs
