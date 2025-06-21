"""
Storage module for Job Hunter.

This module handles data storage and retrieval using Supabase.
"""

from .db import upsert_resume_embedding, get_resume_embedding

__all__ = ["upsert_resume_embedding", "get_resume_embedding"] 