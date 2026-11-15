"""
HeatHack Solar — Solar Engineering & Financial Calculation Engine
All calculations use deterministic code. Large Language Models (Gemini) do not calculate totals.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class SolarCalcRequest(BaseModel):
    usable_area_sqm: float = Field(..., gt=0, description="Net usable rooftop area in square meters")
    panel_count: Optional[int] = Field(None, ge=1, description="Number of virtual panels placed")
    panel_wattage: int = Field(500, ge=200, le=750, description="Rated wattage per panel in Watts")
    monthly_consumption_kwh: float = Field(250.0, ge=10.0, description="Monthly household electricity consumption in kWh")
    retail_tariff_inr: float = Field(7.50, ge=1.0, description="Household retail tariff in INR per kWh")
    export_tariff_inr: float = Field(2.50, ge=0.0, description="Discom export feed-in tariff in INR per kWh")
    monthly_yield_kwh_per_kw: float = Field(120.0, ge=90.0, le=160.0, description="Planning yield assumption (120 default, 100-140 sensitivity)")
    cost_per_kw_inr: float = Field(60000.0, ge=40000.0, description="Estimated gross cost per kW installed")
    sanctioned_load_kw: Optional[float] = Field(None, description="Current utility sanctioned electrical load in kW")

class SolarOptionComparison(BaseModel):
    system_size_kw: float
    panel_count: int
    gross_cost_inr: float
    eligible_subsidy_inr: float
    net_cost_inr: float
    monthly_generation_kwh: float
    annual_net_savings_inr: float
    simple_payback_years: float
    is_recommended: bool
    recommendation_reason: str

class SolarCalcResult(BaseModel):
    installed_capacity_kw: float
    panel_count: int
    monthly_generation_kwh: float
    annual_generation_kwh: float
    sensitivity_range: Dict[str, float]
    gross_installation_cost_inr: float
    eligible_subsidy_inr: float
    net_installation_cost_inr: float
    monthly_self_consumed_kwh: float
    monthly_exported_kwh: float
    annual_self_consumption_savings_inr: float
    annual_export_credit_inr: float
    annual_om_cost_inr: float
    annual_net_savings_inr: float
    simple_payback_years: float
    feasible_options: List[SolarOptionComparison]
    recommended_size_kw: float
    recommendation_explanation: str
    regulatory_notes: List[str]

def calculate_pm_surya_ghar_subsidy(capacity_kw: float) -> float:
    """
    Standard Central Residential Subsidy Calculation (PM Surya Ghar: Muft Bijli Yojana):
    Subsidy = ₹30,000 * min(kW, 2) + ₹18,000 * min(max(kW - 2, 0), 1)
    
    1 kW: ₹30,000
    2 kW: ₹60,000
    3 kW and above: ₹78,000 (Capped)
    """
    if capacity_kw <= 0:
        return 0.0
    
    tier1 = 30000.0 * min(capacity_kw, 2.0)
    tier2 = 18000.0 * min(max(capacity_kw - 2.0, 0.0), 1.0)
    return round(tier1 + tier2, 2)

def calculate_solar_economics(req: SolarCalcRequest) -> SolarCalcResult:
    """
    Performs full transparent calculations of generation, subsidy, net savings, and simple payback.
    """
    # 1. Determine Capacity
    if req.panel_count is not None and req.panel_count > 0:
        panels = req.panel_count
        capacity_kw = round((panels * req.panel_wattage) / 1000.0, 2)
    else:
        # Initial estimate rule of thumb: ~10 m² per kW
        approx_kw = max(1.0, round(req.usable_area_sqm / 10.0, 1))
        capacity_kw = approx_kw
        panels = int(round((capacity_kw * 1000.0) / req.panel_wattage))

    # 2. Generation Calculations (120 kWh/kW/month default; sensitivity range 100-140)
    monthly_gen = round(capacity_kw * req.monthly_yield_kwh_per_kw, 1)
    annual_gen = round(monthly_gen * 12.0, 1)
    
    sensitivity = {
        "conservative_100kwh": round(capacity_kw * 100.0 * 12.0, 1),
        "planning_default_120kwh": annual_gen,
        "optimistic_140kwh": round(capacity_kw * 140.0 * 12.0, 1)
    }

    # 3. Capital Cost and Central Subsidy
    gross_cost = round(capacity_kw * req.cost_per_kw_inr, 2)
    subsidy = calculate_pm_surya_ghar_subsidy(capacity_kw)
    net_cost = max(0.0, round(gross_cost - subsidy, 2))

    # 4. Self-Consumption vs Export Split
    # Does not assume all generated units offset retail tariff or that fixed charges disappear
    self_consumed_monthly = min(req.monthly_consumption_kwh, monthly_gen)
    exported_monthly = max(0.0, monthly_gen - req.monthly_consumption_kwh)

    annual_self_saving = round(self_consumed_monthly * 12.0 * req.retail_tariff_inr, 2)
    annual_export_credit = round(exported_monthly * 12.0 * req.export_tariff_inr, 2)
    
    # 1% gross cost for annual operations & maintenance (cleaning, inverter reserve)
    annual_om = round(gross_cost * 0.01, 2)
    
    annual_net_savings = round((annual_self_saving + annual_export_credit) - annual_om, 2)

    # 5. Simple Payback
    if annual_net_savings > 0:
        simple_payback = round(net_cost / annual_net_savings, 2)
    else:
        simple_payback = 999.0

    # 6. Compare System Sizes & Generate Recommendations
    # Options: 1 kW, 2 kW, 3 kW, and up to physical roof capacity limit
    max_physical_kw = max(1.0, req.usable_area_sqm / 8.5)
    size_candidates = [1.0, 2.0, 3.0]
    if max_physical_kw > 3.5:
        size_candidates.append(min(round(max_physical_kw, 1), 5.0))

    feasible_options: List[SolarOptionComparison] = []
    best_size = 1.0
    best_metric = -1e9
    
    for sz in sorted(list(set(size_candidates))):
        if sz > max_physical_kw:
            continue
        opt_panels = int(round((sz * 1000.0) / req.panel_wattage))
        opt_gross = round(sz * req.cost_per_kw_inr, 2)
        opt_sub = calculate_pm_surya_ghar_subsidy(sz)
        opt_net = max(0.0, round(opt_gross - opt_sub, 2))
        opt_m_gen = round(sz * req.monthly_yield_kwh_per_kw, 1)
        opt_self = min(req.monthly_consumption_kwh, opt_m_gen)
        opt_exp = max(0.0, opt_m_gen - req.monthly_consumption_kwh)
        opt_sav = round(12.0 * (opt_self * req.retail_tariff_inr + opt_exp * req.export_tariff_inr) - (opt_gross * 0.01), 2)
        opt_pb = round(opt_net / opt_sav, 2) if opt_sav > 0 else 999.0

        # Scoring heuristic: balanced between payback speed and high coverage of consumption
        coverage_ratio = min(1.2, opt_m_gen / max(1.0, req.monthly_consumption_kwh))
        score = (coverage_ratio * 100.0) - (opt_pb * 12.0)
        
        reason = f"{sz} kW system generates ~{opt_m_gen:.0f} kWh/month with ₹{opt_sub:,.0f} central subsidy."
        if sz == 2.0 and req.monthly_consumption_kwh <= 250:
            reason += " Optimal balance of consumption coverage and ₹60,000 maximum per-kW subsidy tier."
        elif sz == 3.0:
            reason += " Maximizes ₹78,000 subsidy cap. Ideal for higher consumption or air conditioning."

        is_best = False
        if score > best_metric:
            best_metric = score
            best_size = sz
            
        feasible_options.append(SolarOptionComparison(
            system_size_kw=sz,
            panel_count=opt_panels,
            gross_cost_inr=opt_gross,
            eligible_subsidy_inr=opt_sub,
            net_cost_inr=opt_net,
            monthly_generation_kwh=opt_m_gen,
            annual_net_savings_inr=opt_sav,
            simple_payback_years=opt_pb,
            is_recommended=False,
            recommendation_reason=reason
        ))

    # Mark the best option
    for opt in feasible_options:
        if opt.system_size_kw == best_size:
            opt.is_recommended = True

    rec_reason = (
        f"We recommend a {best_size:.1f} kW installation ({int(round(best_size*1000/req.panel_wattage))} panels) "
        f"based on your monthly consumption of {req.monthly_consumption_kwh:.0f} kWh and available usable roof area "
        f"of {req.usable_area_sqm:.1f} m². It captures ₹{calculate_pm_surya_ghar_subsidy(best_size):,.0f} in central subsidy "
        f"with an estimated payback period of {next((o.simple_payback_years for o in feasible_options if o.system_size_kw == best_size), 4.5)} years."
    )

    regulatory_notes = [
        "Subsidy amounts follow PM Surya Ghar: Muft Bijli Yojana guidelines (up to ₹78,000 for 3 kW+).",
        "PM Surya Ghar subsidy applies strictly to grid-tied solar systems and must NOT be applied to cool roofs or civil works.",
        "Actual generation depends on local solar irradiance, panel orientation, degradation, and shading.",
        "Concept layout — installer verification and structural load check required."
    ]

    return SolarCalcResult(
        installed_capacity_kw=capacity_kw,
        panel_count=panels,
        monthly_generation_kwh=monthly_gen,
        annual_generation_kwh=annual_gen,
        sensitivity_range=sensitivity,
        gross_installation_cost_inr=gross_cost,
        eligible_subsidy_inr=subsidy,
        net_installation_cost_inr=net_cost,
        monthly_self_consumed_kwh=round(self_consumed_monthly, 1),
        monthly_exported_kwh=round(exported_monthly, 1),
        annual_self_consumption_savings_inr=annual_self_saving,
        annual_export_credit_inr=annual_export_credit,
        annual_om_cost_inr=annual_om,
        annual_net_savings_inr=annual_net_savings,
        simple_payback_years=simple_payback,
        feasible_options=feasible_options,
        recommended_size_kw=best_size,
        recommendation_explanation=rec_reason,
        regulatory_notes=regulatory_notes
    )
