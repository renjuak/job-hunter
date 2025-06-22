# job_hunter/scrapers/workable.py
import httpx, re
from datetime import datetime
from typing import List
from job_hunter.models import JobPost

class WorkableScraper:
    """
    Workable JSON feed:
      https://apply.workable.com/api/v1/accounts/<slug>/jobs
    """
    def __init__(self, slug: str, company: str):
        self.slug = slug
        self.company = company

    def fetch(self) -> List[JobPost]:
        url = f"https://apply.workable.com/api/v1/accounts/{self.slug}/jobs"
        data = httpx.get(url, timeout=15).json()
        jobs = []
        for j in data:
            desc = re.sub(r"<[^>]+>", "", j.get("description", ""))[:5000]
            jobs.append(
                JobPost(
                    job_id      = str(j["id"]),
                    title       = j["title"],
                    company     = self.company,
                    location    = j.get("location", ""),
                    url         = j["shortlink"],
                    description = desc,
                    source      = "workable",
                    posted_at   = datetime.fromisoformat(j["created_at"][:-1]),
                )
            )
        return jobs
