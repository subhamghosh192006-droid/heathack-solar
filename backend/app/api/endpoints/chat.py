from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
from app.services.gemini_service import gemini_service

router = APIRouter(prefix="/chat", tags=["Multilingual AI Advisory"])

class ChatExplainRequest(BaseModel):
    query: str = Field(..., description="User question (e.g. 'Why was this solar size recommended?')")
    context_payload: Dict[str, Any] = Field(..., description="Calculation results and scenario parameters")
    language: str = Field("en", description="Target language code: 'en' (English), 'hi' (Hindi), 'bn' (Bengali)")

class ChatExplainResponse(BaseModel):
    explanation: str
    language: str

@router.post("/explain", response_model=ChatExplainResponse)
async def explain_plan(req: ChatExplainRequest):
    """
    Explains verified calculation outputs, cooling evidence, or ranking criteria
    in Bengali, Hindi, or English.
    """
    try:
        reply = await gemini_service.explain_plan(
            context_payload=req.context_payload,
            query=req.query,
            language=req.language
        )
        return ChatExplainResponse(
            explanation=reply,
            language=req.language
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Advisory explanation failed: {str(e)}")
