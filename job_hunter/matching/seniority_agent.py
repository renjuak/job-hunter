import os, json, functools, re
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYS = """Return JSON exactly {"level":"junior|mid|senior|staff"} for the given title+desc"""

@functools.lru_cache(maxsize=10_000)
def level_for(job_id: str, title: str, desc: str) -> str:
    """Cached LLM call → 'junior'|'mid'|'senior'|'staff'.  Falls back to heuristics."""
    prompt = f"Title: {title}\nDesc:\n{desc[:800]}"
    try:
        r = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            temperature=0,
            messages=[{"role": "system", "content": SYS},
                      {"role": "user",   "content": prompt}],
        )
        raw = r.choices[0].message.content.strip()
        # try strict JSON
        data = json.loads(raw)
        lvl  = data["level"].lower()
        if lvl in {"junior", "mid", "senior", "staff"}:
            return lvl
    except Exception:
        pass  # fall through to heuristics

    # ---------- heuristic fallback ---------------------------------
    t = title.lower()
    if re.search(r"\b(staff|principal|lead|architect)\b", t):
        return "staff"
    if "senior" in t or "sr." in t:
        return "senior"
    if "intern" in t or "graduate" in t:
        return "junior"
    return "mid"   # safe default

def needed_years(level: str) -> int:
    return {"junior": 0, "mid": 3, "senior": 5, "staff": 8}.get(level, 3)
