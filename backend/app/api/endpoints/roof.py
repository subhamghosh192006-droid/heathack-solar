from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Dict, Any, List
from app.services.geo_engine import RoofGeometryRequest, process_usable_geometry
from app.services.gemini_service import gemini_service

router = APIRouter(prefix="/roof", tags=["Roof Analysis"])

@router.post("/process", response_model=Dict[str, Any])
async def process_roof(req: RoofGeometryRequest):
    """
    Computes total roof area, applies perimeter safety setbacks, and subtracts confirmed exclusions.
    """
    try:
        data = process_usable_geometry(req)
        return {
            "total_area_sqm": data["total_area_sqm"],
            "usable_area_sqm": data["usable_area_sqm"],
            "usable_geojson": data["usable_geojson"],
            "exclusions_geojson": data["exclusions_geojson"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Geometry processing failed: {str(e)}")

@router.post("/review-features")
async def review_roof_features(file: UploadFile = File(None)):
    """
    Inspects roof satellite image via Gemini Vision to suggest visible features
    such as water tanks, stairwell mumties, and HVAC equipment.
    """
    image_bytes = None
    if file:
        image_bytes = await file.read()
    
    suggestions = await gemini_service.review_roof_obstructions(image_bytes)
    return {
        "status": "success",
        "suggestions": suggestions,
        "note": "User confirmation required before exclusions are finalized."
    }
