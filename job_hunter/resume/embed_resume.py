"""
Resume embedding functionality using OpenAI's embedding API.

This module provides functions to embed resume text and store the results in Supabase.
"""

import os

from pathlib import Path
from typing import List, Dict, Any
# Load environment variables
from job_hunter.config import load_env
load_env() 
from openai import OpenAI
from job_hunter.models import ResumeEmbedding          # <— changed

from job_hunter.storage.db import upsert_resume_embedding




def embed_resume_text(resume_id: str, text: str, metadata: Dict[str, Any] = None) -> ResumeEmbedding:
    """
    Embed resume text using OpenAI's embedding API and store in Supabase.
    
    Args:
        resume_id: Unique identifier for the resume
        text: The resume text to embed
        metadata: Optional metadata to store with the embedding
        
    Returns:
        ResumeEmbedding object containing the embedding data
        
    Raises:
        ValueError: If OpenAI API key is not configured
        Exception: If embedding or storage fails
    """
    # Validate OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    try:
        # Create embedding
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        
        embedding_vector = response.data[0].embedding
        
        # Create embedding object
        resume_embedding = ResumeEmbedding(
            resume_id=resume_id,
            text=text,
            embedding=embedding_vector,
            metadata=metadata or {}
        )
        
        # Store in Supabase
        upsert_resume_embedding(resume_embedding)
        
        return resume_embedding
        
    except Exception as e:
        raise Exception(f"Failed to embed resume text: {str(e)}")

def batch_embed_resumes(resumes: List[Dict[str, Any]]) -> List[ResumeEmbedding]:
    """
    Embed multiple resumes in batch.
    
    Args:
        resumes: List of dictionaries containing resume_id, text, and optional metadata
        
    Returns:
        List of ResumeEmbedding objects
    """
    embeddings = []
    
    for resume_data in resumes:
        resume_id = resume_data["resume_id"]
        text = resume_data["text"]
        metadata = resume_data.get("metadata")
        
        embedding = embed_resume_text(resume_id, text, metadata)
        embeddings.append(embedding)
    
    return embeddings 