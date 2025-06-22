# job_hunter/scrapers/teamtailor.py
import httpx, re
from datetime import datetime
from typing import List
from job_hunter.models import JobPost

HEADERS = {
    "X-Api-Version": "20230101",
    "Accept": "application/vnd.api+json",
}

class TeamtailorScraper:
    """
    Teamtailor API:
      https://api.teamtailor.com/v1/accounts/<slug>/jobs
    """
    def __init__(self, slug: str, company: str):
        self.slug = slug
        self.company = company

    def fetch(self) -> List[JobPost]:
        url = f"https://api.teamtailor.com/v1/accounts/{self.slug}/jobs"
        data = httpx.get(url, headers=HEADERS, timeout=15).json()["data"]
        jobs = []
        for d in data:
            attr = d["attributes"]
            desc = re.sub(r"<[^>]+>", "", attr.get("descriptionHtml", ""))[:5000]
            jobs.append(
                JobPost(
                    job_id      = d["id"],
                    title       = attr["title"],
                    company     = self.company,
                    location    = attr.get("location", ""),
                    url         = attr["urls"]["applyUrl"],
                    description = desc,
                    source      = "teamtailor",
                    posted_at   = datetime.fromisoformat(attr["createdAt"][:-1]),
                )
            )
        return jobs
