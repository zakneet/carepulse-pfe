from __future__ import annotations

import math
import os
import json
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any, Dict, Optional, Tuple, Union
from urllib import error, parse, request

try:
    from services.weather_service import get_current_weather
except Exception:  # pragma: no cover - optional dependency chain
    get_current_weather = None


AVG_SPEED_KMH = float(os.getenv("TRAFFIC_BASE_SPEED_KMH", "35"))
TRAFFIC_THRESHOLD_PERCENT = float(os.getenv("TRAFFIC_THRESHOLD_PERCENT", "20"))
TRAFFIC_MEDIUM_THRESHOLD_PERCENT = float(os.getenv("TRAFFIC_MEDIUM_THRESHOLD_PERCENT", "10"))
ARRIVAL_BUFFER_MINUTES = int(os.getenv("TRAFFIC_ARRIVAL_BUFFER_MINUTES", "5"))
DEFAULT_MESSAGE = "Information trafic indisponible"
DEFAULT_START_COORDS = (
    float(os.getenv("DEFAULT_START_LON", "10.10")),
    float(os.getenv("DEFAULT_START_LAT", "36.80")),
)
ORS_API_KEY = os.getenv("ORS_API_KEY", "")
ORS_BASE_URL = os.getenv("ORS_BASE_URL", "https://api.openrouteservice.org").rstrip("/")
ORS_PROFILE = os.getenv("ORS_PROFILE", "driving-car")
DEFAULT_CLINIC_ADDRESS = os.getenv("CLINIC_ADDRESS", "Clinique OptiClinic, Tunis, Tunisie")
REQUEST_TIMEOUT_SECONDS = float(os.getenv("ORS_REQUEST_TIMEOUT_SECONDS", "10"))


def _error_response(message: str = DEFAULT_MESSAGE) -> Dict[str, Any]:
    return {
        "status": "error",
        "message": message,
        "recommendation": message,
        "distance_km": None,
        "duration_normal": None,
        "duration_current": None,
        "traffic_delay_minutes": None,
        "traffic_delay_percent": None,
        "traffic_level": "unknown",
        "departure_time": None,
        "should_notify": False,
        "traffic_available": False,
        "weather_recommendation": None,
        "weather_is_bad": False,
    }


def _normalize_coords(coords: Tuple[float, float]) -> Tuple[float, float]:
    longitude, latitude = coords
    return float(longitude), float(latitude)


def _haversine_km(start_coords: Tuple[float, float], end_coords: Tuple[float, float]) -> float:
    """Compute a simple geographic distance when ORS is unavailable."""
    start_lon, start_lat = _normalize_coords(start_coords)
    end_lon, end_lat = _normalize_coords(end_coords)
    radius_km = 6371.0
    delta_lat = math.radians(end_lat - start_lat)
    delta_lon = math.radians(end_lon - start_lon)
    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(math.radians(start_lat))
        * math.cos(math.radians(end_lat))
        * math.sin(delta_lon / 2) ** 2
    )
    return radius_km * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


def _fallback_route_summary(start_coords: Tuple[float, float], end_coords: Tuple[float, float]) -> Dict[str, Any]:
    """Fallback route estimate used when OpenRouteService is missing or unreachable."""
    distance_km = _haversine_km(start_coords, end_coords)
    if distance_km <= 0:
        return {"status": "error", "message": "Trajet introuvable"}

    # Slightly conservative road factor to approximate street routing.
    road_distance_km = round(distance_km * 1.22, 2)
    duration_min = round((road_distance_km / max(AVG_SPEED_KMH, 1.0)) * 60.0, 2)
    return {
        "status": "ok",
        "distance_km": road_distance_km,
        "duration_min": duration_min,
        "route_source": "fallback_estimation",
    }


def _minutes_to_hhmm(minutes: int) -> str:
    minutes = minutes % (24 * 60)
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _parse_appointment_time(appointment_time: Union[str, datetime, None]) -> Optional[datetime]:
    if appointment_time is None:
        return None

    if isinstance(appointment_time, datetime):
        return appointment_time

    value = str(appointment_time).strip()
    if not value:
        return None

    iso_candidates = [value, value.replace(" ", "T")]
    for candidate in iso_candidates:
        try:
            return datetime.fromisoformat(candidate)
        except ValueError:
            continue

    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%H:%M", "%H:%M:%S"):
        try:
            parsed = datetime.strptime(value, fmt)
            if fmt.startswith("%H:%M"):
                today = datetime.now().date()
                return datetime.combine(today, parsed.time())
            return parsed
        except ValueError:
            continue

    return None


@lru_cache(maxsize=256)
def _geocode_address(address: str) -> Optional[Dict[str, Any]]:
    cleaned_address = (address or "").strip()
    if not cleaned_address or not ORS_API_KEY:
        return None

    url = f"{ORS_BASE_URL}/geocode/search?{parse.urlencode({'text': cleaned_address, 'api_key': ORS_API_KEY, 'size': 1})}"
    with request.urlopen(url, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        payload = json.loads(response.read().decode('utf-8'))
    features = payload.get("features") or []
    if not features:
        return None

    feature = features[0]
    geometry = feature.get("geometry") or {}
    coordinates = geometry.get("coordinates") or []
    if len(coordinates) < 2:
        return None

    properties = feature.get("properties") or {}
    return {
        "label": properties.get("label") or cleaned_address,
        "city": properties.get("locality") or properties.get("region") or properties.get("country"),
        "country": properties.get("country"),
        "coordinates": (float(coordinates[0]), float(coordinates[1])),
    }


def _route_summary(start_coords: Tuple[float, float], end_coords: Tuple[float, float]) -> Dict[str, Any]:
    if not ORS_API_KEY:
        return _fallback_route_summary(start_coords, end_coords)

    start_lon, start_lat = _normalize_coords(start_coords)
    end_lon, end_lat = _normalize_coords(end_coords)

    body = json.dumps({
        "coordinates": [[start_lon, start_lat], [end_lon, end_lat]],
        "instructions": False,
        "geometry": True,
    }).encode('utf-8')
    req = request.Request(
        f"{ORS_BASE_URL}/v2/directions/{ORS_PROFILE}/geojson",
        data=body,
        headers={"Authorization": ORS_API_KEY, "Content-Type": "application/json"},
        method='POST',
    )
    try:
        with request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode('utf-8'))
    except (error.URLError, error.HTTPError, TimeoutError, ValueError):
        return _fallback_route_summary(start_coords, end_coords)

    features = payload.get("features") or []
    if not features:
        return {"status": "error", "message": "Trajet introuvable"}

    summary = (features[0].get("properties") or {}).get("summary") or {}
    distance_m = summary.get("distance")
    duration_s = summary.get("duration")

    if distance_m is None or duration_s is None:
        return {"status": "error", "message": "Résumé de trajet indisponible"}

    return {
        "status": "ok",
        "distance_km": round(float(distance_m) / 1000.0, 2),
        "duration_min": round(float(duration_s) / 60.0, 2),
        "route_source": "openrouteservice",
    }


def _traffic_multiplier(appointment_dt: Optional[datetime]) -> float:
    if not appointment_dt:
        return 1.0

    weekday = appointment_dt.weekday()
    hour = appointment_dt.hour

    if weekday < 5 and ((7 <= hour < 9) or (16 <= hour < 19)):
        return 1.35
    if weekday < 5 and 12 <= hour < 14:
        return 1.15
    if weekday >= 5 and (10 <= hour < 12 or 16 <= hour < 19):
        return 1.12
    return 1.0


def _weather_is_bad(weather_payload: Optional[Dict[str, Any]]) -> bool:
    if not weather_payload:
        return False

    recommendation = str(weather_payload.get("weather_recommendation") or "").lower()
    current_weather = weather_payload.get("current_weather") or {}
    weather_code = current_weather.get("weathercode")
    windspeed = float(current_weather.get("windspeed") or 0)

    bad_weather_codes = {
        45, 48, 51, 53, 55, 56, 57,
        61, 63, 65, 66, 67,
        71, 73, 75, 77,
        80, 81, 82,
        85, 86,
        95, 96, 99,
    }

    if isinstance(weather_code, int) and weather_code in bad_weather_codes:
        return True
    if windspeed >= 40:
        return True
    return "défavorable" in recommendation or "defavorable" in recommendation


def _build_recommendation(
    traffic_level: str,
    departure_time: Optional[str],
    traffic_delay_minutes: float,
    weather_is_bad: bool,
) -> str:
    if weather_is_bad and traffic_level == "dense":
        return "⚠️ Mauvais temps et circulation dense : prévoyez un départ anticipé."

    if traffic_level == "dense":
        early_minutes = max(5, int(math.ceil(traffic_delay_minutes)))
        return f"Trafic dense détecté : il est recommandé de partir {early_minutes} minutes plus tôt."

    if traffic_level == "moyen":
        early_minutes = max(3, int(math.ceil(traffic_delay_minutes)))
        if departure_time:
            return f"Circulation modérée : partez vers {departure_time} pour arriver à temps."
        return f"Trafic modéré : il est recommandé de partir {early_minutes} minutes plus tôt."

    if departure_time:
        return f"Circulation fluide : partez à {departure_time} pour arriver à temps."
    return "Circulation fluide : départ normal possible."


def _compose_notice(
    start_coords: Tuple[float, float],
    end_coords: Tuple[float, float],
    appointment_time: Union[str, datetime, None],
    start_label: str,
    end_label: str,
    weather_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    route_result = _route_summary(start_coords, end_coords)
    if route_result.get("status") != "ok":
        return _error_response(route_result.get("message", DEFAULT_MESSAGE))

    appointment_dt = _parse_appointment_time(appointment_time)
    duration_normal = float(route_result.get("duration_min") or 0)
    distance_km = float(route_result.get("distance_km") or 0)
    if duration_normal <= 0 or distance_km <= 0:
        return _error_response()

    duration_current = max(duration_normal, duration_normal * _traffic_multiplier(appointment_dt))
    traffic_delay_minutes = max(0.0, duration_current - duration_normal)
    traffic_delay_percent = round((traffic_delay_minutes / duration_normal) * 100.0, 2) if duration_normal else 0.0

    if traffic_delay_percent >= TRAFFIC_THRESHOLD_PERCENT:
        traffic_level = "dense"
    elif traffic_delay_percent >= TRAFFIC_MEDIUM_THRESHOLD_PERCENT:
        traffic_level = "moyen"
    else:
        traffic_level = "fluide"

    departure_time = None
    if appointment_dt:
        departure_dt = appointment_dt - timedelta(minutes=duration_current + ARRIVAL_BUFFER_MINUTES)
        departure_time = departure_dt.strftime("%H:%M")

    weather_is_bad = _weather_is_bad(weather_payload)
    recommendation = _build_recommendation(traffic_level, departure_time, traffic_delay_minutes, weather_is_bad)

    should_notify = weather_is_bad or traffic_level in {"moyen", "dense"}
    notification_title = "Trajet vers la clinique"
    if weather_is_bad and traffic_level == "dense":
        notification_title = "Attention au départ"

    return {
        "status": "ok",
        "patient_address": start_label,
        "clinic_address": end_label,
        "distance_km": round(distance_km, 2),
        "duration_normal": round(duration_normal, 2),
        "duration_current": round(duration_current, 2),
        "traffic_delay_minutes": round(traffic_delay_minutes, 2),
        "traffic_delay_percent": traffic_delay_percent,
        "traffic_level": traffic_level,
        "departure_time": departure_time,
        "recommendation": recommendation,
        "message": recommendation,
        "should_notify": should_notify,
        "traffic_available": True,
        "weather_recommendation": (weather_payload or {}).get("weather_recommendation"),
        "weather_is_bad": weather_is_bad,
        "notification_title": notification_title,
        "notification_body": recommendation,
        "checked_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "route_source": route_result.get("route_source", "openrouteservice"),
    }


def _get_weather_payload_for_coords(coords: Optional[Tuple[float, float]]) -> Optional[Dict[str, Any]]:
    if not coords or get_current_weather is None:
        return None

    try:
        longitude, latitude = coords
        return get_current_weather(latitude, longitude)
    except Exception:
        return None


def get_travel_notice(
    patient_address: Union[str, Tuple[float, float]],
    clinic_address: Union[str, Tuple[float, float]],
    appointment_time: Union[str, datetime, None],
) -> Dict[str, Any]:
    """Return a travel notice for a patient-clinic trip.

    When strings are provided, they are geocoded via OpenRouteService.
    When coordinate tuples are provided, the route is computed directly.
    """
    try:
        if isinstance(patient_address, tuple) and isinstance(clinic_address, tuple):
            start_coords = _normalize_coords(patient_address)
            end_coords = _normalize_coords(clinic_address)
            weather_payload = _get_weather_payload_for_coords(end_coords)
            return _compose_notice(start_coords, end_coords, appointment_time, "Point de départ", "Clinique", weather_payload)

        patient_text = str(patient_address or "").strip()
        clinic_text = str(clinic_address or DEFAULT_CLINIC_ADDRESS).strip()
        if not patient_text or not clinic_text:
            return _error_response("Adresse patient ou clinique manquante")

        patient_geo = _geocode_address(patient_text)
        clinic_geo = _geocode_address(clinic_text)
        if not patient_geo or not clinic_geo:
            return _error_response("Impossible de géocoder les adresses fournies")

        weather_payload = _get_weather_payload_for_coords(clinic_geo["coordinates"])
        return _compose_notice(
            patient_geo["coordinates"],
            clinic_geo["coordinates"],
            appointment_time,
            patient_geo["label"],
            clinic_geo["label"],
            weather_payload,
        )
    except Exception:
        return _error_response()


def get_traffic_notice(start_coords: Tuple[float, float], end_coords: Tuple[float, float]) -> Dict[str, Any]:
    """Backward-compatible helper used by legacy appointment pages."""
    return get_travel_notice(start_coords, end_coords, None)


def get_default_start_coords() -> Tuple[float, float]:
    return DEFAULT_START_COORDS
