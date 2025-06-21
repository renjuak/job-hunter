"""
Trivial tests for Job Hunter.

These tests verify that the basic project structure and imports work correctly.
"""

import pytest
from job_hunter import __version__


def test_version():
    """Test that the package version is defined."""
    assert __version__ == "0.1.0"


def test_imports():
    """Test that all main modules can be imported."""
    # Test main package
    import job_hunter
    
    # Test resume module
    from job_hunter.resume import embed_resume_text
    from job_hunter.resume.embed_resume import ResumeEmbedding
    
    # Test storage module
    from job_hunter.storage import upsert_resume_embedding, get_resume_embedding
    from job_hunter.storage.db import get_supabase_client
    
    # Test main module
    from job_hunter.main import main, process_single_resume
    
    assert True  # If we get here, all imports worked


def test_resume_embedding_model():
    """Test the ResumeEmbedding Pydantic model."""
    from job_hunter.resume.embed_resume import ResumeEmbedding
    
    # Test model creation
    embedding = ResumeEmbedding(
        resume_id="test-123",
        text="This is a test resume",
        embedding=[0.1, 0.2, 0.3],
        metadata={"source": "test"}
    )
    
    assert embedding.resume_id == "test-123"
    assert embedding.text == "This is a test resume"
    assert len(embedding.embedding) == 3
    assert embedding.metadata["source"] == "test"


def test_supabase_config_model():
    """Test the SupabaseConfig Pydantic model."""
    from job_hunter.storage.db import SupabaseConfig
    
    # Test model creation
    config = SupabaseConfig(
        url="https://test.supabase.co",
        service_key="test-key"
    )
    
    assert config.url == "https://test.supabase.co"
    assert config.service_key == "test-key"


if __name__ == "__main__":
    pytest.main([__file__]) 