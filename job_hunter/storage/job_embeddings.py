from job_hunter.models import JobPost
from job_hunter.storage.db import get_supabase_client
from typing import List

def upsert_job_embeddings(rows: List[dict]) -> None:
    supa = get_supabase_client()
    supa.table("job_embeddings").upsert(rows, on_conflict="job_id").execute()