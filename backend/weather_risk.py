import math


METHOD_DESCRIPTION = (
    "Unvalidated weather-based screening prototype. No defensible rainfall "
    "thresholds or historical landslide labels are available in this project, "
    "so no landslide risk category or probability is inferred. This is not "
    "trained ML output or an official warning."
)


def assess_weather_risk(weather):
    observed_at = weather.get("observed_at") if isinstance(weather, dict) else None
    readings = weather.get("readings") if isinstance(weather, dict) else None
    factors = []

    if not isinstance(weather, dict) or not weather.get("available"):
        return {
            "status": "unavailable",
            "category": "UNAVAILABLE",
            "reason": "Open-Meteo weather readings are unavailable.",
            "contributing_factors": factors,
            "observed_at": observed_at,
            "method_description": METHOD_DESCRIPTION,
        }

    required_readings = (
        ("rain_mm", "Current rain", "mm"),
        ("precipitation_mm", "Current precipitation", "mm"),
    )

    for key, label, unit in required_readings:
        value = readings.get(key) if isinstance(readings, dict) else None
        try:
            is_finite = math.isfinite(value) if isinstance(value, (int, float)) else False
        except OverflowError:
            is_finite = False

        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not is_finite
            or value < 0
        ):
            return {
                "status": "unavailable",
                "category": "UNAVAILABLE",
                "reason": (
                    f"Required {label.lower()} reading is missing "
                    "or invalid."
                ),
                "contributing_factors": factors,
                "observed_at": observed_at,
                "method_description": METHOD_DESCRIPTION,
            }

        factors.append({
            "label": label,
            "value": value,
            "unit": unit,
        })

    return {
        "status": "unassessed",
        "category": "UNASSESSED",
        "reason": (
            "Current rain and precipitation readings are available, but "
            "they do not support a defensible landslide risk category. "
            "Historical event data and validated, time-window-specific "
            "thresholds are not available."
        ),
        "contributing_factors": factors,
        "observed_at": observed_at,
        "method_description": METHOD_DESCRIPTION,
    }
