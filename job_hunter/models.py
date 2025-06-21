# file: job_hunter/models.py  (new)
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ResumeEmbedding(BaseModel):
    resume_id: str = Field(..., description="Unique identifier for the resume")
    text: str = Field(..., description="The resume text content")
    embedding: List[float] = Field(..., description="OpenAI vector")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class JobPost(BaseModel):
    job_id:      str
    title:       str
    company:     str
    location:    str | None = None
    url:         str
    description: str
    posted_at:   str  # ISO timestamp


# job_hunter/scrapers/base.py
class Scraper:
    company_slug: str

    def fetch(self) -> list["JobPost"]:
        raise NotImplementedError


