# job_hunter/scrapers/__init__.py 

from importlib import import_module

REGISTRY = {
    "greenhouse":  "job_hunter.scrapers.greenhouse:GreenhouseScraper",
    "lever":       "job_hunter.scrapers.lever:LeverScraper",
    "ashby":       "job_hunter.scrapers.ashby:AshbyScraper",
    "workable":    "job_hunter.scrapers.workable:WorkableScraper",
    "recruitee":   "job_hunter.scrapers.recruitee:RecruiteeScraper",
    "teamtailor":  "job_hunter.scrapers.teamtailor:TeamtailorScraper",
    "bamboo":      "job_hunter.scrapers.bamboo:BambooScraper",
    "generic-json": "job_hunter.scrapers.generic_json:GenericJSONScraper",
    "rss":          "job_hunter.scrapers.rss:RSSScraper",
    "html-jsonld":  "job_hunter.scrapers.html_jsonld:HTMLJSONLDScraper",
    "linkedin":     "job_hunter.scrapers.linkedin_guest:LinkedInGuestScraper",
}

def get_scraper(board: str):
    path = REGISTRY[board]
    mod, cls = path.split(":")
    return getattr(import_module(mod), cls)
