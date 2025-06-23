"""
Embed a résumé with OpenAI embeddings and store/refresh it in Supabase.
"""

from __future__ import annotations
import os, argparse, pathlib
from typing import List, Dict, Any

from job_hunter.config import load_env; load_env()          # loads .env
from openai import OpenAI

from job_hunter.models      import ResumeEmbedding
from job_hunter.storage.db  import (
    upsert_resume_embedding,
    get_resume_embedding,
    get_supabase_client,
)
from job_hunter.matching.resume_agent import inspect_resume
from job_hunter.utils.hash             import sha256_text
from job_hunter.resume.pdf_to_text     import extract_text   # your PDF→text util


# ---------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------
def embed_resume_text(resume_id: str, text: str, metadata: dict | None = None
) -> ResumeEmbedding:
    """Embed `text` and write/overwrite the résumé row in Supabase."""
    supa   = get_supabase_client()
    digest = sha256_text(text)

    # short-circuit if unchanged
    rows = (
    supa.table("resume_embeddings")
        .select("sha256")
        .eq("resume_id", resume_id)
        .execute()
        .data              # rows is [] when the résumé is not yet in the table
    )
    existing = rows[0] if rows else None        # ← safe even when table is empty
    if existing and existing["sha256"] == digest:
        print("ℹ️  résumé unchanged – using cached embedding")
        return get_resume_embedding(resume_id)

    # OpenAI embedding ------------------------------------------------
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    emb = client.embeddings.create(model="text-embedding-3-small", input=text)

    # LLM résumé inspection ------------------------------------------
    meta = metadata or {}
    meta.update(inspect_resume(text))          # {"skills":[…], "years": …}

    resume_embedding = ResumeEmbedding(
        resume_id = resume_id,
        text      = text,
        embedding = emb.data[0].embedding,
        metadata  = meta,
    )

    # store with checksum
    data = resume_embedding.dict()
    data["sha256"] = digest
    supa.table("resume_embeddings").upsert(data, on_conflict="resume_id").execute()
    print(f"✅ résumé '{resume_id}' embedded & stored")
    return resume_embedding


# ---------------------------------------------------------------------
# Batch helper (optional)
# ---------------------------------------------------------------------
def batch_embed_resumes(resumes: List[Dict[str, Any]]) -> List[ResumeEmbedding]:
    return [
        embed_resume_text(r["resume_id"], r["text"], r.get("metadata"))
        for r in resumes
    ]


# ---------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------
def cli() -> None:
    """
    Examples
    --------
    poetry run embed-resume resume/resume.pdf
    poetry run embed-resume resume.txt --id my-resume
    """
    ap = argparse.ArgumentParser(description="Embed a résumé into Supabase")
    ap.add_argument("file", help="PDF or TXT résumé file")
    ap.add_argument("--id", help="resume_id (defaults to file name w/o ext)")
    args = ap.parse_args()

    path = pathlib.Path(args.file).expanduser()
    if not path.exists():
        raise SystemExit(f"❌ file not found: {path}")

    text = extract_text(path) if path.suffix.lower() == ".pdf" else path.read_text()
    resume_id = args.id or path.stem
    embed_resume_text(resume_id, text)


if __name__ == "__main__":          # allows: python -m job_hunter.resume.embed_resume
    cli()
