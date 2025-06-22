# job_hunter/scrapers/bamboo.py
import httpx, re, json
from datetime import datetime
from typing import List
from job_hunter.models import JobPost

class BambooScraper:
    """
    BambooHR careers JSON:
      https://<slug>.bamboohr.com/careers/list
    """
    def __init__(self, slug: str, company: str):
        self.slug = slug
        self.company = company

    def fetch(self) -> List[JobPost]:
        url = f"https://{self.slug}.bamboohr.com/careers/list"
        raw = httpx.get(url, timeout=15).text
        data = json.loads(raw)["result"]
        jobs = []
        for j in data:
            desc = re.sub(r"<[^>]+>", "", j.get("jobPosting", ""))[:5000]
            jobs.append(
                JobPost(
                    job_id      = str(j["Id"]),
                    title       = j["JobOpeningName"],
                    company     = self.company,
                    location    = j.get("Location", ""),
                    url         = j["ApplyUrl"],
                    description = desc,
                    source      = "bamboo",
                    posted_at   = datetime.utcnow(),   # Bamboo feed lacks dates
                )
            )
        return jobs
