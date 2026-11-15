from fastapi import APIRouter, HTTPException
from app.services.geo_engine import PanelPlacementRequest, PanelPlacementResult, pack_solar_panels
from app.services.solar_engine import SolarCalcRequest, SolarCalcResult, calculate_solar_economics

router = APIRouter(prefix="/solar", tags=["Solar Sizing & Economics"])

@router.post("/layout", response_model=PanelPlacementResult)
async def create_panel_layout(req: PanelPlacementRequest):
    """
    Packs scaled virtual solar panels inside usable roof geometry,
    respecting exclusions, orientation azimuth, and maintenance clearance.
    """
    try:
        result = pack_solar_panels(req)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Panel layout failed: {str(e)}")

@router.post("/calculate", response_model=SolarCalcResult)
async def calculate_solar(req: SolarCalcRequest):
    """
    Computes capacity, monthly/annual generation, PM Surya Ghar subsidy,
    self-consumption savings, export credit, and simple payback.
    """
    try:
        return calculate_solar_economics(req)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Solar calculation failed: {str(e)}")
