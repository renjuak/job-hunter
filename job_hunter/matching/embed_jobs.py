# job_hunter/matching/embed_jobs.py
from pathlib import Path
from typing import List
from job_hunter.config import load_env; load_env()
from job_hunter.storage.db import get_supabase_client
from job_hunter.storage.jobs import fetch_jobs_without_embeddings
from job_hunter.storage.job_embeddings import upsert_job_embeddings
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed_all_jobs(batch_size: int = 96) -> None:
    jobs = fetch_jobs_without_embeddings()
    print(f"Found {len(jobs)} jobs needing embeddings")
    if not jobs:          # ← bail early, avoids PGRST100
        print("No new jobs to embed – all caught up ✅")
        return
 
    payload: List[dict] = []

    for i in range(0, len(jobs), batch_size):
        chunk = jobs[i : i + batch_size]
        resp = client.embeddings.create(
            model="text-embedding-3-small",
            input=[j.description for j in chunk],
        )
        for job, item in zip(chunk, resp.data):
            payload.append(
                dict(
                    job_id      = job.job_id,
                    vector      = item.embedding,          # matches DB column
                    emb_version = "text-embedding-3-small",
                )
            )

    upsert_job_embeddings(payload)
    print(f"✅ Embedded {len(payload)} jobs")

if __name__ == "__main__":
    embed_all_jobs()
