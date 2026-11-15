# HeatHack Solar

**Plan solar on your roof. Prioritise cooling in your neighbourhood.**

A runnable planning MVP based on the supplied brief and flowchart. The interface is dependency-free JavaScript, HTML and CSS, with Leaflet for optional satellite context and an optional Python FastAPI service. No model training is required.

## Run the project

Install Node.js 20 or later, then from the project directory:

```sh
npm start
```

Open http://127.0.0.1:4173. No npm install or build step is needed for the planner.

```sh
npm test
```

The included tests cover subsidy boundaries, consumption/export calculations, non-positive payback, geometry, overlapping exclusions, collision checks, provisional ranking and budget arithmetic.

## Working features

- Two connected modes: My Roof and My Neighbourhood.
- Address search, coordinate entry and opt-in geolocation; Esri satellite imagery through Leaflet. Network failures leave the manual planner available.
- A clearly labelled illustrative map with a selectable demo roof.
- Metric roof editor: draw a polygon, move vertices, add/remove exclusions, add/move/rotate/remove panels, confirm the outline.
- Full-rectangle fit checks, boundary setbacks, exclusion avoidance, inter-panel spacing and sanctioned-load limits.
- Generation, separate self-consumption/export values, installation/subsidy/net costs and simple payback.
- Feasible system comparison; recommendation minimises positive simple payback within the generated grid candidates.
- Manual bill-period conversion and confirmation of electricity inputs.
- Cooling priority weights, missing-data flags, aggregate survey entry, costing and integer-household budget allocation.
- Roof-material/intervention-specific cooling evidence. No numerical estimate where evidence does not match.
- Relative cooling coverage scenarios, shared roof/shading review, before/after roof view.
- English, Hindi and Bengali **solar explanations** (interface remains English).
- Browser-local saving, JSON export/import, printable HTML combined report, verification checklist and pilot observations.

## Clear MVP boundaries

**The hosted app is a manual planning demo, not a production AI/geospatial service.** Its buildings and heat values are synthetic. It has no verified building dataset, acquisition date or cloud-filtered thermal layer. Satellite location context does not georeference the illustrative roof. Do not interpret a selected demo polygon as the actual building beneath a satellite marker.

The optional SAM/Gemini endpoints below are implemented but **not wired into the static UI or exercised with live credentials/checkpoints**. They return actual provider results when configured; they never fabricate an AI result. Bill entry and roof tracing in the app remain manual. Exact WGS84 geospatial calculation is available via the optional backend; the UI uses a local metre plane.

Not included: automated satellite-to-SAM tile capture, verified imagery-processing rights, raster thermal ingestion, full multilingual UI, production accounts/database, arbitrary panel angles, 3D/tilt/shading simulation, structural design, live quotations, subsidy approval, automatic calibration from pilot readings, or validated microclimate modelling.

## Optional FastAPI services

Use Python **3.11 or 3.12** for broad PyTorch compatibility. From the project root:

```sh
python -m venv .venv
# Activate .venv for your shell
pip install -r backend/requirements.txt
```

Set environment variables listed in `backend/.env.example`. The example file is not loaded automatically. Use a random `HEATHACK_API_TOKEN` with at least 24 characters. Set `GEMINI_API_KEY` and a currently supported `GEMINI_MODEL` only on the backend. Then:

```sh
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

API docs: http://127.0.0.1:8000/docs. Supply `Authorization: Bearer <HEATHACK_API_TOKEN>` for protected endpoints. Default CORS allows only the local frontend origin. Use HTTPS, proper user authentication, request size/concurrency limits and rate limiting before exposing this service beyond localhost.

| Endpoint | Input | Output |
| --- | --- | --- |
| GET `/health` | None | Configured capabilities, no secrets |
| POST `/api/bill/extract` | Multipart bill image/PDF + `consent=true` | Validated fields, requiring human confirmation |
| POST `/api/roof/features` | Image + `consent=true` | Visible-feature suggestions, no invented geometric exclusions |
| POST `/api/roof/segment` | Image + point `x`, `y` + imagery-rights confirmation | SAM binary PNG mask, score, dimensions; no fabricated geographic scale |
| POST `/api/geometry/usable` | WGS84 GeoJSON roof, exclusions and setback | UTM-projected area and usable geometry with unioned exclusions |

For SAM, install PyTorch appropriate to your hardware and Meta's `segment-anything` package from its official repository; download an official pretrained checkpoint. Set `SAM_CHECKPOINT`, matching `SAM_MODEL_TYPE`, and `SAM_DEVICE`. Model binaries are deliberately excluded from the project. The predictor is locked to avoid concurrent-image state corruption. Uploaded bytes stay in memory and are not written by this application. Gemini uploads go to Google only after a consent flag; review provider retention terms. Do not send map tiles to a model without processing rights.

## Calculation notes

- Default example: 6 × 500 W = 3 kW; 3 × 120 = 360 kWh/month.
- Default monthly demand: 350 kWh. Self-consumption share: 75%; retail ₹8/kWh, export ₹2.50/kWh.
- Self-use = min(generation × self-use share, demand). Exports = generation − self-use.
- Annual net savings = 12 × (self-use value + export credit) − annual maintenance.
- Fixed charges are not removed. Financing, degradation and tariff escalation are excluded.
- Standard subsidy assumption: ₹30,000/kW for first 2 kW + ₹18,000 for next 1 kW, capped at ₹78,000 and installation cost. Verify current eligibility; never apply to cooling work.
- Browser roof area: shoelace formula in local metres. Usable area: 0.1 m grid approximation, excluding setbacks and the union of exclusions. Displayed values are approximate.
- Spaced module area sums panel rectangle plus assigned spacing. It is not a complete installation access design. The installer must reserve access corridors.
- Priority weights are normalised. Missing vulnerability uses neutral 50/100 and requires survey, rather than appearing as low need.
- Coating cost = area × installed rate + preparation; programme overhead is separate. Rates include labour but are illustrative, not market quotes. Maintenance/recoating is not estimated.
- Reported thermal values are synthetic surface temperature, not indoor or outdoor air measurements. Scenario overlays never subtract an indoor estimate from surface temperature.

## Project layout

```text
dist/index.html       Application shell
dist/app.js           Workflows, state, editor, map, reports
dist/engine.js        Pure geometry, solar, ranking and budgeting functions
dist/styles.css       Responsive visual design
server.mjs            Minimal local static server
tests/engine.test.mjs Core numerical and geometry checks
backend/main.py       Optional FastAPI AI/geospatial adapters
backend/requirements.txt
docs/FLOWCHART.md     Implementation mapping and next integration steps
```

## Sources

- [PIB residential solar overview, 1 March 2024](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2010674)
- [Official PM Surya Ghar programme](https://www.pmsuryaghar.gov.in/)
- [EPA heat island measurement guidance](https://www.epa.gov/heatislands/measuring-heat-islands)
- [Vellingiri et al. (2020), Ahmedabad indoor cooling study](https://www.mahilahousingtrust.org/wp-content/uploads/2022/06/MHT_Combating-Climate-Change%E2%80%90induced-Heat-Stress.pdf)
- [Meta Segment Anything](https://github.com/facebookresearch/segment-anything)
- [Gemini structured output documentation](https://ai.google.dev/gemini-api/docs/structured-output)

## Validation status

Core Node tests and JavaScript syntax checks run locally. Python adapter source is syntax-checked only; no model checkpoint, Gemini credentials or verified geospatial dataset was supplied. Local browser QA could not reach the local preview server from the browser tool. Do not claim field-validated estimates.
