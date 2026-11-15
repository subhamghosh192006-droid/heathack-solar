from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Dict, Any, Optional
from app.services.gemini_service import gemini_service

router = APIRouter(prefix="/bill", tags=["Electricity Bill Extraction"])

@router.post("/extract")
async def extract_bill(
    file: Optional[UploadFile] = File(None),
    text_content: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """
    Extracts consumption, billing cycle, sanctioned load, and tariff from utility bills
    using Gemini OCR and structured parsing.
    """
    image_bytes = None
    if file:
        image_bytes = await file.read()
    
    extracted = await gemini_service.extract_bill_data(image_bytes=image_bytes, text_content=text_content)
    return {
        "status": "success",
        "data": extracted,
        "note": "Please review extracted values before using in financial models."
    }
