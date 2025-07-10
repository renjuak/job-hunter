from __future__ import annotations
import httpx, email.utils, uuid
from datetime import datetime, timezone
from typing import List
from xml.etree import ElementTree as ET
from job_hunter.models import JobPost

class RSSScraper:
    """
    Fetches an RSS/Atom feed.  Pass the full feed URL as slug_or_url.
    """
    def __init__(self, feed_url: str, company: str):
        self.url     = feed_url
        self.company = company

    def _parse_date(self, datestr: str) -> str:
        # rfc822 → datetime
        try:
            dt = email.utils.parsedate_to_datetime(datestr)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc).isoformat()
        except Exception:
            return datetime.now(timezone.utc).isoformat()

    def fetch(self) -> List[JobPost]:
        try:
            xml = httpx.get(self.url, timeout=10).text
            root = ET.fromstring(xml)
        except Exception:
            return []

        ns = {"atom": "http://www.w3.org/2005/Atom"}  # covers Atom feeds
        items = root.findall(".//item") or root.findall(".//atom:entry", ns)

        jobs = []
        for it in items:
            title = (it.findtext("title") or it.findtext("atom:title", namespaces=ns) or "").strip()
            link  = (it.findtext("link")  or
                     (it.find("atom:link", ns).attrib.get("href") if it.find("atom:link", ns) is not None else ""))
            pub   = (it.findtext("pubDate") or it.findtext("atom:updated", ns) or "")
            posted = self._parse_date(pub)

            jobs.append(
                JobPost(
                    job_id     = f"rss-{uuid.uuid4()}",
                    title      = title,
                    company    = self.company,
                    location   = "remote",
                    url        = link,
                    description= "",          # RSS usually lacks full JD
                    source     = "rss",
                    posted_at  = posted,
                )
            )
        return jobs
