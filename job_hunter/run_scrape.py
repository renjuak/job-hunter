import asyncio, yaml, pathlib, re
from datetime import datetime, timedelta, timezone
from job_hunter.scrapers           import get_scraper          # existing registry
from job_hunter.scrapers.search.multi import search_all_boards # NEW global search
from job_hunter.storage.jobs       import upsert_jobs
from job_hunter.resolve_board      import resolve

ROOT   = pathlib.Path(__file__).parents[1]
PREFS  = yaml.safe_load((ROOT / "config" / "prefs.yml").read_text())
COMP   = yaml.safe_load((ROOT / "config" / "companies.yml").read_text())
CUT_OFF= datetime.now(timezone.utc) - timedelta(days=7)

# ------------------------------------------------------------------ #
def _to_dt(ts):
    """Parse ISO-8601 string or return tz-aware datetime as-is."""
    if isinstance(ts, datetime):
        return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return datetime.min

# ------------------------------------------------------------------ #
def vendor_search() -> None:
    jobs = []
    for title in PREFS["titles"]:
        for loc in PREFS["locations"]:
            jobs.extend(search_all_boards(title, loc))
    jobs = [j for j in jobs if _to_dt(j.posted_at) > CUT_OFF]
    upsert_jobs(jobs)
    print(f"Vendor search inserted {len(jobs)} jobs.")

# ------------------------------------------------------------------ #
async def scrape_one_company(name: str):
    res = await resolve(name)
    Scraper = get_scraper(res["board"])
    jobs = Scraper(res["slug_or_url"], name).fetch()
    jobs = [j for j in jobs if _to_dt(j.posted_at) > CUT_OFF]
    upsert_jobs(jobs)
    print(f"{name:<15} {len(jobs):3d} new")

# ------------------------------------------------------------------ #
async def company_scrape() -> None:
    """Scrape all private boards in parallel (COMP list)."""
    await asyncio.gather(*(scrape_one_company(c) for c in COMP))

# ------------------------------------------------------------------ #
def main() -> None:
    asyncio.run(company_scrape())   # ← pass coroutine, not gather-future
    vendor_search()                 # sync; executes after the awaits

if __name__ == "__main__":
    main()
