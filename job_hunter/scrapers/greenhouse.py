import requests
import time
from typing import List, Optional
from datetime import datetime

from ..models import JobPost


class GreenhouseScraper:
    """Scraper for Greenhouse job boards (e.g., company_slug='stripe')."""
    
    def __init__(self, company_slug: str, company_name: Optional[str] = None):
        self.company_slug = company_slug
        self.company_name = company_name or company_slug.title()
        self.base_url = "https://boards-api.greenhouse.io/v1/boards"
    
    def fetch(self) -> List[JobPost]:
        """Fetch jobs from Greenhouse API with retry logic."""
        url = f"{self.base_url}/{self.company_slug}/jobs"
        params = {"content": "true"}
        
        for attempt in range(3):
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                return self._normalize_jobs(data.get("jobs", []))
                
            except requests.RequestException as e:
                if attempt == 2:  # Last attempt
                    raise Exception(f"Failed to fetch jobs from Greenhouse after 3 attempts: {e}")
                
                # Exponential backoff: 1s, 2s, 4s
                wait_time = 2 ** attempt
                time.sleep(wait_time)
        
        return []
    
    def _normalize_jobs(self, jobs_data: List[dict]) -> List[JobPost]:
        """Normalize Greenhouse job data to JobPost objects."""
        normalized_jobs = []
        
        for job in jobs_data:
            try:
                # Extract location - handle nested structure
                location = None
                if job.get("location"):
                    location = job["location"].get("name")
                
                # Extract description from content
                description = ""
                if job.get("content"):
                    description = job["content"]
                
                # Format posted date
                posted_at = ""
                if job.get("updated_at"):
                    # Convert to ISO format if needed
                    posted_at = job["updated_at"]
                
                job_post = JobPost(
                    job_id=str(job.get("id", "")),
                    title=job.get("title", ""),
                    company=self.company_name,
                    location=location,
                    url=job.get("absolute_url", ""),
                    description=description,
                    posted_at=posted_at
                )
                
                normalized_jobs.append(job_post)
                
            except Exception as e:
                # Log error but continue processing other jobs
                print(f"Error normalizing job {job.get('id', 'unknown')}: {e}")
                continue
        
        return normalized_jobs 