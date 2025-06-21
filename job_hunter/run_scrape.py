# job_hunter/run_scrape.py
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