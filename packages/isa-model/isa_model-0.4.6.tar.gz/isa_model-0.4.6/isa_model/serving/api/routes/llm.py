"""
LLM API Routes

Endpoints for language model tasks (placeholder)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

@router.get("/")
async def llm_info():
    """LLM service information"""
    return {
        "service": "llm",
        "status": "placeholder", 
        "description": "Language model processing endpoints"
    }