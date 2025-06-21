# job_hunter/matching/rank.py
from __future__ import annotations
from math import sqrt
import json                              # ← add this
from typing import Sequence, List, Tuple
from job_hunter.config import load_env; load_env()
from job_hunter.storage.db import get_supabase_client

def _to_vec(v) -> List[float]:
    """Convert PostgREST pgvector output to list[float]."""
    if isinstance(v, str):
        # pgvector serialises as "[0.12,0.34,...]" which is valid JSON
        return json.loads(v)
    return v  # already a list

# ---------- low-level helper --------------------------------------------------
def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    dot   = sum(x * y for x, y in zip(a, b))
    mag_a = sqrt(sum(x * x for x in a))
    mag_b = sqrt(sum(y * y for y in b))
    return dot / (mag_a * mag_b) if mag_a and mag_b else 0.0


# ---------- high-level API ----------------------------------------------------
def top_matches(
    resume_id: str,
    k: int = 20,
    threshold: float = 0.55,
) -> List[Tuple[str, float]]:
    supa = get_supabase_client()

    # résumé vector ------------------------------------------
    res_row = (
        supa.table("resume_embeddings")
            .select("embedding")
            .eq("resume_id", resume_id)
            .execute()
            .data
    )
    if not res_row:
        raise ValueError(f"Résumé '{resume_id}' not found")
    resume_vec = _to_vec(res_row[0]["embedding"])

    # job vectors ---------------------------------------------
    rows = (
        supa.table("job_embeddings")
            .select("job_id, vector")
            .execute()
            .data
    )

    scored = [
        (row["job_id"], _cosine(resume_vec, _to_vec(row["vector"])))
        for row in rows
    ]
    scored.sort(key=lambda t: t[1], reverse=True)
    return [(jid, s) for jid, s in scored if s >= threshold][:k]
