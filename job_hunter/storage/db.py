"""
Supabase database operations for Job Hunter.

This module provides helper functions for storing and retrieving resume embeddings.
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from supabase import create_client, Client
from pydantic import BaseModel
from job_hunter.models import ResumeEmbedding          # <— changed
from pathlib import Path
import json                
from job_hunter.config import load_env
load_env()                           #  ← add this right after imports



class SupabaseConfig(BaseModel):
    """Configuration for Supabase connection."""
    url: str
    service_key: str

def get_supabase_client() -> Client:
    """
    Create and return a Supabase client.
    
    Returns:
        Supabase client instance
        
    Raises:
        ValueError: If Supabase credentials are not configured
    """
    url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not url or not service_key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables must be set")
    
    return create_client(url, service_key)

def upsert_resume_embedding(embedding: ResumeEmbedding) -> Dict[str, Any]:
    """
    Upsert a resume embedding to Supabase.
    
    Args:
        embedding: ResumeEmbedding object to store
        
    Returns:
        Dictionary containing the stored data
        
    Raises:
        Exception: If the upsert operation fails
    """
    try:
        supabase = get_supabase_client()
        
        # Prepare data for storage
        data = {
            "resume_id": embedding.resume_id,
            "text": embedding.text,
            "embedding": embedding.embedding,
            "metadata": embedding.metadata,
            "emb_version": "text-embedding-3-small",
        }
        
        # Upsert the data
        result = supabase.table("resume_embeddings").upsert(
            data,
            on_conflict="resume_id"
        ).execute()
        
        return result.data[0] if result.data else {}
        
    except Exception as e:
        raise Exception(f"Failed to upsert resume embedding: {str(e)}")

def _to_vec(v):
    """Convert pgvector text -> list[float] if needed."""
    return json.loads(v) if isinstance(v, str) else v

def get_resume_embedding(resume_id: str) -> ResumeEmbedding | None:
    """
    Retrieve a résumé embedding row and return a ResumeEmbedding model,
    coercing the 'embedding' pgvector into a list[float].
    """
    supa = get_supabase_client()
    res = (
        supa.table("resume_embeddings")
            .select("*")
            .eq("resume_id", resume_id)
            .single()
            .execute()
            .data
    )
    if not res:
        return None

    return ResumeEmbedding(
        resume_id = res["resume_id"],
        text      = res["text"],
        embedding = _to_vec(res["embedding"]),   # ← fix
        metadata  = res.get("metadata", {}),
    )

def delete_resume_embedding(resume_id: str) -> bool:
    """
    Delete a resume embedding from Supabase.
    
    Args:
        resume_id: Unique identifier for the resume
        
    Returns:
        True if deletion was successful, False otherwise
        
    Raises:
        Exception: If the deletion operation fails
    """
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("resume_embeddings").delete().eq(
            "resume_id", resume_id
        ).execute()
        
        return len(result.data) > 0
        
    except Exception as e:
        raise Exception(f"Failed to delete resume embedding: {str(e)}")

def list_resume_embeddings(limit: int = 100, offset: int = 0) -> list:
    """
    List resume embeddings from Supabase with pagination.
    
    Args:
        limit: Maximum number of records to return
        offset: Number of records to skip
        
    Returns:
        List of resume embedding records
        
    Raises:
        Exception: If the list operation fails
    """
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("resume_embeddings").select("*").range(
            offset, offset + limit - 1
        ).execute()
        
        return result.data
        
    except Exception as e:
        raise Exception(f"Failed to list resume embeddings: {str(e)}") 