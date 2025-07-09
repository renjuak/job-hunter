# job_hunter/storage/jobs.py
from job_hunter.models import JobPost
from job_hunter.storage.db import get_supabase_client

def upsert_jobs(jobs: list[JobPost], batch_size: int = 500) -> None:
    """
    • De-duplicate by job_id (last occurrence wins)
    • Push rows to Supabase in batches ≤ batch_size
    """
    if not jobs:
        return

    # 1️⃣  collapse duplicates
    uniq: dict[str, JobPost] = {}
    for j in jobs:
        uniq[j.job_id] = j

    rows = [j.dict() for j in uniq.values()]
    supa = get_supabase_client()

    # 2️⃣  chunked UPSERT (avoids PostgREST 21000 + large-payload issues)
    for i in range(0, len(rows), batch_size):
        supa.table("jobs") \
            .upsert(rows[i : i + batch_size], on_conflict="job_id") \
            .execute()
        
def fetch_jobs_without_embeddings() -> list[JobPost]:
    supa = get_supabase_client()
    # left join to find jobs not yet embedded
    rows = supa.rpc("jobs_without_embeddings").execute().data  # see SQL below
    return [JobPost(**row) for row in rows]

def fetch_job_by_id(job_id: str) -> JobPost | None:
    supa = get_supabase_client()
    row = supa.table("jobs").select("*").eq("job_id", job_id).limit(1).execute().data
    return JobPost(**row[0]) if row else None