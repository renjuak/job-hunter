import pytest
from job_hunter.scrapers.greenhouse import GreenhouseScraper
from job_hunter.models import JobPost


class TestGreenhouseScraper:
    """Test cases for Greenhouse scraper."""
    
    def test_fetch_stripe_jobs(self):
        """Test fetching jobs from Stripe's Greenhouse board."""
        scraper = GreenhouseScraper("stripe", "Stripe")
        jobs = scraper.fetch()
        
        # Assert that at least one job is returned
        assert len(jobs) > 0, "Expected at least one job from Stripe board"
        
        # Assert that all returned items are JobPost instances
        for job in jobs:
            assert isinstance(job, JobPost), f"Expected JobPost instance, got {type(job)}"
        
        # Assert that job fields are properly populated
        for job in jobs:
            assert job.job_id, "Job ID should not be empty"
            assert job.title, "Job title should not be empty"
            assert job.company == "Stripe", "Company should be set to Stripe"
            assert job.url, "Job URL should not be empty"
    
    def test_scraper_initialization(self):
        """Test scraper initialization with different parameters."""
        # Test with company_name provided
        scraper1 = GreenhouseScraper("stripe", "Stripe Inc.")
        assert scraper1.company_slug == "stripe"
        assert scraper1.company_name == "Stripe Inc."
        
        # Test without company_name (should use slug)
        scraper2 = GreenhouseScraper("stripe")
        assert scraper2.company_slug == "stripe"
        assert scraper2.company_name == "Stripe"  # slug.title()
    
    def test_job_post_structure(self):
        """Test that returned JobPost objects have the expected structure."""
        scraper = GreenhouseScraper("stripe")
        jobs = scraper.fetch()
        
        if jobs:  # Only test if jobs are returned
            job = jobs[0]
            
            # Check required fields
            assert hasattr(job, 'job_id')
            assert hasattr(job, 'title')
            assert hasattr(job, 'company')
            assert hasattr(job, 'url')
            assert hasattr(job, 'description')
            assert hasattr(job, 'posted_at')
            
            # Check optional fields
            assert hasattr(job, 'location')
            
            # Verify field types
            assert isinstance(job.job_id, str)
            assert isinstance(job.title, str)
            assert isinstance(job.company, str)
            assert isinstance(job.url, str)
            assert isinstance(job.description, str)
            assert isinstance(job.posted_at, str)
            # location can be None or str
            assert job.location is None or isinstance(job.location, str) 