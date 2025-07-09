"""
Cache job requirements, preferred skills, seniority level, salary.
Falls back gracefully if LLM fails to return valid JSON.
"""

from __future__ import annotations
import os, json, re, functools
from datetime import datetime
from typing import Dict, Any
from openai import OpenAI
from job_hunter.storage.db import get_supabase_client

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
SYS = """Return JSON exactly:
{
 "required":  [...],
 "preferred": [...],
 "level":     "junior|mid|senior|staff",
 "salary":    <number or null>
}
"""

# ---------------- salary heuristic ---------------------------------
def _parse_salary(text: str) -> int | None:
    m = re.search(r"\$([1-9]\d{2,3})(?:[,\s]?(\d{3}))?\s*[kK]?", text)
    if not m:
        return None
    if m.group(2):
        return int(m.group(1) + m.group(2))
    return int(m.group(1)) * (1_000 if "k" in m.group(0).lower() else 1)

# ---------------- LLM call & parsing -------------------------------
def _call_llm(text: str) -> Dict[str, Any]:
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        temperature=0.0,
        messages=[
            {"role": "system", "content": SYS},
            {"role": "user", "content": text[:8000]},
        ],
    )
    raw = resp.choices[0].message.content.strip()

    # 1️⃣ strict load
    try:
        return json.loads(raw)
    except Exception:
        pass

    # 2️⃣ extract first { … } with regex
    m = re.search(r"\{.*\}", raw, re.S)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass

    # 3️⃣ fallback default
    return {
        "required": [],
        "preferred": [],
        "level": "mid",
        "salary": _parse_salary(text),
    }

# ---------------- public API ---------------------------------------
def extract_requirements(job_id: str, text: str) -> Dict[str, Any]:
    """Return cached row or call LLM, then persist."""
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

    data = _call_llm(text)
    data.setdefault("salary", _parse_salary(text))
    data.setdefault("level", "mid")
    data.setdefault("required", [])
    data.setdefault("preferred", [])
    data["job_id"] = job_id
    data["cached_at"] = datetime.utcnow().isoformat()

    supa.table("job_requirements").upsert(data, on_conflict="job_id").execute()
    return data
