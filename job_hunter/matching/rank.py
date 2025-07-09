from __future__ import annotations
import json, yaml, pathlib, re
from typing import List, Tuple
from job_hunter.storage.db import get_supabase_client
from job_hunter.matching.job_agent        import judge
from job_hunter.matching.seniority_agent  import level_for, needed_years
from job_hunter.matching.job_requirements import extract_requirements

# --------------------------------------------------------------------#
# Configuration                                                       #
# --------------------------------------------------------------------#
ROOT = pathlib.Path(__file__).parents[2]
CFG  = yaml.safe_load((ROOT / "config" / "prefs.yml").read_text())
LOC_KEYWORDS   = [k.lower() for k in CFG["locations"]]
TITLE_KEYWORDS = [k.lower() for k in CFG["titles"]]

BIG_TECH = {
    c.lower() for c in yaml.safe_load((ROOT / "config" / "companies.yml").read_text())
}
# --------------------------------------------------------------------#


def _in_keywords(text: str, keywords: list[str]) -> bool:
    return any(k in text for k in keywords)


def top_matches(
    resume_id: str,
    k: int = 20,
    shortlist_cap: int = 300,   # cap before LLM cost kicks in
) -> List[Tuple[str, float]]:
    supa = get_supabase_client()

    # ----------------------------------------------------------------
    # Résumé metadata (skills + years)
    # ----------------------------------------------------------------
    r_meta = (
        supa.table("resume_embeddings")
            .select("metadata")
            .eq("resume_id", resume_id)
            .single()
            .execute()
            .data["metadata"]
    )
    resume_years  = r_meta.get("years", 0)
    resume_skills = {s.lower() for s in r_meta.get("skills", [])}

    # ----------------------------------------------------------------
    # All jobs from DB
    # ----------------------------------------------------------------
    jobs = (
        supa.table("jobs")
            .select("job_id,title,location,description,company")
            .execute()
            .data
    )

    # ----------------------------------------------------------------
    # Stage-1 / Stage-2  • title & location keywords (deterministic)
    # ----------------------------------------------------------------
    pre: list[dict] = []
    for j in jobs:
        title = (j["title"] or "").lower()
        loc   = (j["location"] or "").lower()
        if LOC_KEYWORDS   and not _in_keywords(loc,   LOC_KEYWORDS):
            continue
        if TITLE_KEYWORDS and not _in_keywords(title, TITLE_KEYWORDS):
            continue
        pre.append(j)
    pre = pre[:shortlist_cap]            # keep cost bounded

    # ----------------------------------------------------------------
    # Stage-3  • upside rule (salary ≥ 200K OR big-tech OR experience fit)
    # ----------------------------------------------------------------
    survivors: list[dict] = []
    lvl_cache: dict[str, str] = {}

    for j in pre:
        # requirements JSON (cached) contains salary (may be None)
        req  = extract_requirements(j["job_id"], j["description"])
        salary = req.get("salary")              # int or None

        slug = re.sub(r"[^a-z]", "", j["company"].lower())
        bigtech_ok = slug in BIG_TECH

        # seniority → needed years
        lvl = lvl_cache.get(j["job_id"]) or level_for(
            j["job_id"], j["title"], j["description"]
        )
        lvl_cache[j["job_id"]] = lvl
        exp_ok = resume_years >= needed_years(lvl)

        salary_ok = salary is None or salary >= 200_000

        if not (salary_ok or bigtech_ok or exp_ok):
            continue

        # Stage-4  • hard requirements (all must be present)
        required = {r.lower() for r in req["required"]}
        overlap  = len(required & resume_skills) / (len(required) or 1)
        if overlap < 0.60:            # ← tweak 0.60→0.50 for even looser match
          continue

        survivors.append(j)

    # ----------------------------------------------------------------
    # Stage-5  • GPT-4o holistic scoring
    # ----------------------------------------------------------------
    scored: list[Tuple[str, float]] = []
    for j in survivors:
        score, _ = judge(r_meta, j)      # GPT-4o reasoning
        scored.append((j["job_id"], score))

    scored.sort(key=lambda t: t[1], reverse=True)
    return scored[:k]
