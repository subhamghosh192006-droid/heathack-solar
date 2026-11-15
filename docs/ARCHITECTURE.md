# HeatHack Solar — System Architecture & Design

## 🏛️ High-Level System Architecture

HeatHack Solar adopts a decoupled, micro-service-ready architecture designed for rapid deployment, local determinism, and zero-shot AI integration without fine-tuning overhead.

```
+-----------------------------------------------------------------------------------+
|                                 REACT CLIENT                                     |
|  +-----------------------------------------------------------------------------+  |
|  | - Map Engine (Leaflet / MapLibre GL): Satellite Tile Viewport, GeoJSON Layers |  |
|  | - Interactive Canvas: Roof Polygon Editor, Virtual Solar Panel Drag & Drop   |  |
|  | - Mode Switcher: 'My Roof' (Individual) vs. 'My Neighbourhood' (Community)  |  |
|  | - Calculation Dashboards & Multilingual Advisory Chat (EN / HI / BN)         |  |
|  +-----------------------------------------------------------------------------+  |
+------------------------------------------^----------------------------------------+
                                           | HTTP / REST (JSON)
+------------------------------------------v----------------------------------------+
|                               FASTAPI BACKEND SERVICE                             |
|  +-----------------------------------------------------------------------------+  |
|  | API Routing Layer (/api/roof, /api/solar, /api/cooling, /api/bill, /api/chat) |  |
|  +-----------------------------------------------------------------------------+  |
|  | Core Computational Engines (Deterministic Code)                             |  |
|  |  * geo_engine.py      : Shapely planar polygon math, setbacks, panel packing|  |
|  |  * solar_engine.py    : Generation yields, PM Surya Ghar subsidy, payback   |  |
|  |  * cooling_engine.py  : Multi-criteria heat ranking, evidence matching, cost |  |
|  +-----------------------------------------------------------------------------+  |
|  | AI Integration Adapters (Zero-Shot / Foundation APIs)                       |  |
|  |  * SAM / SAM 2 Adapter: Prompt-based roof boundary segmentation             |  |
|  |  * Gemini Service     : Vision feature review, bill OCR, multilingual agent |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 🧩 Component Responsibilities

| Component | Technology | Primary Duty |
|---|---|---|
| **Frontend Map & UI** | React 18, TypeScript, Tailwind CSS, Leaflet | Map viewport, manual boundary editing, virtual panel drag/drop, before-and-after scenarios |
| **Backend API Gateway** | Python 3.10+, FastAPI, Pydantic | Validates requests, coordinates geospatial operations, serves structured calculations |
| **Geospatial Engine** | Shapely, PyProj, GeoPandas, Rasterio | Performs projection transforms (WGS84 $\rightarrow$ metric), applies polygon setbacks, computes usable area |
| **Solar Placement Engine** | Python geometric packing | Packs rectangular panel bounding boxes into arbitrary polygons with spacing and clearance constraints |
| **Roof Segmentation** | Pretrained SAM / SAM 2 | Generates mask polygons from positive point clicks or bounding boxes |
| **Vision & OCR Service** | Google Gemini Vision | Inspects satellite roof crops to suggest water tanks, stairwells, and structures; extracts utility bills |
| **AI Advisory Engine** | Google Gemini Multi-Turn | Formulates accessible, evidence-backed explanations in English, Hindi, and Bengali |
| **Cooling Engine** | Python statistical engine | Calculates MCDA vulnerability scores and budget projections for urban wards |

---

## 🔒 Security, Privacy & Data Compliance

1. **Map Tile Licensing:**
   - Visual tiles are displayed within the user's browser under standard mapping licenses (e.g. OpenStreetMap, Esri World Imagery, or licensed commercial providers).
   - Only explicitly user-selected roof bounds are processed for AI analysis.
2. **Personal Data & Utility Bills:**
   - Uploaded electricity bills are processed ephemeral-only: user identifiers (name, address, consumer ID) are discarded or redacted prior to Gemini processing.
   - Only numerical parameters (consumption kWh, sanctioned load kW, billing period) are retained for calculation session state.
3. **No Model Training:**
   - User roof boundaries and bill data are never used for training or model weight updates.

---

## 📡 API Interface Definitions

### 1. Roof Segmentation (`/api/roof/segment`)
- **Input:** Bounding box coordinates $[lat_{\min}, lon_{\min}, lat_{\max}, lon_{\max}]$ or click coordinate $[lat, lon]$.
- **Output:** GeoJSON Polygon representing roof outline with estimated confidence and planar area.

### 2. Obstruction Suggestions (`/api/roof/exclusions`)
- **Input:** Roof polygon and satellite image crop.
- **Output:** List of identified exclusions:
  ```json
  [
    {"type": "water_tank", "polygon": [[x1, y1], [x2, y2], ...], "confidence": 0.88},
    {"type": "stairwell", "polygon": [[x1, y1], [x2, y2], ...], "confidence": 0.94}
  ]
  ```

### 3. Solar Layout & Placement (`/api/solar/layout`)
- **Input:** Usable polygon geometry, panel dimensions ($l, w$), orientation angle (azimuth), inter-row spacing, setback margins.
- **Output:** Array of placed panel polygons, total panel count, unutilized roof area.

### 4. Solar Sizing & Financials (`/api/solar/calculate`)
- **Input:** Installed capacity (kWp), monthly consumption (kWh), retail tariff (₹), export credit (₹), assumed yield (default 120 kWh/kW/mo).
- **Output:** Generation estimates, PM Surya Ghar subsidy amount, net cost, net annual savings, simple payback years.

### 5. Neighbourhood Heat Ranking (`/api/cooling/rank`)
- **Input:** Ward or cluster GeoJSON with thermal indices and survey data, optional user weight parameters.
- **Output:** Prioritized list of clusters with intervention matches, evidence citations, household cost estimates, and survey requirement flags.

### 6. Multilingual Explanation (`/api/chat/explain`)
- **Input:** Calculation result payload, user prompt, requested language (`"en"`, `"hi"`, `"bn"`).
- **Output:** Grounded, factual explanation explaining the numbers without hallucinating or modifying totals.
