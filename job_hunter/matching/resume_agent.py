import os, json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYS_PROMPT = """\
You are a helpful assistant that extracts structured data from a résumé.
Return JSON exactly:
{
  "skills": [canonical lowercase skills],
  "years":  <float total relevant experience>
}
"""

def inspect_resume(text: str) -> dict:
    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.0,
        messages=[
            {"role": "system", "content": SYS_PROMPT},
            {"role": "user",   "content": text[:8000]},
        ],
    )
    return json.loads(resp.choices[0].message.content)
