# job_hunter/matching/embed_jobs.py
"""
Embed all job descriptions that do **not** yet have a pgvector row.
Guaranteed ≤ 7 800 tokens / description, so OpenAI never throws the 8 192-token
error.
"""

from __future__ import annotations
import os, uuid
from typing import List
from job_hunter.config import load_env; load_env()
from job_hunter.storage.db import get_supabase_client
from job_hunter.storage.jobs import fetch_jobs_without_embeddings
from job_hunter.storage.job_embeddings import upsert_job_embeddings
from openai import OpenAI

# --------------------------------------------------------------------
# Robust tokenizer clamp (< 8 192 tokens)
# --------------------------------------------------------------------
MAX_TOKENS = 7_800          # generous safety margin

try:
    import tiktoken
    _enc = tiktoken.get_encoding("cl100k_base")  # model family encoder

    def _truncate(text: str) -> str:
        toks = _enc.encode(text)
        return _enc.decode(toks[:MAX_TOKENS]) if len(toks) > MAX_TOKENS else text

except ImportError:
    # First CI run (before tiktoken install) – coarse fallback
    MAX_CHARS = MAX_TOKENS * 4                    # ≈ 4 chars / token
    def _truncate(text: str) -> str:
        return text[:MAX_CHARS]
# --------------------------------------------------------------------

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def embed_all_jobs(batch_size: int = 96) -> None:
    jobs = fetch_jobs_without_embeddings()
    print(f"Found {len(jobs)} jobs needing embeddings")
    if not jobs:
        print("No new jobs to embed – all caught up ✅")
        return

    payload: List[dict] = []
    for i in range(0, len(jobs), batch_size):
        chunk = jobs[i : i + batch_size]
        inputs = [_truncate(j.description or "") for j in chunk]

        resp = client.embeddings.create(
            model="text-embedding-3-small",
            input=inputs,
            encoding_format="float",
        )

        for job, item in zip(chunk, resp.data):
            payload.append(
                {
                    "job_id":      job.job_id,
                    "vector":      item.embedding,
                    "emb_version": "text-embedding-3-small",
                }
            )

    upsert_job_embeddings(payload)
    print(f"✅ Embedded {len(payload)} jobs")


if __name__ == "__main__":
    embed_all_jobs()
