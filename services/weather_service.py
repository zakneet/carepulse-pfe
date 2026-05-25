import json
from urllib import parse, request
from urllib.error import URLError, HTTPError


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def _is_bad_weather(weather_code: int, windspeed: float) -> bool:
    bad_weather_codes = {
        45, 48, 51, 53, 55, 56, 57,
        61, 63, 65, 66, 67,
        71, 73, 75, 77,
        80, 81, 82,
        85, 86,
        95, 96, 99,
    }
    return weather_code in bad_weather_codes or windspeed >= 40


def get_weather_recommendation(weather_code: int, windspeed: float) -> str:
    if _is_bad_weather(weather_code, windspeed):
        return "⚠️ Météo défavorable : il est recommandé de partir plus tôt pour votre rendez-vous."
    return "☀️ Météo favorable : déplacement normal possible."


def get_current_weather(lat: float, lon: float) -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "timezone": "auto",
    }

    try:
        url = f"{OPEN_METEO_URL}?{parse.urlencode(params)}"
        with request.urlopen(url, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
        current_weather = payload.get("current_weather") or {}
        weather_code = int(current_weather.get("weathercode", -1))
        windspeed = float(current_weather.get("windspeed", 0) or 0)

        return {
            "status": "success",
            "latitude": lat,
            "longitude": lon,
            "current_weather": {
                "temperature": current_weather.get("temperature"),
                "weathercode": current_weather.get("weathercode"),
                "windspeed": current_weather.get("windspeed"),
                "winddirection": current_weather.get("winddirection"),
                "time": current_weather.get("time"),
            },
            "weather_recommendation": get_weather_recommendation(weather_code, windspeed),
            "timezone": payload.get("timezone"),
            "status_code": 200,
        }
    except (URLError, HTTPError, TimeoutError, ValueError, OSError):
        return {
            "status": "error",
            "message": "Impossible de recuperer la meteo pour le moment.",
            "weather_recommendation": "Météo indisponible",
            "current_weather": {},
            "status_code": 502,
        }


def get_weather(city: str) -> dict:
    """
    Geocode a city name using Open-Meteo geocoding API then return the same
    structure as `get_current_weather` (with recommendation in French).
    """
    if not city:
        return {"status": "error", "message": "No city provided", "status_code": 400, "weather_recommendation": "Météo indisponible", "current_weather": {}}

    geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
    try:
        url = f"{geocode_url}?{parse.urlencode({'name': city, 'count': 1})}"
        with request.urlopen(url, timeout=8) as gresp:
            gpayload = json.loads(gresp.read().decode("utf-8"))
        results = gpayload.get("results") or []
        if not results:
            return {"status": "error", "message": "Ville introuvable", "status_code": 404, "weather_recommendation": "Météo indisponible", "current_weather": {}}

        first = results[0]
        lat = float(first.get("latitude", 0) or 0)
        lon = float(first.get("longitude", 0) or 0)

        # reuse existing function to fetch current weather
        res = get_current_weather(lat, lon)
        # add geocoded city name
        res["city"] = first.get("name")
        res["country"] = first.get("country")
        return res
    except (URLError, HTTPError, TimeoutError, ValueError, OSError):
        return {"status": "error", "message": "Geocodage échoué", "status_code": 502, "weather_recommendation": "Météo indisponible", "current_weather": {}}