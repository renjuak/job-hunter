# job_hunter/scrapers/recruitee.py
import httpx, re
from datetime import datetime
from typing import List
from job_hunter.models import JobPost

class RecruiteeScraper:
    """
    Recruitee feed:
      https://<slug>.recruitee.com/api/offers/
    """
    def __init__(self, slug: str, company: str):
        self.slug = slug
        self.company = company

    def fetch(self) -> List[JobPost]:
        url = f"https://{self.slug}.recruitee.com/api/offers/"
        data = httpx.get(url, timeout=15).json()["offers"]
        jobs = []
        for j in data:
            locs = ", ".join(l["city"] for l in j.get("locations", []))
            desc = re.sub(r"<[^>]+>", "", j.get("description", ""))[:5000]
            jobs.append(
                JobPost(
                    job_id      = str(j["id"]),
                    title       = j["title"],
                    company     = self.company,
                    location    = locs,
                    url         = j["careers_url"],
                    description = desc,
                    source      = "recruitee",
                    posted_at   = datetime.fromisoformat(j["created_at"][:-1]),
                )
            )
        return jobs
