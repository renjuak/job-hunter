"""
Main orchestration module for Job Hunter.

This module will coordinate the resume embedding and storage operations.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

from .resume.embed_resume import embed_resume_text, batch_embed_resumes
from .storage.db import get_resume_embedding, list_resume_embeddings

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env", override=True)
def main():
    """
    Main entry point for the Job Hunter application.
    
    This function will orchestrate the resume processing workflow.
    """
    print("Job Hunter - Resume Processing System")
    print("=" * 40)
    
    # Check if environment variables are set
    required_vars = ["OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_SERVICE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file")
        sys.exit(1)
    
    print("Environment variables configured successfully!")
    print("Ready to process resumes...")
    
    # TODO: Implement resume processing workflow
    # This will include:
    # 1. Reading resume files
    # 2. Extracting text content
    # 3. Creating embeddings
    # 4. Storing in Supabase
    # 5. Retrieving and analyzing stored data
    
    print("Resume processing workflow not yet implemented.")
    print("Check back later for updates!")

def process_single_resume(resume_id: str, text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Process a single resume by embedding its text and storing the result.
    
    Args:
        resume_id: Unique identifier for the resume
        text: The resume text content
        metadata: Optional metadata to store with the embedding
        
    Returns:
        Dictionary containing the processing result
    """
    try:
        print(f"Processing resume: {resume_id}")
        
        # Embed the resume text
        embedding = embed_resume_text(resume_id, text, metadata)
        
        print(f"Successfully embedded resume: {resume_id}")
        print(f"Embedding vector length: {len(embedding.embedding)}")
        
        return {
            "success": True,
            "resume_id": resume_id,
            "embedding_length": len(embedding.embedding),
            "metadata": embedding.metadata
        }
        
    except Exception as e:
        print(f"Error processing resume {resume_id}: {str(e)}")
        return {
            "success": False,
            "resume_id": resume_id,
            "error": str(e)
        }

def process_multiple_resumes(resumes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process multiple resumes in batch.
    
    Args:
        resumes: List of dictionaries containing resume_id, text, and optional metadata
        
    Returns:
        List of processing results
    """
    print(f"Processing {len(resumes)} resumes in batch...")
    
    results = []
    for resume_data in resumes:
        result = process_single_resume(
            resume_data["resume_id"],
            resume_data["text"],
            resume_data.get("metadata")
        )
        results.append(result)
    
    # Print summary
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful
    
    print(f"Batch processing complete:")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    
    return results

def list_stored_resumes(limit: int = 10) -> List[Dict[str, Any]]:
    """
    List stored resume embeddings.
    
    Args:
        limit: Maximum number of records to return
        
    Returns:
        List of stored resume records
    """
    try:
        print(f"Retrieving up to {limit} stored resumes...")
        
        resumes = list_resume_embeddings(limit=limit)
        
        print(f"Found {len(resumes)} stored resumes:")
        for resume in resumes:
            print(f"  - {resume['resume_id']} (created: {resume.get('created_at', 'unknown')})")
        
        return resumes
        
    except Exception as e:
        print(f"Error retrieving stored resumes: {str(e)}")
        return []

if __name__ == "__main__":
    main() 