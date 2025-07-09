import os, json, functools
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYS = """You are a hiring assistant. 
Return JSON exactly:
{ "ok": true|false, "reason": "<one line>" }"""

@functools.lru_cache(maxsize=20_000)
def judge_requirements(resume_frag: str, req_text: str) -> dict:
    prompt = f"""Résumé snippet:
----------------
{resume_frag}

Job hard requirements:
----------------
{req_text}

Does the résumé satisfy most of the hard requirements?"""
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        temperature=0,
        messages=[
            {"role": "system", "content": SYS},
            {"role": "user",   "content": prompt},
        ],
    )
    try:
        return json.loads(resp.choices[0].message.content)
    except Exception:
        # fallback: treat non-JSON or parsing error as "no"
        return {"ok": False, "reason": "unparsable LLM output"}
