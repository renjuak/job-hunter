import httpx, uuid
from datetime import datetime, timezone
from typing import List
from job_hunter.models import JobPost

class GenericJSONScraper:
    """Fetches a JSON array of job dicts from a full URL passed as slug_or_url."""
    def __init__(self, url: str, company: str):
        self.url     = url
        self.company = company

    def fetch(self) -> List[JobPost]:
        try:
            data = httpx.get(self.url, timeout=10).json()
        except Exception:
            return []

        now = datetime.now(timezone.utc).isoformat()
        jobs=[]
        for j in data:
            jobs.append(
                JobPost(
                    job_id   = f"gn-{uuid.uuid4()}",
                    title    = j.get("title",""),
                    company  = self.company,
                    location = j.get("location","remote"),
                    url      = j.get("url",""),
                    description = j.get("description","")[:5000],
                    source   = "generic",
                    posted_at= j.get("posted_at", now),
                )
            )
        return jobs
