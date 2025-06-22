import httpx, json, re, selectolax.parser as dom
from datetime import datetime
from typing import List
from job_hunter.models import JobPost

class HTMLJSONLDScraper:
    def __init__(self, url: str, company: str):
        self.url = url
        self.company = company

    def fetch(self) -> List[JobPost]:
        html = httpx.get(self.url, timeout=15).text
        doc  = dom.HTMLParser(html)
        jobs = []
        for tag in doc.css('script[type="application/ld+json"]'):
            try:
                data = json.loads(tag.text())
                items = data if isinstance(data, list) else [data]
            except Exception:
                continue
            for item in items:
                if item.get("@type") != "JobPosting":
                    continue
                jobs.append(
                    JobPost(
                        job_id      = item.get("identifier", {}).get("value", item["url"]),
                        title       = item["title"],
                        company     = self.company,
                        location    = item.get("jobLocation", {}).get("address", {}).get("addressLocality", ""),
                        url         = item["url"],
                        description = re.sub(r"<[^>]+>", "", item.get("description", ""))[:5000],
                        source      = "html-jsonld",
                        posted_at   = datetime.fromisoformat(item.get("datePosted", datetime.utcnow().isoformat())),
                    )
                )
        return jobs
