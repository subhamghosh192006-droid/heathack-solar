import os
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from app.services.cooling_engine import (
    NeighbourhoodClusterInput,
    CoolingWeights,
    RankedInterventionOutput,
    rank_neighbourhood_clusters
)

router = APIRouter(prefix="/cooling", tags=["Urban Heat & Cooling Planner"])

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"

@router.get("/pilot-data")
async def get_pilot_data() -> Dict[str, Any]:
    """
    Returns the baseline sample neighbourhood GeoJSON dataset with LST, NDVI, and building surveys.
    """
    path = DATA_DIR / "sample_neighbourhood.geojson"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Sample neighbourhood data not found.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("/evidence")
async def get_cooling_evidence() -> Dict[str, Any]:
    """
    Returns the evidence catalog of peer-reviewed cooling studies and baseline unit costs.
    """
    path = DATA_DIR / "cooling_evidence.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Cooling evidence catalog not found.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

class RankRequest(BaseModel):
    clusters: List[NeighbourhoodClusterInput]
    weights: CoolingWeights = CoolingWeights()

@router.post("/rank", response_model=List[RankedInterventionOutput])
async def rank_clusters(req: RankRequest):
    """
    Ranks neighbourhood clusters by heat vulnerability, matches evidence-based interventions,
    and calculates household and programme budgets.
    """
    try:
        return rank_neighbourhood_clusters(req.clusters, req.weights)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ranking failed: {str(e)}")
