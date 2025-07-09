import os, json, functools, re
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
SYS="Return JSON {'level':'junior|mid|senior|staff'} for the given title+desc"
@functools.lru_cache(maxsize=10_000)
def level_for(job_id:str, title:str, desc:str)->str:
    msg=f"Title: {title}\nDesc: {desc[:600]}"
    r=client.chat.completions.create(model="gpt-3.5-turbo-0125",temperature=0,
        messages=[{"role":"system","content":SYS},{"role":"user","content":msg}],)
    return json.loads(r.choices[0].message.content)["level"]
def needed_years(level:str)->int:
    return {"junior":0,"mid":3,"senior":5,"staff":8}.get(level,3)
