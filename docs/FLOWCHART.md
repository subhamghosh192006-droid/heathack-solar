# Flowchart implementation

| User journey | Implementation | Status |
| --- | --- | --- |
| Open → locate → choose mode | Planning workspace, satellite context, address/coordinates/geolocation, mode switch | Working; network required for satellite/search |
| Click roof / draw boundary | Demo building opens metric editor; polygon drawing and vertex movement | Working in local metric plane |
| SAM outline → user confirms | Optional SAM point-prompt API; manual outline confirmation in UI | SAM requires separate setup and frontend integration |
| AI suggestions → exclusions | Optional Gemini feature endpoint; manual exclusion editing | Manual UI working, Gemini integration pending |
| Bill → extract → confirm | Manual period-based bill entry; optional Gemini extraction API | Manual UI working, API requires credentials and UI wiring |
| Usable geometry → scaled layout → validity loop | Geometry functions, setback, spacing, collision rejection, add/remove/rotate/move | Working for flat roofs and right-angle rectangles |
| Capacity → comparison → economics | Deterministic engine with editable inputs and feasible system table | Working; assumptions, not quotations |
| Heat + vegetation → survey → sufficient? | Synthetic dated-as-unavailable demo, aggregate surveys and provisional confidence | Real raster ingestion pending |
| Suitability → evidence → household cost | Intervention/material matching and coating arithmetic | Working; other packages require quotation |
| Ranking → budget | Adjustable need weights, survey status, funded household count | Working with synthetic inputs |
| Shared roof conflicts → before/after | Footprint review, original/proposed roof toggle, future canopy caveat | Concept review only; annual shade analysis deferred |
| Indoor cooling → explanation → export | Evidence-matched scenario, three-language solar explanation, HTML/JSON export | Working; no universal thermal reduction |
| Verification → pilot → local refinement | Checklist and paired observations saved/exported | Records working; scientific recalibration intentionally manual |

## Next steps for production use

1. Obtain licensed imagery permitting AI processing and a georeferencing transform.
2. Replace demo blocks with surveyed GeoJSON and validated building dimensions.
3. Load dated thermal rasters with acquisition date, cloud mask, resolution and vegetation context. Do not label a building temperature from coarse pixels as measured indoor conditions.
4. Deploy optional Python service on suitable hardware, configure model access, and wire authenticated upload/review UX to each endpoint.
5. Convert masks into georeferenced polygons, then send confirmed polygons to the exact geometry endpoint; preserve uncertainty and manual edits.
6. Establish local quotations, electrical constraints and eligibility checks.
7. Run matched pilot monitoring and review causal evidence before changing scenario assumptions.
