import math
import os
from typing import Dict, Tuple

from services.route_service import get_route
from services.weather_service import get_weather


AVG_SPEED_KMH = float(os.getenv("DEPARTURE_BASE_SPEED_KMH", "35"))
DEFAULT_CITY = os.getenv("DEPARTURE_DEFAULT_CITY", "Tunis")
DEFAULT_COORDS = {
    "tunis": (10.10, 36.80),
    "ariana": (10.19, 36.86),
    "ben arous": (10.19, 36.75),
    "sousse": (10.64, 35.83),
    "sfax": (10.76, 34.74),
}

WEATHER_BAD_CODES = {
    45, 48, 51, 53, 55, 56, 57,
    61, 63, 65, 66, 67,
    71, 73, 75, 77,
    80, 81, 82,
    85, 86,
    95, 96, 99,
}

WEATHER_MODERATE_CODES = {
    51, 53, 55,
    61, 63, 65,
    80, 81, 82,
}


def _haversine_km(start_coords: Tuple[float, float], end_coords: Tuple[float, float]) -> float:
    start_lon, start_lat = start_coords
    end_lon, end_lat = end_coords

    radius_km = 6371.0
    lon1 = math.radians(float(start_lon))
    lat1 = math.radians(float(start_lat))
    lon2 = math.radians(float(end_lon))
    lat2 = math.radians(float(end_lat))

    delta_lon = lon2 - lon1
    delta_lat = lat2 - lat1
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius_km * c


def _normalize_city(city: str | None) -> str:
    return str(city or DEFAULT_CITY).strip() or DEFAULT_CITY


def resolve_city_coordinates(city: str | None) -> Tuple[float, float]:
    normalized = _normalize_city(city).lower()
    for key, coords in DEFAULT_COORDS.items():
        if key in normalized:
            return coords
    return DEFAULT_COORDS.get(normalized, DEFAULT_COORDS[DEFAULT_CITY.lower()])


def _normal_duration_minutes(distance_km: float) -> float:
    return (float(distance_km) / AVG_SPEED_KMH) * 60.0


def _weather_penalty(weather_payload: Dict) -> float:
    if not weather_payload or weather_payload.get("status") != "success":
        return 0.0

    current_weather = weather_payload.get("current_weather") or {}
    try:
        weather_code = int(current_weather.get("weathercode", -1))
        windspeed = float(current_weather.get("windspeed", 0) or 0)
    except (TypeError, ValueError):
        return 0.0

    if weather_code in WEATHER_BAD_CODES or windspeed >= 45:
        return 0.20
    if weather_code in WEATHER_MODERATE_CODES or windspeed >= 30:
        return 0.10
    return 0.0


def _traffic_penalty(base_duration: float, traffic_duration: float) -> float:
    if base_duration <= 0 or traffic_duration <= 0:
        return 0.0

    ratio = traffic_duration / base_duration
    if ratio <= 1.20:
        return 0.0

    return round(min(max(ratio - 1.0, 0.10), 0.30), 2)


def _tone_from_penalties(weather_penalty: float, traffic_penalty: float, final_duration: float, base_duration: float) -> str:
    if final_duration > base_duration * 1.25:
        return "danger"
    if traffic_penalty > 0:
        return "warning"
    if weather_penalty > 0:
        return "warning"
    return "normal"


def _recommendation(weather_penalty: float, traffic_penalty: float, final_duration: float, base_duration: float) -> str:
    if final_duration > base_duration * 1.25:
        return "⚠️ Il est recommandé de partir plus tôt que prévu pour éviter retard (météo + trafic défavorables)."
    if traffic_penalty > 0 and weather_penalty == 0:
        return "🚗 Trafic dense actuellement, départ anticipé recommandé."
    if weather_penalty > 0 and traffic_penalty == 0:
        return "🌧 Conditions météo difficiles, prévoir du temps supplémentaire."
    if weather_penalty > 0 and traffic_penalty > 0:
        return "⚠️ Conditions météo et trafic défavorables, partez plus tôt que prévu."
    return "☀️ Conditions normales, départ standard suffisant."


def get_optimal_departure(start_coords: Tuple[float, float], end_coords: Tuple[float, float], city: str | None) -> Dict:
    """Return a combined departure assistant using weather and traffic signals."""
    try:
        route_result = get_route(start_coords, end_coords)
        route_ok = route_result.get("status") == "ok"

        if route_ok:
            distance_km = float(route_result.get("distance_km") or 0)
            traffic_duration = float(route_result.get("duration_min") or 0)
        else:
            distance_km = _haversine_km(start_coords, end_coords)
            traffic_duration = _normal_duration_minutes(distance_km)

        if distance_km <= 0:
            return {
                "status": "error",
                "recommendation": "Information de départ indisponible",
                "base_duration": None,
                "traffic_duration": None,
                "weather_penalty": None,
                "traffic_penalty": None,
                "final_duration": None,
                "tone": "normal",
            }

        base_duration = _normal_duration_minutes(distance_km)
        weather_payload = get_weather(_normalize_city(city))
        weather_penalty = round(_weather_penalty(weather_payload), 2)
        traffic_penalty = _traffic_penalty(base_duration, traffic_duration)
        final_duration = round(base_duration * (1 + weather_penalty + traffic_penalty), 2)

        return {
            "status": "ok",
            "base_duration": round(base_duration, 2),
            "traffic_duration": round(traffic_duration, 2),
            "weather_penalty": weather_penalty,
            "traffic_penalty": traffic_penalty,
            "final_duration": final_duration,
            "recommendation": _recommendation(weather_penalty, traffic_penalty, final_duration, base_duration),
            "tone": _tone_from_penalties(weather_penalty, traffic_penalty, final_duration, base_duration),
        }
    except Exception:
        return {
            "status": "error",
            "recommendation": "Information de départ indisponible",
            "base_duration": None,
            "traffic_duration": None,
            "weather_penalty": None,
            "traffic_penalty": None,
            "final_duration": None,
            "tone": "normal",
        }
