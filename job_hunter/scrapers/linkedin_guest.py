import httpx, urllib.parse, re, json, datetime
from typing import List
from job_hunter.models import JobPost

class LinkedInGuestScraper:
    def __init__(self, company: str, _unused: str):
        self.company = company

    def fetch(self) -> List[JobPost]:
        q  = urllib.parse.quote_plus(self.company)
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPostings/jobs?q={q}&location=Worldwide"
        try:
            data = httpx.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).json()["elements"]
        except Exception:
            return []
        jobs = []
        for j in data:
            jobs.append(
                JobPost(
                    job_id      = str(j["jobPostingId"]),
                    title       = j["title"],
                    company     = j.get("companyName", self.company),
                    location    = j.get("formattedLocation", ""),
                    url         = "https://www.linkedin.com/jobs/view/" + str(j["jobPostingId"]),
                    description = "",
                    source      = "linkedin",
                    posted_at   = datetime.datetime.utcnow(),
                )
            )
        return jobs
