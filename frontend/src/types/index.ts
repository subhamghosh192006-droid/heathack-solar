export type PlanningMode = 'roof' | 'neighbourhood';
export type SupportedLanguage = 'en' | 'hi' | 'bn';

export interface RoofExclusion {
  id: string;
  type: string;
  label: string;
  area_sqm: number;
  confirmed: boolean;
}

export interface PlacedPanel {
  id: number;
  length_m: number;
  width_m: number;
  wattage: number;
  x: number;
  y: number;
  rotation: number;
}

export interface SolarCalculation {
  installed_capacity_kw: number;
  panel_count: number;
  monthly_generation_kwh: number;
  annual_generation_kwh: number;
  gross_cost_inr: number;
  subsidy_inr: number;
  net_cost_inr: number;
  annual_net_savings_inr: number;
  simple_payback_years: number;
  recommended_size_kw: number;
  recommendation_reason: string;
}

export interface NeighbourhoodCluster {
  cluster_id: string;
  name: string;
  surface_temp_lst_c: number;
  ndvi_green_index: number;
  predominant_roof_material: string;
  total_households: number;
  avg_roof_area_sqm: number;
  survey_completed: boolean;
  priority_score?: number;
  rank?: number;
  intervention?: string;
  indoor_cooling_estimate?: string;
  household_cost_inr?: number;
  total_budget_inr?: number;
  confidence?: string;
  survey_required_notes?: string;
}
