"""
HeatHack Solar — Geospatial & Virtual Panel Placement Engine
Calculates roof polygon area, setbacks, exclusions, and packs scaled solar panel bounding boxes.
"""

import math
from typing import List, Dict, Any, Tuple, Optional
from pydantic import BaseModel, Field
from shapely.geometry import Polygon, MultiPolygon, Point, box, mapping
from shapely.affinity import rotate, translate
from shapely.ops import unary_union

class GeoPoint(BaseModel):
    lng: float
    lat: float

class RoofGeometryRequest(BaseModel):
    boundary_coords: List[List[float]] = Field(..., description="Array of [lng, lat] coordinates defining the roof polygon")
    setback_distance_m: float = Field(0.5, ge=0.0, le=3.0, description="Perimeter safety setback distance in meters")
    exclusions: List[List[List[float]]] = Field(default_factory=list, description="Array of polygon coordinate loops for exclusions (tanks, stairwells)")
    exclusion_buffer_m: float = Field(0.5, ge=0.0, le=2.0, description="Buffer clearance around exclusions in meters")

class PanelPlacementRequest(BaseModel):
    boundary_coords: List[List[float]]
    setback_distance_m: float = 0.5
    exclusions: List[List[List[float]]] = []
    exclusion_buffer_m: float = 0.5
    panel_length_m: float = Field(2.0, ge=1.0, le=3.0)
    panel_width_m: float = Field(1.05, ge=0.5, le=2.0)
    panel_spacing_m: float = Field(0.35, ge=0.1, le=1.5)
    row_spacing_m: float = Field(0.50, ge=0.2, le=2.0)
    azimuth_deg: float = Field(0.0, ge=-180.0, le=180.0, description="Rotation angle in degrees (0 = South/True alignment)")

class PanelPlacementResult(BaseModel):
    roof_total_area_sqm: float
    usable_area_sqm: float
    total_panels_placed: int
    panel_footprint_area_sqm: float
    installation_area_sqm: float
    uncovered_usable_area_sqm: float
    panels_geojson: Dict[str, Any]
    usable_boundary_geojson: Dict[str, Any]
    exclusions_geojson: Dict[str, Any]
    label: str = "Concept layout — installer verification required."

def lat_lng_to_meters_scale(center_lat: float) -> Tuple[float, float]:
    """
    Computes approximate meters per degree longitude and latitude at a given latitude.
    """
    rad = math.radians(center_lat)
    m_per_deg_lat = 111132.92 - 559.82 * math.cos(2 * rad) + 1.175 * math.cos(4 * rad)
    m_per_deg_lng = 111412.84 * math.cos(rad) - 93.5 * math.cos(3 * rad)
    return m_per_deg_lng, m_per_deg_lat

def to_metric_polygon(coords: List[List[float]], ref_lat: float, ref_lng: float) -> Polygon:
    """Converts WGS84 [lng, lat] coordinates to local metric planar coordinates (meters relative to ref)."""
    m_lng, m_lat = lat_lng_to_meters_scale(ref_lat)
    metric_pts = [((pt[0] - ref_lng) * m_lng, (pt[1] - ref_lat) * m_lat) for pt in coords]
    return Polygon(metric_pts)

def to_wgs84_polygon(metric_poly: Polygon, ref_lat: float, ref_lng: float) -> Polygon:
    """Converts local metric coordinates back to WGS84 [lng, lat]."""
    m_lng, m_lat = lat_lng_to_meters_scale(ref_lat)
    wgs_pts = [(ref_lng + (pt[0] / m_lng), ref_lat + (pt[1] / m_lat)) for pt in metric_poly.exterior.coords]
    return Polygon(wgs_pts)

def process_usable_geometry(req: RoofGeometryRequest) -> Dict[str, Any]:
    """
    Computes total area, applies setbacks and subtracts exclusions.
    """
    if len(req.boundary_coords) < 3:
        raise ValueError("A polygon requires at least 3 coordinates.")
    
    ref_lng = req.boundary_coords[0][0]
    ref_lat = req.boundary_coords[0][1]
    
    # 1. Base roof polygon in meters
    roof_poly_m = to_metric_polygon(req.boundary_coords, ref_lat, ref_lng)
    if not roof_poly_m.is_valid:
        roof_poly_m = roof_poly_m.buffer(0)
    total_area_sqm = round(roof_poly_m.area, 2)

    # 2. Setback perimeter buffer (erode inwards)
    if req.setback_distance_m > 0:
        setback_poly_m = roof_poly_m.buffer(-req.setback_distance_m)
    else:
        setback_poly_m = roof_poly_m

    # 3. Buffer exclusions and union
    buffered_exclusions = []
    for excl in req.exclusions:
        if len(excl) >= 3:
            excl_poly = to_metric_polygon(excl, ref_lat, ref_lng)
            if not excl_poly.is_valid:
                excl_poly = excl_poly.buffer(0)
            if req.exclusion_buffer_m > 0:
                excl_poly = excl_poly.buffer(req.exclusion_buffer_m)
            buffered_exclusions.append(excl_poly)

    if buffered_exclusions:
        all_excl_m = unary_union(buffered_exclusions)
        usable_poly_m = setback_poly_m.difference(all_excl_m)
    else:
        all_excl_m = Polygon()
        usable_poly_m = setback_poly_m

    usable_area_sqm = round(max(0.0, usable_poly_m.area), 2)

    # Convert back to WGS84 for GeoJSON output
    usable_wgs = []
    if isinstance(usable_poly_m, Polygon) and not usable_poly_m.is_empty:
        usable_wgs.append(to_wgs84_polygon(usable_poly_m, ref_lat, ref_lng))
    elif isinstance(usable_poly_m, MultiPolygon):
        for p in usable_poly_m.geoms:
            if not p.is_empty:
                usable_wgs.append(to_wgs84_polygon(p, ref_lat, ref_lng))

    usable_geojson = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "properties": {"type": "usable_roof_area"}, "geometry": mapping(p)}
            for p in usable_wgs
        ]
    }

    exclusions_wgs = []
    if isinstance(all_excl_m, Polygon) and not all_excl_m.is_empty:
        exclusions_wgs.append(to_wgs84_polygon(all_excl_m, ref_lat, ref_lng))
    elif isinstance(all_excl_m, MultiPolygon):
        for p in all_excl_m.geoms:
            if not p.is_empty:
                exclusions_wgs.append(to_wgs84_polygon(p, ref_lat, ref_lng))

    exclusions_geojson = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "properties": {"type": "confirmed_exclusion"}, "geometry": mapping(p)}
            for p in exclusions_wgs
        ]
    }

    return {
        "ref_lat": ref_lat,
        "ref_lng": ref_lng,
        "roof_poly_m": roof_poly_m,
        "usable_poly_m": usable_poly_m,
        "total_area_sqm": total_area_sqm,
        "usable_area_sqm": usable_area_sqm,
        "usable_geojson": usable_geojson,
        "exclusions_geojson": exclusions_geojson
    }

def pack_solar_panels(req: PanelPlacementRequest) -> PanelPlacementResult:
    """
    Packs scaled rectangular panel footprints into usable polygon bounds.
    Respects exclusions, orientation angle, setbacks, and maintenance clearance.
    """
    geom_data = process_usable_geometry(RoofGeometryRequest(
        boundary_coords=req.boundary_coords,
        setback_distance_m=req.setback_distance_m,
        exclusions=req.exclusions,
        exclusion_buffer_m=req.exclusion_buffer_m
    ))

    ref_lat = geom_data["ref_lat"]
    ref_lng = geom_data["ref_lng"]
    usable_poly_m = geom_data["usable_poly_m"]
    total_area_sqm = geom_data["total_area_sqm"]
    usable_area_sqm = geom_data["usable_area_sqm"]

    if usable_poly_m.is_empty or usable_area_sqm < (req.panel_length_m * req.panel_width_m):
        return PanelPlacementResult(
            roof_total_area_sqm=total_area_sqm,
            usable_area_sqm=usable_area_sqm,
            total_panels_placed=0,
            panel_footprint_area_sqm=0.0,
            installation_area_sqm=0.0,
            uncovered_usable_area_sqm=usable_area_sqm,
            panels_geojson={"type": "FeatureCollection", "features": []},
            usable_boundary_geojson=geom_data["usable_geojson"],
            exclusions_geojson=geom_data["exclusions_geojson"]
        )

    # Rotate usable polygon by -azimuth for axis-aligned bounding box search
    rot_angle = req.azimuth_deg
    rot_usable = rotate(usable_poly_m, -rot_angle, origin=(0, 0))

    min_x, min_y, max_x, max_y = rot_usable.bounds
    step_x = req.panel_width_m + req.panel_spacing_m
    step_y = req.panel_length_m + req.row_spacing_m

    placed_panels_m: List[Polygon] = []
    
    y = min_y
    while y + req.panel_length_m <= max_y:
        x = min_x
        while x + req.panel_width_m <= max_x:
            # Candidate panel box (axis-aligned)
            p_box = box(x, y, x + req.panel_width_m, y + req.panel_length_m)
            # Rotate back to original angle
            placed_p = rotate(p_box, rot_angle, origin=(0, 0))
            
            # Check collision: must be completely inside usable polygon
            if usable_poly_m.contains(placed_p):
                # Check overlap with existing placed panels
                collision = any(placed_p.intersects(existing) for existing in placed_panels_m)
                if not collision:
                    placed_panels_m.append(placed_p)
            x += step_x
        y += step_y

    total_panels = len(placed_panels_m)
    single_panel_area = round(req.panel_length_m * req.panel_width_m, 2)
    single_installation_area = round(step_x * step_y, 2)
    
    panel_footprint_total = round(total_panels * single_panel_area, 2)
    installation_area_total = round(min(usable_area_sqm, total_panels * single_installation_area), 2)
    uncovered_usable_area = round(max(0.0, usable_area_sqm - panel_footprint_total), 2)

    # Convert placed panels to WGS84 GeoJSON features
    features = []
    for idx, p_m in enumerate(placed_panels_m):
        wgs_poly = to_wgs84_polygon(p_m, ref_lat, ref_lng)
        features.append({
            "type": "Feature",
            "id": f"panel_{idx + 1}",
            "properties": {
                "panel_id": idx + 1,
                "length_m": req.panel_length_m,
                "width_m": req.panel_width_m,
                "area_sqm": single_panel_area,
                "azimuth_deg": req.azimuth_deg,
                "status": "placed"
            },
            "geometry": mapping(wgs_poly)
        })

    return PanelPlacementResult(
        roof_total_area_sqm=total_area_sqm,
        usable_area_sqm=usable_area_sqm,
        total_panels_placed=total_panels,
        panel_footprint_area_sqm=panel_footprint_total,
        installation_area_sqm=installation_area_total,
        uncovered_usable_area_sqm=uncovered_usable_area,
        panels_geojson={"type": "FeatureCollection", "features": features},
        usable_boundary_geojson=geom_data["usable_geojson"],
        exclusions_geojson=geom_data["exclusions_geojson"]
    )
