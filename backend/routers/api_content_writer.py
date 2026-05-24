from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
from core.article_writer import write_full_article

router = APIRouter(prefix="/api", tags=["content"])

class WriteFullRequest(BaseModel):
    topic: str
    sections: List[Dict[str, Any]]

@router.post("/content/write-full")
async def generate_full_article(req: WriteFullRequest):
    """
    Generate a full article using Groq AI based on a given topic and outline sections.
    """
    return await write_full_article(req.topic, req.sections)
