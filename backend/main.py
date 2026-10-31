
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pymongo import MongoClient
from datetime import datetime, timezone
from threading import Lock
from typing import Optional
import sys
import os

# ---------- MONGODB CONNECTION ----------

MONGO_URL = "mongodb://localhost:27017"

client = MongoClient(
    MONGO_URL,
    serverSelectionTimeoutMS=5000
)

db = client["slope_guard_ai"]

sensor_history = db["sensor_history"]
risk_predictions = db["risk_predictions"]
alerts_collection = db["alerts"]

try:
    client.admin.command("ping")
    print("MongoDB connected successfully!")
except Exception as exc:
    print("MongoDB connection failed:", exc)


# ---------- PROJECT IMPORTS ----------

sys.path.append(os.path.dirname(__file__))

from ml.model import model
from sensor_data import generate_sensor_data
from risk_engine import calculate_risk
from locations import get_monitoring_locations
from weather_service import get_weather
from weather_risk import assess_weather_risk
from csv_reader import reader, USE_SIMULATOR


# ---------- FASTAPI APPLICATION ----------

app = FastAPI(
    title="Nilgiris Landslide Early Warning System",
    description="Backend API for GIS, ML, sensors and alerts",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- ESP32 LIVE TELEMETRY API ----------

telemetry_lock = Lock()
latest_telemetry = None


class Telemetry(BaseModel):
    sequence: int
    uptime_ms: int

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    soil_raw: int = Field(ge=0, le=65535)

    accel_x: float
    accel_y: float
    accel_z: float

    gyro_x: float
    gyro_y: float
    gyro_z: float

    gps_valid: bool
    mpu_valid: bool
    rain_detected: bool


@app.post("/api/telemetry")
def receive_telemetry(data: Telemetry):
    global latest_telemetry

    # Compatible with both Pydantic v1 and v2.
    if hasattr(data, "model_dump"):
        record = data.model_dump()
    else:
        record = data.dict()

    record["received_at"] = datetime.now(timezone.utc).isoformat()

    with telemetry_lock:
        latest_telemetry = record.copy()

    # Telemetry remains available in memory if MongoDB is offline.
    try:
        sensor_history.insert_one(record.copy())
    except Exception as exc:
        print("MongoDB telemetry save failed:", exc)

    return {
        "ok": True,
        "sequence": record["sequence"],
        "received_at": record["received_at"],
    }


@app.get("/api/telemetry/latest")
def get_latest_telemetry():
    with telemetry_lock:
        record = (
            latest_telemetry.copy()
            if latest_telemetry is not None
            else None
        )

    if record is None:
        return {
            "available": False,
            "data": None,
            "message": "No telemetry received yet",
        }

    return {
        "available": True,
        "data": record,
    }


@app.get("/api/telemetry/geojson")
def get_telemetry_geojson():
    with telemetry_lock:
        reading = (
            latest_telemetry.copy()
            if latest_telemetry is not None
            else None
        )

    if reading is None:
        return {
            "type": "FeatureCollection",
            "features": [],
        }

    if (
        not reading.get("gps_valid", False)
        or reading.get("latitude") is None
        or reading.get("longitude") is None
    ):
        return {
            "type": "FeatureCollection",
            "features": [],
        }

    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        reading["longitude"],
                        reading["latitude"],
                    ],
                },
                "properties": reading,
            }
        ],
    }


# ---------- LANDSLIDE PREDICTION API ----------

class PredictionInput(BaseModel):
    DEM_Final: float
    Slope: float
    Aspect: float
    Rainfall: float
    Clay: float
    LULC: float
    Road_Dist: float


@app.get("/")
def root():
    return {
        "message": (
            "Nilgiris Landslide Early Warning System API is running"
        )
    }


@app.get("/api/status")
def system_status():
    return {
        "status": "online",
        "system": "Landslide Early Warning System",
        "location": "Nilgiris District, Tamil Nadu",
    }


@app.post("/api/predict")
def predict_landslide(data: PredictionInput):
    features = [[
        data.DEM_Final,
        data.Slope,
        data.Aspect,
        data.Rainfall,
        data.Clay,
        data.LULC,
        data.Road_Dist,
    ]]

    prediction = int(model.predict(features)[0])
    probability = float(model.predict_proba(features)[0][1]) * 100

    if probability >= 70:
        risk_level = "HIGH"
    elif probability >= 40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "prediction": prediction,
        "probability": round(probability, 2),
        "risk_level": risk_level,
    }


# ---------- SENSOR & RISK DATA HELPERS ----------

def _build_sensors_payload(include_risk: bool = False):
    if USE_SIMULATOR:
        sensors = generate_sensor_data()
        results = []
        for s in sensors:
            item = {
                "sensor_id": s["sensor_id"],
                "location": s["location"],
                "readings": s["readings"],
                "data_source": "SIMULATED",
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "packet_loss_count": 0,
                "gps_valid": True,
                "mpu_valid": True,
            }
            if include_risk:
                r = calculate_risk(s["readings"])
                item["risk_score"] = r["risk_score"]
                item["risk_level"] = r["risk_level"]
                item["contributing_factors"] = r.get("contributing_factors", [])
                item["factor_points"] = r.get("factor_points", {})
            results.append(item)
        return {
            "count": len(results),
            "data_source": "SIMULATED",
            "sensors": results
        }

    status = reader.get_status()
    if not status["available"]:
        return {
            "count": 0,
            "data_source": status["data_source"],
            "packet_loss_count": status["packet_loss_count"],
            "message": status["message"],
            "sensors": []
        }

    node = status["data"]
    readings = {
        "soil_raw": node["soil_raw"],
        "soil_moisture": node["soil_moisture"],
        "tilt": node["tilt"],
        "tilt_baseline": node["tilt_baseline"],
        "tilt_change": node["tilt_change"],
        "motion_accel": node["motion_accel"],
        "motion_gyro": node["motion_gyro"],
        "rain_detected": node["rain_detected"],
        "calibrated": node.get("calibrated", False),
        "accel_x": node["accel_x"],
        "accel_y": node["accel_y"],
        "accel_z": node["accel_z"],
        "gyro_x": node["gyro_x"],
        "gyro_y": node["gyro_y"],
        "gyro_z": node["gyro_z"],
    }

    location = {
        "latitude": node["latitude"],
        "longitude": node["longitude"],
        "gps_valid": node["gps_valid"],
    }

    sensor_entry = {
        "sensor_id": "NODE-01",
        "location": location,
        "readings": readings,
        "data_source": status["data_source"],
        "is_stale": status["is_stale"],
        "age_seconds": status["age_seconds"],
        "last_updated": node["received_at"],
        "sequence": node["sequence"],
        "uptime_ms": node["uptime_ms"],
        "packet_loss_count": status["packet_loss_count"],
        "gps_valid": node["gps_valid"],
        "mpu_valid": node["mpu_valid"],
        "calibrated": node.get("calibrated", False),
    }

    if include_risk:
        risk = calculate_risk(readings)
        sensor_entry["risk_score"] = risk["risk_score"]
        sensor_entry["risk_level"] = risk["risk_level"]
        sensor_entry["contributing_factors"] = risk["contributing_factors"]
        sensor_entry["factor_points"] = risk["factor_points"]

    return {
        "count": 1,
        "data_source": status["data_source"],
        "is_stale": status["is_stale"],
        "packet_loss_count": status["packet_loss_count"],
        "calibrated": node.get("calibrated", False),
        "sensors": [sensor_entry],
    }


# ---------- SENSOR API ----------

@app.get("/api/sensors")
def get_sensors():
    return _build_sensors_payload(include_risk=False)


# ---------- RISK API ----------

@app.get("/api/risk")
def get_risk():
    return _build_sensors_payload(include_risk=True)


# ---------- MONITORING LOCATIONS API ----------

@app.get("/api/locations")
def get_locations():
    locations = get_monitoring_locations()

    return {
        "count": len(locations),
        "sensor_covered": sum(
            1 for location in locations
            if location["monitoring_type"] == "sensor"
        ),
        "weather_monitored": sum(
            1 for location in locations
            if location["monitoring_type"] == "weather_api"
        ),
        "locations": locations,
    }


# ---------- WEATHER API ----------

@app.get("/api/weather")
def get_weather_for_locations():
    locations = get_monitoring_locations()

    weather_locations = [
        location for location in locations
        if location["monitoring_type"] == "weather_api"
    ]

    results = []

    for location in weather_locations:
        weather = get_weather(
            location["latitude"],
            location["longitude"],
        )

        results.append({
            "location_id": location["location_id"],
            "name": location["name"],
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "monitoring_type": "weather_api",
            "weather": weather,
        })

    return {
        "count": len(results),
        "locations": results,
    }


# ---------- WEATHER RISK API ----------

@app.get("/api/weather-risk")
def get_weather_risk_for_locations():
    locations = get_monitoring_locations()

    weather_locations = [
        location for location in locations
        if location["monitoring_type"] == "weather_api"
    ]

    results = []

    for location in weather_locations:
        weather = get_weather(
            location["latitude"],
            location["longitude"],
        )

        results.append({
            "location_id": location["location_id"],
            "name": location["name"],
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "monitoring_type": "weather_api",
            "weather": weather,
            "weather_risk": {
                "location_name": location["name"],
                **assess_weather_risk(weather),
            },
        })

    return {
        "count": len(results),
        "method_description": (
            "Unvalidated weather-based screening prototype; this endpoint "
            "does not provide trained ML output, official warnings, or "
            "validated landslide predictions."
        ),
        "locations": results,
    }
