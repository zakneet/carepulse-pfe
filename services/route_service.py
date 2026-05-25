import os
from typing import Any, Dict, Tuple

try:
    import openrouteservice
except Exception:  # pragma: no cover - fallback when dependency is unavailable
    openrouteservice = None


ORS_API_KEY = os.getenv("ORS_API_KEY")
ORS_PROFILE = os.getenv("ORS_PROFILE", "driving-car")


def _error_response(message: str = "Route unavailable") -> Dict[str, Any]:
    return {
        "status": "error",
        "message": message,
        "distance_km": None,
        "duration_min": None,
    }


def _normalize_coords(coords: Tuple[float, float]) -> Tuple[float, float]:
    longitude, latitude = coords
    return float(longitude), float(latitude)


def get_route(start_coords: Tuple[float, float], end_coords: Tuple[float, float]) -> Dict[str, Any]:
    """Return route distance/duration between two coordinate pairs.

    Coordinates must be provided as (longitude, latitude).
    """
    if not ORS_API_KEY or openrouteservice is None:
        return _error_response()

    try:
        start_lon, start_lat = _normalize_coords(start_coords)
        end_lon, end_lat = _normalize_coords(end_coords)

        client = openrouteservice.Client(key=ORS_API_KEY)
        payload = client.directions(
            coordinates=[[start_lon, start_lat], [end_lon, end_lat]],
            profile=ORS_PROFILE,
            format="geojson",
            geometry=True,
            instructions=False,
        )

        feature = (payload.get("features") or [{}])[0]
        properties = feature.get("properties") or {}
        summary = properties.get("summary") or {}

        distance_m = summary.get("distance")
        duration_s = summary.get("duration")

        if distance_m is None or duration_s is None:
            route = (payload.get("routes") or [{}])[0]
            summary = route.get("summary") or {}
            distance_m = summary.get("distance")
            duration_s = summary.get("duration")

        if distance_m is None or duration_s is None:
            return _error_response()

        geometry = None
        feature_geometry = feature.get("geometry") or {}
        if isinstance(feature_geometry, dict):
            geometry = feature_geometry.get("coordinates")

        if geometry is None:
            geometry = (payload.get("routes") or [{}])[0].get("geometry")

        result = {
            "status": "ok",
            "distance_km": round(float(distance_m) / 1000.0, 2),
            "duration_min": round(float(duration_s) / 60.0, 2),
        }
        if geometry:
            result["route"] = geometry

        return result
    except Exception:
        return _error_response()
