import asyncio, httpx, re, json, urllib.parse, selectolax.parser as dom
from datetime import datetime
from job_hunter.storage.db import get_supabase_client

PROBES = {
    "greenhouse":  "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=false",
    "lever":       "https://api.lever.co/v0/postings/{slug}?mode=json",
    "ashby":       "https://{slug}.ashbyhq.com/api/non-user-application/job-board/{slug}",
    "workable":    "https://apply.workable.com/api/v1/accounts/{slug}/jobs",
    "recruitee":   "https://{slug}.recruitee.com/api/offers/",
    "teamtailor":  "https://api.teamtailor.com/v1/accounts/{slug}/jobs",
    "bamboo":      "https://{slug}.bamboohr.com/careers/list",
}

JSON_PATHS = ["/jobs.json", "/careers/jobs.json"]
RSS_PATHS  = ["/careers/feed.xml", "/jobs/rss"]

HEADERS = {"User-Agent": "job-hunter-probe/1.0"}

def _slug_candidates(name: str) -> set[str]:
    plain = re.sub(r"[^a-z0-9]", "", name.lower())
    return {plain, plain.replace("ai", "")+"ai", name.lower().split()[0]}

async def _head(client, url):
    try:
        r = await client.get(url, headers=HEADERS, timeout=6)
        return r.status_code < 300
    except Exception:
        return False

async def resolve(company: str) -> dict:
    supa = get_supabase_client()
    cached = supa.table("board_resolver").select("*").eq("company", company).execute().data
    if cached:
        return cached[0]

    async with httpx.AsyncClient(timeout=6) as client:
        # Tier A – vendor probes
        for slug in _slug_candidates(company):
            tasks = {b: _head(client, url.format(slug=slug)) for b, url in PROBES.items()}
            done = await asyncio.gather(*tasks.values())
            for (board, _), ok in zip(tasks.items(), done):
                if ok:
                    res = {"company": company, "board": board, "slug_or_url": slug}
                    supa.table("board_resolver").upsert(res, on_conflict="company").execute()
                    return res

        # Tier B – machine-readable feeds
        domain = f"{_slug_candidates(company).pop()}.com"
        for path in [*JSON_PATHS, *RSS_PATHS]:
            url = f"https://{domain}{path}"
            if await _head(client, url):
                board = "generic-json" if url.endswith(".json") else "rss"
                res = {"company": company, "board": board, "slug_or_url": url}
                supa.table("board_resolver").upsert(res, on_conflict="company").execute()
                return res

        # Tier C – JSON-LD on careers root
        root = f"https://{domain}/careers"
        try:
            html = (await client.get(root)).text
            if '"JobPosting"' in html:
                res = {"company": company, "board": "html-jsonld", "slug_or_url": root}
                supa.table("board_resolver").upsert(res, on_conflict="company").execute()
                return res
        except Exception:
            pass

    # Tier D – LinkedIn guest search
    res = {"company": company, "board": "linkedin", "slug_or_url": company}
    supa.table("board_resolver").upsert(res, on_conflict="company").execute()
    return res
