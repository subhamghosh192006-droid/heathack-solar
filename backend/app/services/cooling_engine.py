"""
HeatHack Solar — Neighbourhood Urban Heat & Cooling Priority Planning Engine
Implements evidence-based cooling benchmarks, survey gap tracking, and municipal programme budgeting.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class CoolingWeights(BaseModel):
    heat_exposure_weight: float = Field(0.35, ge=0.0, le=1.0)
    vegetation_deficit_weight: float = Field(0.20, ge=0.0, le=1.0)
    roof_material_vulnerability_weight: float = Field(0.25, ge=0.0, le=1.0)
    socioeconomic_vulnerability_weight: float = Field(0.20, ge=0.0, le=1.0)

class NeighbourhoodClusterInput(BaseModel):
    cluster_id: str
    name: str
    surface_temp_lst_c: float
    ndvi_green_index: float
    predominant_roof_material: str  # "corrugated_tin", "asbestos", "flat_concrete", "tiles"
    total_households: int
    avg_roof_area_sqm: float = 40.0
    survey_completed: bool = True
    vulnerability_index_raw: Optional[float] = 0.5  # 0 to 1
    installed_coating_rate_sqm: float = 100.0  # INR
    prep_cost_per_household: float = 1000.0    # INR
    programme_overhead_percent: float = 10.0

class RankedInterventionOutput(BaseModel):
    rank: int
    cluster_id: str
    name: str
    priority_score: float
    intervention_type: str
    households_reached: int
    estimated_household_cost_inr: float
    total_programme_budget_inr: float
    indoor_cooling_estimate: str
    evidence_citation: str
    confidence: str
    next_action: str
    survey_required_notes: Optional[str]
    satellite_lst_c: float
    caveats: List[str]

# Evidence references
EVIDENCE_TIN_COOL_ROOF = (
    "Reference scenario: approximately 1°C lower daytime indoor temperature, "
    "based on a small Ahmedabad study (Vellingiri et al., 2020 / MHT). Local performance requires verification."
)
EVIDENCE_ASSESSMENT_REQUIRED = (
    "Temperature reduction: assessment required. Airflow and cooling depend on opening orientations, "
    "ceiling height, and diurnal temperature swings."
)

def evaluate_cluster_intervention(cluster: NeighbourhoodClusterInput, weights: CoolingWeights) -> RankedInterventionOutput:
    """
    Computes priority score, matches scientific cooling evidence, and estimates household and programme costs.
    """
    # 1. Normalize Factors
    # Surface temperature: 35C -> 0.0, 50C -> 1.0
    norm_lst = min(1.0, max(0.0, (cluster.surface_temp_lst_c - 35.0) / 15.0))
    # Vegetation deficit: NDVI 0.4 -> 0.0 deficit, NDVI 0.0 -> 1.0 deficit
    norm_veg_deficit = min(1.0, max(0.0, 1.0 - (cluster.ndvi_green_index / 0.4)))
    
    # Roof material vulnerability
    material_scores = {
        "corrugated_tin": 1.0,
        "asbestos": 0.9,
        "clay_tiles": 0.5,
        "flat_concrete": 0.4
    }
    mat_factor = material_scores.get(cluster.predominant_roof_material.lower(), 0.5)

    # Socio-economic vulnerability (if survey missing, use provisional default and mark flag)
    survey_notes = None
    confidence = "High (Field Surveyed)"
    next_action = "Pilot implementation & vendor quote"
    
    if not cluster.survey_completed:
        socio_factor = 0.65  # Provisional assumption
        confidence = "Low (Provisional - Survey Required)"
        next_action = "Conduct on-ground structural & socio-economic survey"
        survey_notes = "Missing confirmed household income, roof load strength, and tenancy status."
    else:
        socio_factor = cluster.vulnerability_index_raw or 0.5

    # Composite Priority Score
    tot_weight = (
        weights.heat_exposure_weight +
        weights.vegetation_deficit_weight +
        weights.roof_material_vulnerability_weight +
        weights.socioeconomic_vulnerability_weight
    ) or 1.0

    priority_score = round((
        norm_lst * weights.heat_exposure_weight +
        norm_veg_deficit * weights.vegetation_deficit_weight +
        mat_factor * weights.roof_material_vulnerability_weight +
        socio_factor * weights.socioeconomic_vulnerability_weight
    ) / tot_weight, 3)

    # 2. Intervention Selection & Evidence Matching
    if cluster.predominant_roof_material in ("corrugated_tin", "asbestos"):
        intervention_type = "Cool-Roof Reflective Coating (High-SRI)"
        indoor_cooling = EVIDENCE_TIN_COOL_ROOF
        evidence_cite = "Vellingiri et al., 2020 (Mahila Housing Trust, 16 households, Ahmedabad)"
    elif cluster.predominant_roof_material == "flat_concrete":
        intervention_type = "Cool-Roof Barrier & Solar PV Co-Existence"
        indoor_cooling = "Reference scenario: approx. 0.5°C to 1.2°C indoor ceiling temperature dampening."
        evidence_cite = "Ahmedabad Heat Adaptation Study (2021)"
    else:
        intervention_type = "Ventilation Audit & Shading Assessment"
        indoor_cooling = EVIDENCE_ASSESSMENT_REQUIRED
        evidence_cite = "EPA Heat Island Reduction Guidelines"

    # 3. Budgeting Arithmetic
    # Household cost = treatment area * installed coating rate + additional prep
    household_direct_cost = round(
        (cluster.avg_roof_area_sqm * cluster.installed_coating_rate_sqm) + cluster.prep_cost_per_household, 2
    )
    base_cluster_budget = household_direct_cost * cluster.total_households
    overhead_amount = round(base_cluster_budget * (cluster.programme_overhead_percent / 100.0), 2)
    total_budget = round(base_cluster_budget + overhead_amount, 2)

    caveats = [
        "Satellite surface temperature reflects ground/roof skin temperature and is NOT equal to indoor air temperature.",
        "PM Surya Ghar solar subsidies must NOT be applied to cool-roof coating or ventilation works.",
        "Recoating or washing cycle recommended every 3 years to maintain high Solar Reflectance Index (SRI)."
    ]

    return RankedInterventionOutput(
        rank=0,  # Assigned after sorting
        cluster_id=cluster.cluster_id,
        name=cluster.name,
        priority_score=priority_score,
        intervention_type=intervention_type,
        households_reached=cluster.total_households,
        estimated_household_cost_inr=household_direct_cost,
        total_programme_budget_inr=total_budget,
        indoor_cooling_estimate=indoor_cooling,
        evidence_citation=evidence_cite,
        confidence=confidence,
        next_action=next_action,
        survey_required_notes=survey_notes,
        satellite_lst_c=cluster.surface_temp_lst_c,
        caveats=caveats
    )

def rank_neighbourhood_clusters(clusters: List[NeighbourhoodClusterInput], weights: CoolingWeights) -> List[RankedInterventionOutput]:
    """
    Ranks clusters in descending order of priority need.
    """
    outputs = [evaluate_cluster_intervention(c, weights) for c in clusters]
    outputs.sort(key=lambda x: x.priority_score, reverse=True)
    
    for idx, item in enumerate(outputs):
        item.rank = idx + 1
        
    return outputs
