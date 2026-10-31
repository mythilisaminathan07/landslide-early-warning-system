
import httpx


WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(latitude, longitude):

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "rain,"
            "surface_pressure"
        ),
        "timezone": "Asia/Kolkata"
    }

    try:
        response = httpx.get(
            WEATHER_API_URL,
            params=params,
            timeout=15.0
        )

        response.raise_for_status()
        data = response.json()

        current = data.get("current")

        if not current:
            return {
                "available": False,
                "error": "Current weather data is unavailable"
            }

        return {
            "available": True,
            "source": "Open-Meteo",
            "observed_at": current.get("time"),
            "readings": {
                "temperature_c": current.get("temperature_2m"),
                "humidity_percent": current.get(
                    "relative_humidity_2m"
                ),
                "precipitation_mm": current.get(
                    "precipitation"
                ),
                "rain_mm": current.get("rain"),
                "pressure_hpa": current.get(
                    "surface_pressure"
                )
            }
        }

    except (httpx.HTTPError, ValueError) as error:
        return {
            "available": False,
            "error": str(error)
        }