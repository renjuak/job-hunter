# job_hunter/run_scrape.py
'''
from job_hunter.scrapers.greenhouse import GreenhouseScraper
from job_hunter.storage.jobs import upsert_jobs
from job_hunter.config import load_env
load_env() 

def main() -> None:
    # -- Stripe slug ---------------------------------------------------------
    scraper = GreenhouseScraper(company_slug="stripe", company_name="Stripe")
    jobs = scraper.fetch()
    upsert_jobs(jobs)
    print(f"Inserted/updated {len(jobs)} Stripe jobs 🚀")

if __name__ == "__main__":
    main()
'''

import asyncio, yaml, pathlib
from job_hunter.resolve_board import resolve
from job_hunter.scrapers import get_scraper
from job_hunter.storage.jobs import upsert_jobs
from job_hunter.config import load_env; load_env()

CFG = pathlib.Path(__file__).resolve().parents[1] / "config" / "companies.yml"

async def scrape_one(name: str):
    res = await resolve(name)
    Scraper = get_scraper(res["board"])
    jobs = Scraper(res["slug_or_url"], name).fetch()
    upsert_jobs(jobs)
    print(f"{name:<15} {res['board']:<12} {len(jobs):3d}")

async def main():
    companies = yaml.safe_load(CFG.read_text())
    await asyncio.gather(*(scrape_one(c) for c in companies))

# NEW: sync wrapper for Poetry entry-point
def cli():
    asyncio.run(main())

if __name__ == "__main__":
    cli()

