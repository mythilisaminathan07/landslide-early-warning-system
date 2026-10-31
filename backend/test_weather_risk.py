import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import main
from weather_risk import assess_weather_risk


class WeatherRiskTests(unittest.TestCase):
    def test_available_readings_are_reported_as_unassessed(self):
        weather = {
            "available": True,
            "observed_at": "2026-10-14T15:00",
            "readings": {
                "rain_mm": 0.4,
                "precipitation_mm": 0.7,
            },
        }

        result = assess_weather_risk(weather)

        self.assertEqual(result["status"], "unassessed")
        self.assertEqual(result["category"], "UNASSESSED")
        self.assertEqual(result["observed_at"], "2026-10-14T15:00")
        self.assertEqual(len(result["contributing_factors"]), 2)

    def test_missing_and_invalid_rainfall_inputs_are_unavailable(self):
        invalid_values = (
            None,
            "0.4",
            float("nan"),
            float("inf"),
            10 ** 1000,
            -0.1,
            True,
        )

        for value in invalid_values:
            with self.subTest(value=value):
                result = assess_weather_risk({
                    "available": True,
                    "readings": {
                        "rain_mm": value,
                        "precipitation_mm": 0.7,
                    },
                })
                self.assertEqual(result["status"], "unavailable")
                self.assertEqual(result["category"], "UNAVAILABLE")

        self.assertEqual(
            assess_weather_risk({"available": False})["status"],
            "unavailable",
        )

    def test_weather_risk_endpoint_returns_one_result_per_weather_location(self):
        weather = {
            "available": True,
            "observed_at": "2026-10-14T15:00",
            "readings": {
                "rain_mm": 0.1,
                "precipitation_mm": 0.2,
            },
        }
        client = TestClient(main.app)

        with patch("main.get_weather", return_value=weather) as get_weather:
            response = client.get("/api/weather-risk")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], 5)
        self.assertEqual(
            [location["name"] for location in payload["locations"]],
            ["Coonoor", "Kotagiri", "Kundah", "Gudalur", "Pandalur"],
        )
        self.assertTrue(all(
            location["weather_risk"]["status"] == "unassessed"
            for location in payload["locations"]
        ))
        self.assertEqual(get_weather.call_count, 5)

    def test_existing_api_routes_keep_their_responses(self):
        client = TestClient(main.app)
        routes = {
            (route.path, method)
            for route in main.app.routes
            for method in getattr(route, "methods", set())
        }

        for route in (
            ("/api/weather", "GET"),
            ("/api/risk", "GET"),
            ("/api/predict", "POST"),
            ("/api/locations", "GET"),
            ("/api/weather-risk", "GET"),
        ):
            with self.subTest(route=route):
                self.assertIn(route, routes)

        locations_response = client.get("/api/locations")
        self.assertEqual(locations_response.status_code, 200)
        self.assertEqual(locations_response.json()["count"], 6)

        risk_response = client.get("/api/risk")
        self.assertEqual(risk_response.status_code, 200)
        self.assertEqual(risk_response.json()["count"], 3)

        weather = {
            "available": True,
            "source": "Open-Meteo",
            "observed_at": "2026-10-14T15:00",
            "readings": {
                "temperature_c": 20.0,
                "humidity_percent": 80,
                "precipitation_mm": 0.7,
                "rain_mm": 0.4,
                "pressure_hpa": 900.0,
            },
        }
        with patch("main.get_weather", return_value=weather):
            weather_response = client.get("/api/weather")

        self.assertEqual(weather_response.status_code, 200)
        weather_payload = weather_response.json()
        self.assertEqual(weather_payload["count"], 5)
        self.assertEqual(
            set(weather_payload["locations"][0]),
            {
                "location_id",
                "name",
                "latitude",
                "longitude",
                "monitoring_type",
                "weather",
            },
        )

        prediction_response = client.post(
            "/api/predict",
            json={
                "DEM_Final": 1800,
                "Slope": 25,
                "Aspect": 180,
                "Rainfall": 150,
                "Clay": 30,
                "LULC": 40,
                "Road_Dist": 100,
            },
        )
        self.assertEqual(prediction_response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
