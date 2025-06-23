import os, json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYS_PROMPT = """\
You are an expert hiring assistant. Rate how well the RESUME fits the JOB.
Return JSON exactly:
{"score": 0-1 float, "reason": "short explanation"}

Consider (but do not report separately):
• Overlap of specific skills / tools
• Whether resume.years meet the seniority implied by the job title/description
• Any hard blockers (e.g. resume skills lack required stack)
"""

def judge(resume_json: dict, job_dict: dict) -> tuple[float, str]:
    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.0,
        messages=[
            {"role":"system","content":SYS_PROMPT},
            {"role":"user","content":json.dumps({
                "resume": resume_json,
                "job": job_dict,
            })},
        ],
    )
    j = json.loads(resp.choices[0].message.content)
    return float(j["score"]), j.get("reason","")
