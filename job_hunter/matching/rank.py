from __future__ import annotations
import json, yaml, pathlib
from typing import List, Tuple
from job_hunter.storage.db import get_supabase_client
from job_hunter.matching.job_agent import judge

# --------------------------------------------------------------------
CFG = yaml.safe_load((pathlib.Path(__file__).parents[2] / "config" / "prefs.yml").read_text())
LOC_KEYWORDS  = [k.lower() for k in CFG["locations"]]
TITLE_KEYWORDS= [k.lower() for k in CFG["titles"]]

# --------------------------------------------------------------------
def top_matches(resume_id: str, k: int = 20, shortlist: int = 80) -> List[Tuple[str, float]]:
    supa = get_supabase_client()

    # Résumé JSON (skills + years) ----------------------------------
    r_meta = supa.table("resume_embeddings").select("metadata") \
                 .eq("resume_id", resume_id).single().execute().data["metadata"]

    # Jobs -----------------------------------------------------------
    jobs = supa.table("jobs").select("job_id,title,location,description").execute().data

    # 1) deterministic pre-filter (location & title only) -----------
    cand = []
    for j in jobs:
        title = (j["title"] or "").lower()
        loc   = (j["location"] or "").lower()
        if LOC_KEYWORDS and not any(k in loc   for k in LOC_KEYWORDS):  continue
        if TITLE_KEYWORDS and not any(k in title for k in TITLE_KEYWORDS): continue
        cand.append(j)
    cand = cand[:shortlist]              # keep cost bounded

    # 2) LLM scoring -------------------------------------------------
    scored = []
    for j in cand:
        score, _ = judge(r_meta, j)
        scored.append((j["job_id"], score))

    scored.sort(key=lambda t: t[1], reverse=True)
    return scored[:k]
