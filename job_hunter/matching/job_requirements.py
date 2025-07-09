"""
Cache per-job requirements, preferred skills, seniority level, and salary.

• One 3.5-turbo API call per job_id the first time we see it.
• Result persisted to Supabase so later runs are free.
"""

from __future__ import annotations
import os, json, re, functools
from datetime import datetime
from typing import Dict, Any
from openai import OpenAI

from job_hunter.storage.db import get_supabase_client

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
SYS = """You are an HR parsing assistant.
Extract STRICT requirements from a job description.

Return JSON exactly:
{
 "required":  [list of hard-required skills / certs],
 "preferred": [list of nice-to-have skills],
 "level":     "junior|mid|senior|staff",
 "salary":    <annual base in USD, or null>
}
Only include skills or terms explicitly mentioned in the posting.
"""

# --------------------------------------------------------------------
def _parse_salary(text: str) -> int | None:
    """
    Extract first $120k, $200,000, etc. Returns int dollars or None.
    """
    m = re.search(r"\$([1-9]\d{2,3})(?:[,\s]?(\d{3}))?\s*[kK]?", text)
    if not m:
        return None
    if m.group(2):                               # e.g. $200,000
        return int(m.group(1) + m.group(2))
    return int(m.group(1)) * (1_000 if 'k' in m.group(0).lower() else 1)


# --------------------------------------------------------------------
def _call_llm(text: str) -> Dict[str, Any]:
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        temperature=0.0,
        messages=[{"role":"system","content":SYS},
                  {"role":"user",  "content":text[:8000]}],
    )
    data = json.loads(resp.choices[0].message.content)
    # fallback salary heuristic if LLM left null
    if data.get("salary") is None:
        data["salary"] = _parse_salary(text)
    return data


# --------------------------------------------------------------------
def extract_requirements(job_id: str, text: str) -> Dict[str, Any]:
    """
    Fetch cached JSON from Supabase or call LLM and persist.
    """
    supa = get_supabase_client()
    row = (
        supa.table("job_requirements")
            .select("*")
            .eq("job_id", job_id)
            .execute()
            .data
    )
    if row:
        return row[0]

    # call LLM once
    data = _call_llm(text)
    data["job_id"] = job_id
    data["cached_at"] = datetime.utcnow().isoformat()

    # persist
    supa.table("job_requirements").upsert(data, on_conflict="job_id").execute()
    return data
