"""
Resume embedding functionality using OpenAI's embedding API.

This module provides functions to embed resume text and store the results in Supabase.
"""

import os

from pathlib import Path
from typing import List, Dict, Any
# Load environment variables
from job_hunter.config import load_env
load_env() 
from openai import OpenAI
from job_hunter.models import ResumeEmbedding          # <— changed

from job_hunter.storage.db import upsert_resume_embedding
from job_hunter.matching.resume_agent import inspect_resume
from job_hunter.utils.hash import sha256_text
from job_hunter.storage.db import get_supabase_client, get_resume_embedding


def embed_resume_text(resume_id: str, text: str, metadata: dict | None = None):
    supa = get_supabase_client()            # ← ADD this before using `supa`

    # ----- checksum short-circuit ---------------------------------
    digest = sha256_text(text)
    existing = supa.table("resume_embeddings").select("sha256") \
                   .eq("resume_id", resume_id).single().execute().data
    if existing and existing["sha256"] == digest:
        print("Résumé unchanged – skipping re-embed")
        return get_resume_embedding(resume_id)
    # ----- embedding & LLM inspection ------------------------------
    response = client.embeddings.create(model="text-embedding-3-small", input=text)
    meta = metadata or {}
    meta.update(inspect_resume(text))        # ⇐ skills + years from LLM
    
    resume_embedding = ResumeEmbedding(
        resume_id=resume_id,
        text=text,
        embedding=response.data[0].embedding,
        metadata=meta,
    )

    data = resume_embedding.dict()
    data["sha256"] = digest
    supa.table("resume_embeddings").upsert(data, on_conflict="resume_id").execute()
    return resume_embedding

def batch_embed_resumes(resumes: List[Dict[str, Any]]) -> List[ResumeEmbedding]:
    """
    Embed multiple resumes in batch.
    
    Args:
        resumes: List of dictionaries containing resume_id, text, and optional metadata
        
    Returns:
        List of ResumeEmbedding objects
    """
    embeddings = []
    
    for resume_data in resumes:
        resume_id = resume_data["resume_id"]
        text = resume_data["text"]
        metadata = resume_data.get("metadata")
        
        embedding = embed_resume_text(resume_id, text, metadata)
        embeddings.append(embedding)
    
    return embeddings 

# ----------------------------------------------------------------------
# CLI ENTRY-POINT
# ----------------------------------------------------------------------
def cli() -> None:
    """
    Usage:
        poetry run embed-resume resume/resume.pdf
        poetry run embed-resume resume.txt --id my-resume
    """
    import argparse, pathlib
    from job_hunter.resume.pdf_to_text import extract_text  # your PDF→text util

    ap = argparse.ArgumentParser(description="Embed a résumé into Supabase")
    ap.add_argument("file", help="PDF or TXT résumé")
    ap.add_argument("--id", help="resume_id (defaults to file stem)")
    args = ap.parse_args()

    path = pathlib.Path(args.file)
    if not path.exists():
        raise SystemExit(f"❌ file not found: {path}")

    if path.suffix.lower() == ".pdf":
        text = extract_text(path)
    else:
        text = path.read_text()

    resume_id = args.id or path.stem
    embed_resume_text(resume_id, text)
    print(f"✅ résumé '{resume_id}' processed & stored")

if __name__ == "__main__":          # allows “python -m …” too
    cli()