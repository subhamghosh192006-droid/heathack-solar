# HeatHack Solar — Calculation Methodologies & Scientific Baselines

This document details all mathematical formulas, subsidy rules, financial assumptions, and empirical cooling references implemented in HeatHack Solar.

> **Key Tenet:** All calculations are performed in deterministic code. Large Language Models (Gemini) are used solely for explanation, translation, vision inspection, and document field extraction—never for arithmetic.

---

## ☀️ 1. Solar Rooftop Geometry & Placement Engine

### 1.1 Geographic Area Computation
Roof boundaries confirmed by the user are converted from geographic coordinates (WGS84, `EPSG:4326`) to an appropriate local Projected Coordinate System (e.g., UTM zone or Web Mercator `EPSG:3857` with geodesic latitude scale correction $\cos(\phi)$) for metric planar calculations.

$$\text{Area}_{\text{roof}} = \iint_{\text{Polygon}} dx\,dy$$

### 1.2 Usable Area & Exclusions
Usable roof area is calculated by subtracting verified structural exclusions (water tanks, stairwells, HVAC units) and applying perimeter and maintenance setbacks:

$$\text{Polygon}_{\text{setback}} = \text{Polygon}_{\text{roof}} \ominus \delta_{\text{boundary}}$$
$$\text{Polygon}_{\text{usable}} = \text{Polygon}_{\text{setback}} \setminus \left( \bigcup_{i} (\text{Exclusion}_i \oplus \delta_{\text{exclusion}}) \right)$$
$$\text{Area}_{\text{usable}} = \text{Area}(\text{Polygon}_{\text{usable}})$$

- Default boundary setback ($\delta_{\text{boundary}}$): $0.50 \text{ m}$
- Default maintenance walkway / exclusion buffer ($\delta_{\text{exclusion}}$): $0.50 \text{ m}$ to $1.00 \text{ m}$
- Rule of thumb capacity ceiling: $\approx 10 \text{ m}^2 \text{ per kW}$

### 1.3 Virtual Panel Layout Packing
Standard monocrystalline solar module specifications:
- Width ($w$): $1.00 \text{ m}$ to $1.13 \text{ m}$ (default $1.05 \text{ m}$)
- Length ($l$): $1.75 \text{ m}$ to $2.28 \text{ m}$ (default $2.00 \text{ m}$)
- Rated Wattage ($P_{\text{panel}}$): $450\text{--}550\text{ W}$ (default $500\text{ W}$)
- Inter-row spacing ($s_{\text{row}}$): $0.30\text{--}0.60 \text{ m}$ (for top-down maintenance & conceptual clearance)

For each candidate panel footprint $R_k$:
$$\forall k, \; R_k \subset \text{Polygon}_{\text{usable}}$$
$$\forall j \neq k, \; R_j \cap R_k = \emptyset$$

Installed DC Capacity ($C_{\text{kW}}$):
$$C_{\text{kW}} = \frac{N_{\text{panels}} \times P_{\text{panel}}}{1000}$$

---

## ⚡ 2. Solar Generation & Financial Model

### 2.1 Monthly & Annual Generation
- Initial planning yield: **$120 \text{ kWh per kW per month}$**
- Sensitivity bounds: **$100\text{--}140 \text{ kWh per kW per month}$**

$$\text{Gen}_{\text{monthly}} = C_{\text{kW}} \times 120 \quad [\text{kWh/month}]$$
$$\text{Gen}_{\text{annual}} = \text{Gen}_{\text{monthly}} \times 12 \quad [\text{kWh/year}]$$

*Note:* This represents an initial planning baseline for flat roofs under typical Indian insolation conditions. It does not replace site-specific irradiance simulation (such as PVWatts or PVsyst).

### 2.2 PM Surya Ghar: Muft Bijli Yojana Central Subsidy
In accordance with Government of India Ministry of New and Renewable Energy (MNRE) guidelines:

$$\text{Subsidy}(C_{\text{kW}}) = ₹30,000 \times \min(C_{\text{kW}}, 2) + ₹18,000 \times \min(\max(C_{\text{kW}} - 2, 0), 1)$$

| Capacity Bracket ($C_{\text{kW}}$) | Formula Breakdown | Central Subsidy (₹) |
|---|---|---|
| $0 < C \le 1\text{ kW}$ | $₹30,000 \times C$ | Up to ₹30,000 |
| $1 < C \le 2\text{ kW}$ | $₹30,000 \times C$ | Up to ₹60,000 |
| $C \ge 3\text{ kW}$ | $₹30,000 \times 2 + ₹18,000 \times 1$ | **₹78,000** (Capped) |

*Important:* The ₹78,000 cap means that adding capacity beyond 3 kW receives zero additional subsidy; recommendations evaluate whether export tariffs justify larger systems.

### 2.3 Installation Cost & Net Investment
Assuming a benchmark market installation cost of ₹55,000 to ₹65,000 per kW (default ₹60,000/kW):

$$\text{Cost}_{\text{gross}} = C_{\text{kW}} \times \text{Rate}_{\text{kW}}$$
$$\text{Cost}_{\text{net}} = \max\left(0, \text{Cost}_{\text{gross}} - \text{Subsidy}(C_{\text{kW}})\right)$$

### 2.4 Savings, Export Credits & Simple Payback
Let:
- $E_{\text{cons}}$: Monthly household consumption (kWh)
- $T_{\text{retail}}$: Retail electricity tariff (₹/kWh, e.g., ₹7.50/kWh)
- $T_{\text{export}}$: Net-metering export/feed-in tariff (₹/kWh, e.g., ₹2.50/kWh)
- $O\&M_{\text{annual}}$: Annual operations & maintenance (assumed 1% of gross capital cost)

Monthly breakdown:
$$\text{Units}_{\text{self}} = \min(E_{\text{cons}}, \text{Gen}_{\text{monthly}})$$
$$\text{Units}_{\text{export}} = \max(0, \text{Gen}_{\text{monthly}} - E_{\text{cons}})$$

$$\text{Savings}_{\text{annual}} = 12 \times \left( \text{Units}_{\text{self}} \times T_{\text{retail}} + \text{Units}_{\text{export}} \times T_{\text{export}} \right) - O\&M_{\text{annual}}$$

$$\text{Simple Payback (Years)} = \frac{\text{Cost}_{\text{net}}}{\text{Savings}_{\text{annual}}}$$

---

## 🌡️ 3. Urban Heat & Neighbourhood Cooling Planner

### 3.1 Separation of Thermal Quantities
HeatHack Solar strictly enforces the distinction between three different physical quantities:
1. **Land Surface Temperature ($T_{\text{surface}}$):** Radiometric skin temperature derived from satellite thermal sensors (Landsat 8/9 TIRS or Sentinel-3 SLSTR). Represents roof, pavement, and vegetation surfaces.
2. **Ambient Outdoor Air Temperature ($T_{\text{air, 2m}}$):** Ambient weather condition measured at 2 meters height.
3. **Indoor Air Temperature ($T_{\text{indoor}}$):** Thermal microclimate inside dwellings, heavily influenced by roof thermal resistance ($U$-value), ventilation, ceiling height, and orientation.

$$\Delta T_{\text{surface}} \neq \Delta T_{\text{indoor}}$$

Satellite surface temperature maps must **never** have indoor cooling estimations directly subtracted from them.

### 3.2 Evidence-Based Indoor Cooling Reference
Rather than using speculative mathematical cooling equations, HeatHack Solar matches interventions against documented empirical field research:

1. **Reflective Cool-Roof Coating on Metal/Tin Roofs:**
   - **Empirical Baseline:** Vellingiri et al. (2020), Mahila Housing Trust (Ahmedabad informal settlements, 16 monitoring households).
   - **Observed Result:** Reflective solar coatings with High Solar Reflectance Index (SRI > 100) on corrugated tin sheets reduced peak daytime mean indoor air temperatures by **$\approx 1.0^\circ\text{C}$** compared to uncoated tin control homes.
   - **Secondary Benchmark:** Ahmedabad Heat-Adaptation Study reported **$1.0\text{--}1.5^\circ\text{C}$** peak summer indoor reduction, with dependence on ventilation and building geometry.
   - **Standard Label:** `"Reference scenario: approximately 1°C lower daytime indoor temperature, based on a small Ahmedabad study. Local performance requires verification."`
2. **Ventilation Improvements:**
   - Empirical evidence shows that unverified passive vents (e.g. standard Airlite vents without active thermal pressure differentials) can paradoxically draw hot exterior air inward during peak afternoon hours.
   - **Standard Label:** `"Temperature reduction: assessment required. Airflow depends on diurnal outdoor conditions and openings."`
3. **Urban Trees & Vegetative Canopies:**
   - Cools primarily via shade and evapotranspiration.
   - Requires differentiating between newly planted saplings (0–3 years, minimal shade) and mature 10-year canopies.

### 3.3 Neighbourhood Vulnerability Scoring Index
Wards or census blocks are prioritized using an explicit, tunable Multi-Criteria Decision Analysis (MCDA) framework:

$$\text{Score}_{\text{priority}} = w_1 \cdot \tilde{T}_{\text{surface}} + w_2 \cdot (1 - \tilde{\text{NDVI}}) + w_3 \cdot M_{\text{tin/asbestos}} + w_4 \cdot V_{\text{socio-economic}}$$

Where:
- $\tilde{T}_{\text{surface}} \in [0, 1]$: Normalized Land Surface Temperature.
- $(1 - \tilde{\text{NDVI}}) \in [0, 1]$: Normalized green cover deficit.
- $M_{\text{tin/asbestos}} \in [0, 1]$: Proportion of heat-vulnerable roof construction.
- $V_{\text{socio-economic}} \in [0, 1]$: Vulnerability metric (low-income, density, elderly population).
- Default weights: $w_1 = 0.35, \, w_2 = 0.20, \, w_3 = 0.25, \, w_4 = 0.20$.

*Handling Incomplete Data:*
If socio-economic surveys or verified roof material classifications are unavailable, the system assigns a provisional score and marks the record:
$$\text{Status} = \text{"Survey required"} \quad \text{and} \quad \text{Confidence} = \text{"Low (Provisional)"}$$

### 3.4 Programme Costing & Budgeting
For cool-roof interventions:
$$\text{Cost}_{\text{household}} = (\text{Area}_{\text{roof}} \times \text{Rate}_{\text{coating}}) + \text{Cost}_{\text{prep}} + \text{Cost}_{\text{overhead}}$$

**Worked Illustrative Example (100 Households):**
- Average Roof Treatment Area: $40 \text{ m}^2$
- Installed High-SRI Coating Rate: $₹100 / \text{m}^2$ (includes 2 coats + primer)
- Surface Preparation & Cleaning: $₹1,000$ per home
- Direct Household Cost:
  $$\text{Cost}_{\text{household}} = (40 \times 100) + 1000 = ₹5,000$$
- Cluster Pilot Programme (100 Homes):
  $$\text{Budget}_{\text{base}} = 100 \times ₹5,000 = ₹5,00,000 \quad (₹5 \text{ Lakh})$$
- Programme Management & Thermal Monitoring (10%): $₹50,000$
- Total Programme Outlay: **₹5.50 Lakh**
