# job_hunter/storage/jobs.py
from job_hunter.models import JobPost
from job_hunter.storage.db import get_supabase_client

def upsert_jobs(jobs: list[JobPost]) -> None:
    if not jobs:            # ← early-return prevents PGRST100
        return
    
    supa = get_supabase_client()
    payload = [j.dict() for j in jobs]
    supa.table("jobs").upsert(payload, on_conflict="job_id").execute()

def fetch_jobs_without_embeddings() -> list[JobPost]:
    supa = get_supabase_client()
    # left join to find jobs not yet embedded
    rows = supa.rpc("jobs_without_embeddings").execute().data  # see SQL below
    return [JobPost(**row) for row in rows]

def fetch_job_by_id(job_id: str) -> JobPost | None:
    supa = get_supabase_client()
    row = supa.table("jobs").select("*").eq("job_id", job_id).limit(1).execute().data
    return JobPost(**row[0]) if row else None