# GeoRisk / SlopeGuard AI - Complete Source Code Bundle

> **Generated:** 2026-10-29 04:47:48 UTC
> **Total Source Files Included:** 31
> **Note:** All source code and configurations are copied verbatim without modifications.

---

## Table of Contents

| # | File Path | Type | Line Count |
|---|-----------|------|------------|
| 1 | [`serial_bridge.py`](#serial_bridgepy) | `python` | 227 |
| 2 | [`backend/main.py`](#backendmainpy) | `python` | 453 |
| 3 | [`backend/csv_reader.py`](#backendcsv_readerpy) | `python` | 359 |
| 4 | [`backend/risk_engine.py`](#backendrisk_enginepy) | `python` | 263 |
| 5 | [`backend/sensor_data.py`](#backendsensor_datapy) | `python` | 65 |
| 6 | [`backend/locations.py`](#backendlocationspy) | `python` | 55 |
| 7 | [`backend/weather_service.py`](#backendweather_servicepy) | `python` | 64 |
| 8 | [`backend/weather_risk.py`](#backendweather_riskpy) | `python` | 75 |
| 9 | [`backend/ml/model.py`](#backendmlmodelpy) | `python` | 11 |
| 10 | [`backend/test_phase2.py`](#backendtest_phase2py) | `python` | 208 |
| 11 | [`backend/test_weather.py`](#backendtest_weatherpy) | `python` | 5 |
| 12 | [`backend/test_weather_risk.py`](#backendtest_weather_riskpy) | `python` | 155 |
| 13 | [`backend/requirements.txt`](#backendrequirementstxt) | `text` | 29 |
| 14 | [`backend/.env.example`](#backendenvexample) | `text` | 27 |
| 15 | [`frontend/index.html`](#frontendindexhtml) | `html` | 13 |
| 16 | [`frontend/package.json`](#frontendpackagejson) | `json` | 30 |
| 17 | [`frontend/vite.config.js`](#frontendviteconfigjs) | `javascript` | 7 |
| 18 | [`frontend/.oxlintrc.json`](#frontendoxlintrcjson) | `json` | 8 |
| 19 | [`frontend/src/main.jsx`](#frontendsrcmainjsx) | `jsx` | 15 |
| 20 | [`frontend/src/App.jsx`](#frontendsrcappjsx) | `jsx` | 46 |
| 21 | [`frontend/src/App.css`](#frontendsrcappcss) | `css` | 2234 |
| 22 | [`frontend/src/index.css`](#frontendsrcindexcss) | `css` | 15 |
| 23 | [`frontend/src/components/Header.jsx`](#frontendsrccomponentsheaderjsx) | `jsx` | 30 |
| 24 | [`frontend/src/components/LiveTelemetry.jsx`](#frontendsrccomponentslivetelemetryjsx) | `jsx` | 90 |
| 25 | [`frontend/src/components/Sidebar.jsx`](#frontendsrccomponentssidebarjsx) | `jsx` | 104 |
| 26 | [`frontend/src/pages/Dashboard.jsx`](#frontendsrcpagesdashboardjsx) | `jsx` | 557 |
| 27 | [`frontend/src/pages/Sensors.jsx`](#frontendsrcpagessensorsjsx) | `jsx` | 307 |
| 28 | [`frontend/src/pages/Alerts.jsx`](#frontendsrcpagesalertsjsx) | `jsx` | 304 |
| 29 | [`frontend/src/pages/History.jsx`](#frontendsrcpageshistoryjsx) | `jsx` | 292 |
| 30 | [`frontend/src/pages/GIS.jsx`](#frontendsrcpagesgisjsx) | `jsx` | 867 |
| 31 | [`frontend/src/pages/MLPrediction.jsx`](#frontendsrcpagesmlpredictionjsx) | `jsx` | 267 |

---

## `serial_bridge.py`

````python

import csv
import os
import time
from datetime import datetime, timezone

import requests
import serial
from serial import SerialException

# =====================================================
# 1. CONFIGURATION
# =====================================================

SERIAL_PORT = "COM13"
BAUD_RATE = 115200

API_URL = "http://127.0.0.1:8000/api/telemetry"

# Saved in the directory from which this script is run.
CSV_FILE = "sensor_data.csv"

COLUMNS = [
    "sequence",
    "uptime_ms",
    "latitude",
    "longitude",
    "soil_raw",
    "accel_x",
    "accel_y",
    "accel_z",
    "gyro_x",
    "gyro_y",
    "gyro_z",
    "gps_valid",
    "mpu_valid",
    "rain_detected",
]

INTEGER_FIELDS = {
    "sequence", "uptime_ms", "soil_raw"
}

FLOAT_FIELDS = {
    "latitude", "longitude",
    "accel_x", "accel_y", "accel_z",
    "gyro_x", "gyro_y", "gyro_z",
}

BOOLEAN_FIELDS = {
    "gps_valid", "mpu_valid", "rain_detected"
}


# =====================================================
# 2. PARSE SERIAL DATA
# =====================================================

def parse_bool(value):
    value = value.strip().lower()

    if value in ("1", "true"):
        return True
    if value in ("0", "false"):
        return False

    raise ValueError(f"Invalid Boolean value: {value}")


def parse_gateway_line(line):
    """Parse gateway CSV output and ignore startup messages."""

    try:
        values = next(csv.reader([line]))

        if not values:
            return None

        # Ignore CSV headers and startup messages.
        first = values[0].strip().lower()

        if first in ("seq", "sequence"):
            return None

        # Require at least the 14 expected columns.
        if len(values) < len(COLUMNS):
            return None

        # Ignore extra trailing fields.
        values = values[:len(COLUMNS)]

        record = dict(
            zip(COLUMNS, [v.strip() for v in values])
        )

        for key in INTEGER_FIELDS:
            record[key] = int(record[key])

        for key in FLOAT_FIELDS:
            record[key] = float(record[key])

        for key in BOOLEAN_FIELDS:
            record[key] = parse_bool(record[key])

        # Do not use coordinates if GPS is invalid.
        if not record["gps_valid"]:
            record["latitude"] = None
            record["longitude"] = None

        return record

    except (ValueError, TypeError, csv.Error):
        # Boot messages, corrupted lines, and malformed data
        # are ignored rather than crashing the bridge.
        return None


# =====================================================
# 3. MAIN BRIDGE
# =====================================================

def main():
    csv_path = os.path.abspath(CSV_FILE)

    print(f"Serial port: {SERIAL_PORT} at {BAUD_RATE} baud")
    print(f"CSV output: {csv_path}")
    print(f"API endpoint: {API_URL}")

    file_exists = (
        os.path.exists(CSV_FILE)
        and os.path.getsize(CSV_FILE) > 0
    )

    try:
        with serial.Serial(
            SERIAL_PORT,
            BAUD_RATE,
            timeout=2
        ) as port:

            # Append new data instead of deleting old readings.
            with open(
                CSV_FILE, "a", newline="", encoding="utf-8"
            ) as csv_file:

                writer = csv.DictWriter(
                    csv_file,
                    fieldnames=["received_at"] + COLUMNS
                )

                if not file_exists:
                    writer.writeheader()
                    csv_file.flush()

                # ESP32 may reset when serial is opened.
                time.sleep(2)

                print("Bridge running. Press Ctrl+C to stop.")

                while True:
                    raw_line = port.readline()

                    if not raw_line:
                        continue

                    line = raw_line.decode(
                        "utf-8", errors="replace"
                    ).strip()

                    if not line:
                        continue

                    record = parse_gateway_line(line)

                    if record is None:
                        continue

                    received_at = datetime.now(
                        timezone.utc
                    ).isoformat()

                    # Save first, so API failure does not
                    # prevent local CSV logging.
                    csv_record = {
                        "received_at": received_at,
                        **record,
                    }

                    writer.writerow(csv_record)
                    csv_file.flush()

                    print(
                        f"Saved sequence {record['sequence']} "
                        f"to sensor_data.csv"
                    )

                    # Forward the reading to FastAPI.
                    try:
                        response = requests.post(
                            API_URL,
                            json=record,
                            timeout=3,
                        )

                        response.raise_for_status()

                        print("Backend accepted the reading.")

                    except requests.RequestException as exc:
                        print(
                            "API forwarding failed; CSV saved. "
                            f"Reason: {exc}"
                        )

    except SerialException as exc:
        print(f"Serial connection error: {exc}")
        print(
            "Check COM13, the USB cable, ESP32 power, "
            "and that Arduino Serial Monitor is closed."
        )

    except KeyboardInterrupt:
        print("\nBridge stopped.")


if __name__ == "__main__":
    main()
````

---

## `backend/main.py`

````python

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
````

---

## `backend/csv_reader.py`

````python
import csv
from collections import deque
from datetime import datetime, timezone
import math
import os
import threading
from typing import Any, Dict, List, Optional

# ==============================================================================
# CONFIGURATION & ENVIRONMENT
# ==============================================================================

def _load_env_file():
    """Load backend/.env or .env if present without requiring python-dotenv."""
    possible_paths = [
        os.path.join(os.path.dirname(__file__), ".env"),
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        ".env",
    ]
    for env_path in possible_paths:
        if os.path.exists(env_path) and os.path.isfile(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            # Strip inline comments
                            content = line.split("#", 1)[0].strip()
                            if "=" in content:
                                k, v = content.split("=", 1)
                                k = k.strip()
                                v = v.strip().strip("'\"")
                                if k and k not in os.environ:
                                    os.environ[k] = v
            except Exception:
                pass
            break

_load_env_file()

def _parse_bool(val: Any, default: bool = False) -> bool:
    if val is None:
        return default
    s = str(val).strip().lower()
    if s in ("true", "1", "yes", "t", "y"):
        return True
    if s in ("false", "0", "no", "f", "n"):
        return False
    return default

# Read environment variables
CSV_FILE_PATH = os.environ.get(
    "CSV_FILE_PATH",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sensor_data.csv"))
)
STALE_AFTER_SECONDS = float(os.environ.get("STALE_AFTER_SECONDS", 10.0))

# Soil moisture ADC calibration
# TODO: Calibrate with field physical sensors.
_raw_dry_env = os.environ.get("SOIL_DRY_RAW")
_raw_wet_env = os.environ.get("SOIL_WET_RAW")
SOIL_CALIBRATED = bool(_raw_dry_env is not None and _raw_wet_env is not None and _raw_dry_env.strip() != "" and _raw_wet_env.strip() != "")
SOIL_DRY_RAW = float(_raw_dry_env) if (_raw_dry_env is not None and _raw_dry_env.strip() != "") else 3500.0
SOIL_WET_RAW = float(_raw_wet_env) if (_raw_wet_env is not None and _raw_wet_env.strip() != "") else 1800.0
SOIL_HIGHER_IS_WETTER = _parse_bool(os.environ.get("SOIL_HIGHER_IS_WETTER", "False"), default=False)

# MPU validity requirement (Default True; set False in .env for test CSV data)
REQUIRE_MPU_VALID = _parse_bool(os.environ.get("REQUIRE_MPU_VALID", "True"), default=True)

# Baseline tilt (optional environment override)
_env_baseline = os.environ.get("TILT_BASELINE_DEG", None)
TILT_BASELINE_ENV: Optional[float] = float(_env_baseline) if _env_baseline is not None and _env_baseline != "" else None

# Simulator fallback toggle
USE_SIMULATOR = _parse_bool(os.environ.get("USE_SIMULATOR", "False"), default=False)


# ==============================================================================
# CSV READER & CACHE ENGINE
# ==============================================================================

class CSVReaderEngine:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.lock = threading.Lock()
        
        # State
        self.last_byte_offset = 0
        self.latest_reading: Optional[Dict[str, Any]] = None
        self.history: deque = deque(maxlen=100)
        
        # Sequence & Packet Loss tracking
        self.last_sequence: Optional[int] = None
        self.last_uptime_ms: Optional[int] = None
        self.packet_loss_count: int = 0
        
        # Tilt baseline tracking (average of first 5 valid readings)
        self.initial_tilts: List[float] = []
        self.baseline_deg: Optional[float] = TILT_BASELINE_ENV

    def _resolve_file_path(self) -> str:
        candidates = [
            self.file_path,
            os.path.join(os.path.dirname(__file__), "..", "sensor_data.csv"),
            os.path.join(os.getcwd(), "sensor_data.csv"),
            os.path.join(os.path.dirname(__file__), "sensor_data.csv"),
        ]
        for c in candidates:
            if os.path.exists(c):
                return os.path.abspath(c)
        return os.path.abspath(self.file_path)

    def _convert_soil_moisture(
        self,
        soil_raw: int,
        dry_raw: float = SOIL_DRY_RAW,
        wet_raw: float = SOIL_WET_RAW,
        higher_is_wetter: bool = SOIL_HIGHER_IS_WETTER
    ) -> float:
        """Convert soil ADC to percentage clamped to [0.0, 100.0]."""
        raw_low = min(dry_raw, wet_raw)
        raw_high = max(dry_raw, wet_raw)
        span = raw_high - raw_low
        if span < 1e-6:
            return 0.0
        if higher_is_wetter:
            # Higher raw reading means wetter
            pct = ((soil_raw - raw_low) / span) * 100.0
        else:
            # Lower raw reading means wetter (capacitive default)
            pct = ((raw_high - soil_raw) / span) * 100.0
        return max(0.0, min(100.0, round(pct, 1)))

    def _convert_imu(
        self,
        ax: float,
        ay: float,
        az: float,
        gx: float,
        gy: float,
        gz: float,
        mpu_valid: bool
    ) -> Dict[str, Optional[float]]:
        """Compute tilt and motion metrics from IMU readings."""
        if not mpu_valid and REQUIRE_MPU_VALID:
            return {
                "tilt": None,
                "tilt_baseline": self.baseline_deg,
                "tilt_change": None,
                "motion_accel": None,
                "motion_gyro": None,
                "mpu_available": False,
            }
        
        # Calculate absolute tilt angle from vertical gravity vector
        accel_horiz = math.sqrt(ax**2 + ay**2)
        tilt_deg = math.degrees(math.atan2(accel_horiz, abs(az))) if abs(az) > 1e-6 else 90.0
        tilt_deg = round(tilt_deg, 2)

        # Baseline calculation
        if self.baseline_deg is None:
            if len(self.initial_tilts) < 5:
                self.initial_tilts.append(tilt_deg)
            self.baseline_deg = round(sum(self.initial_tilts) / len(self.initial_tilts), 2)
        
        tilt_change = round(abs(tilt_deg - self.baseline_deg), 2)
        
        # Motion metrics
        accel_mag = math.sqrt(ax**2 + ay**2 + az**2)
        motion_accel = round(abs(accel_mag - 9.81), 2)
        motion_gyro = round(math.sqrt(gx**2 + gy**2 + gz**2), 2)

        return {
            "tilt": tilt_deg,
            "tilt_baseline": self.baseline_deg,
            "tilt_change": tilt_change,
            "motion_accel": motion_accel,
            "motion_gyro": motion_gyro,
            "mpu_available": True,
        }

    def _parse_row(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse and convert a single CSV line into a structured record."""
        try:
            line_str = line.strip()
            if not line_str:
                return None
            
            reader = csv.reader([line_str])
            values = next(reader)
            if not values:
                return None
            
            first = values[0].strip().lower()
            if first in ("received_at", "seq", "sequence"):
                return None  # Header row
            
            if len(values) < 15:
                return None  # Incomplete / corrupted line
            
            # Extract fields
            received_at_str = values[0].strip()
            sequence = int(values[1].strip())
            uptime_ms = int(values[2].strip())
            
            # GPS
            gps_valid = _parse_bool(values[12].strip())
            lat = float(values[3].strip()) if gps_valid and values[3].strip() else None
            lon = float(values[4].strip()) if gps_valid and values[4].strip() else None
            
            # Soil
            soil_raw = int(values[5].strip())
            
            # Accelerometer & Gyroscope
            ax = float(values[6].strip())
            ay = float(values[7].strip())
            az = float(values[8].strip())
            gx = float(values[9].strip())
            gy = float(values[10].strip())
            gz = float(values[11].strip())
            
            mpu_valid = _parse_bool(values[13].strip())
            rain_detected = _parse_bool(values[14].strip())
            
            # IMU processing
            imu = self._convert_imu(ax, ay, az, gx, gy, gz, mpu_valid)
            soil_pct = self._convert_soil_moisture(soil_raw)
            
            return {
                "received_at": received_at_str,
                "sequence": sequence,
                "uptime_ms": uptime_ms,
                "gps_valid": gps_valid,
                "latitude": lat,
                "longitude": lon,
                "soil_raw": soil_raw,
                "soil_moisture": soil_pct,
                "accel_x": ax,
                "accel_y": ay,
                "accel_z": az,
                "gyro_x": gx,
                "gyro_y": gy,
                "gyro_z": gz,
                "mpu_valid": mpu_valid,
                "rain_detected": rain_detected,
                "calibrated": SOIL_CALIBRATED,
                **imu,
            }
        except (ValueError, TypeError, IndexError, csv.Error):
            return None

    def _process_sequence_and_gaps(self, record: Dict[str, Any]):
        seq = record["sequence"]
        uptime = record["uptime_ms"]

        if self.last_uptime_ms is not None and uptime < self.last_uptime_ms:
            # Node reboot / restart: reset sequence tracking without adding packet loss
            self.last_sequence = seq
            self.last_uptime_ms = uptime
            return

        if self.last_sequence is not None:
            if seq > self.last_sequence + 1:
                gap = seq - (self.last_sequence + 1)
                self.packet_loss_count += gap

        self.last_sequence = seq
        self.last_uptime_ms = uptime

    def refresh(self) -> None:
        """Incrementally reads new rows from the CSV file."""
        real_path = self._resolve_file_path()
        if not os.path.exists(real_path):
            return

        with self.lock:
            try:
                file_size = os.path.getsize(real_path)
                # Handle file truncation or replacement
                if file_size < self.last_byte_offset:
                    self.last_byte_offset = 0

                # Read with Windows file-sharing safe mode
                with open(real_path, "r", encoding="utf-8", errors="replace") as f:
                    f.seek(self.last_byte_offset)
                    new_lines = f.readlines()
                    
                    # If file has not completed trailing newline on last line, don't advance past it
                    bytes_read = f.tell()
                    if new_lines and not new_lines[-1].endswith("\n"):
                        # Incomplete last line: wind back offset before this partial line
                        f.seek(self.last_byte_offset)
                        offset = self.last_byte_offset
                        for line in new_lines[:-1]:
                            offset += len(line.encode("utf-8", errors="replace"))
                        self.last_byte_offset = offset
                        new_lines = new_lines[:-1]
                    else:
                        self.last_byte_offset = bytes_read

                for line in new_lines:
                    record = self._parse_row(line)
                    if record is not None:
                        self._process_sequence_and_gaps(record)
                        self.latest_reading = record
                        self.history.append(record)

            except (IOError, PermissionError, OSError):
                # Temporary file lock from gateway writer on Windows; retain existing cache
                pass

    def get_status(self) -> Dict[str, Any]:
        """Check latest reading and return status with staleness determination."""
        self.refresh()
        
        with self.lock:
            if self.latest_reading is None:
                return {
                    "available": False,
                    "data_source": "NO_DATA",
                    "data": None,
                    "packet_loss_count": self.packet_loss_count,
                    "message": "Waiting for sensor readings from CSV",
                }

            # Check staleness
            received_str = self.latest_reading.get("received_at", "")
            is_stale = True
            age_seconds = None
            try:
                # Handle ISO timestamps with timezone
                rec_dt = datetime.fromisoformat(received_str.replace("Z", "+00:00"))
                now_dt = datetime.now(timezone.utc)
                age_seconds = round((now_dt - rec_dt).total_seconds(), 1)
                is_stale = age_seconds > STALE_AFTER_SECONDS
            except Exception:
                is_stale = True

            source = "STALE" if is_stale else "LIVE_CSV"
            
            return {
                "available": True,
                "data_source": source,
                "is_stale": is_stale,
                "age_seconds": age_seconds,
                "packet_loss_count": self.packet_loss_count,
                "data": self.latest_reading.copy(),
                "history_count": len(self.history),
            }

    def get_history(self) -> List[Dict[str, Any]]:
        with self.lock:
            return list(self.history)


# Global reader instance
reader = CSVReaderEngine(CSV_FILE_PATH)
````

---

## `backend/risk_engine.py`

````python
"""
================================================================================
SLOPEGUARD AI - RISK SCORING WEIGHTS & THRESHOLDS (MAX 100 POINTS)
================================================================================
Factor                  Max Pts   Thresholds & Points Allocation
--------------------------------------------------------------------------------
Soil Moisture (%)       35 pts    >= 85%  -> 35 pts  (Extreme saturation)
                                  >= 70%  -> 25 pts  (High saturation)
                                  >= 50%  -> 15 pts  (Moderate moisture)
                                  >= 30%  ->  5 pts  (Low-medium moisture)
                                  < 30%   ->  0 pts  (Dry)

Tilt Change (deg)       25 pts    >= 15.0° -> 25 pts (Severe slope displacement)
(from baseline)                   >=  8.0° -> 18 pts (Significant slope tilt)
                                  >=  4.0° -> 10 pts (Moderate tilt shift)
                                  >=  1.5° ->  5 pts (Minor tilt detected)
                                  <   1.5° ->  0 pts (Normal resting orientation)

Motion                  25 pts    Split between Accel Deviation (12) & Gyro (13):
 - Accel Dev (|mag-9.81|) 12 pts  >= 2.5 m/s²  -> 12 pts (Vigorous acceleration)
                                  >= 1.5 m/s²  ->  8 pts (Moderate vibration)
                                  >= 0.5 m/s²  ->  4 pts (Minor vibration)
                                  <  0.5 m/s²  ->  0 pts (Static)
 - Gyro Mag (deg/s)       13 pts  >= 15.0 deg/s -> 13 pts (Fast angular rotation)
                                  >=  8.0 deg/s ->  8 pts (Moderate rotation)
                                  >=  2.0 deg/s ->  4 pts (Minor rotation)
                                  <   2.0 deg/s ->  0 pts (Stationary)

Rain Detected           15 pts    True  -> 15 pts (Digital precipitation trigger)
                                  False ->  0 pts
                                  *Note: Rain alone yields 15 pts, remaining in LOW tier (<25)
--------------------------------------------------------------------------------
TOTAL RISK TIERS:
  LOW      :   0 - 24 pts
  MEDIUM   :  25 - 49 pts
  HIGH     :  50 - 74 pts
  CRITICAL :  75 - 100 pts
================================================================================
PROTOTYPE DISCLAIMER:
These scoring thresholds and weights are preliminary prototype engineering values.
They are NOT calibrated or validated for official evacuation or life-safety warnings.
================================================================================
"""

from typing import Any, Dict, List, Optional


def calculate_risk(readings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate real-time landslide risk score (0-100) and risk tier
    from hardware telemetry (soil moisture %, tilt change, motion, rain detected).
    
    If legacy simulator readings (rainfall mm, humidity, pressure) are passed,
    it falls back gracefully to simulated evaluation.
    """
    # Detect if this is real hardware node reading
    is_real_node = "rain_detected" in readings or "soil_raw" in readings or "tilt_change" in readings

    if is_real_node:
        return _calculate_real_sensor_risk(readings)
    else:
        return _calculate_legacy_simulator_risk(readings)


def _calculate_real_sensor_risk(readings: Dict[str, Any]) -> Dict[str, Any]:
    score = 0
    contributing_factors: List[str] = []
    factor_points: Dict[str, int] = {
        "soil_moisture": 0,
        "tilt_change": 0,
        "motion": 0,
        "rain_detected": 0,
    }

    # 1. Soil Moisture % (up to 35 pts)
    soil_pct = readings.get("soil_moisture")
    if soil_pct is not None:
        soil_val = float(soil_pct)
        if soil_val >= 85.0:
            pts = 35
            reason = f"Extreme soil saturation ({soil_val}% >= 85%)"
        elif soil_val >= 70.0:
            pts = 25
            reason = f"High soil saturation ({soil_val}% >= 70%)"
        elif soil_val >= 50.0:
            pts = 15
            reason = f"Moderate soil moisture ({soil_val}% >= 50%)"
        elif soil_val >= 30.0:
            pts = 5
            reason = f"Low soil moisture ({soil_val}% >= 30%)"
        else:
            pts = 0
            reason = ""

        if pts > 0:
            score += pts
            factor_points["soil_moisture"] = pts
            contributing_factors.append(f"{reason} (+{pts} pts)")

    # 2. Tilt Change from Baseline (up to 25 pts)
    tilt_change = readings.get("tilt_change")
    if tilt_change is not None:
        tc_val = float(tilt_change)
        if tc_val >= 15.0:
            pts = 25
            reason = f"Severe slope displacement ({tc_val}° change >= 15°)"
        elif tc_val >= 8.0:
            pts = 18
            reason = f"Significant slope tilt ({tc_val}° change >= 8°)"
        elif tc_val >= 4.0:
            pts = 10
            reason = f"Moderate tilt shift ({tc_val}° change >= 4°)"
        elif tc_val >= 1.5:
            pts = 5
            reason = f"Minor slope tilt ({tc_val}° change >= 1.5°)"
        else:
            pts = 0
            reason = ""

        if pts > 0:
            score += pts
            factor_points["tilt_change"] = pts
            contributing_factors.append(f"{reason} (+{pts} pts)")
    elif readings.get("mpu_available") is False or readings.get("mpu_valid") is False:
        # Note MPU unavailability if relevant
        contributing_factors.append("Tilt data unavailable (MPU invalid / disabled)")

    # 3. Motion: Accel Deviation (up to 12 pts) + Gyro Magnitude (up to 13 pts) = max 25 pts
    mot_accel = readings.get("motion_accel")
    mot_gyro = readings.get("motion_gyro")
    motion_pts = 0
    motion_reasons = []

    if mot_accel is not None:
        acc_val = float(mot_accel)
        if acc_val >= 2.5:
            p_acc = 12
            motion_reasons.append(f"Vigorous acceleration ({acc_val} m/s²)")
        elif acc_val >= 1.5:
            p_acc = 8
            motion_reasons.append(f"Moderate acceleration ({acc_val} m/s²)")
        elif acc_val >= 0.5:
            p_acc = 4
            motion_reasons.append(f"Minor vibration ({acc_val} m/s²)")
        else:
            p_acc = 0
        motion_pts += p_acc

    if mot_gyro is not None:
        gyr_val = float(mot_gyro)
        if gyr_val >= 15.0:
            p_gyr = 13
            motion_reasons.append(f"Fast angular rotation ({gyr_val} deg/s)")
        elif gyr_val >= 8.0:
            p_gyr = 8
            motion_reasons.append(f"Moderate rotation ({gyr_val} deg/s)")
        elif gyr_val >= 2.0:
            p_gyr = 4
            motion_reasons.append(f"Minor rotation ({gyr_val} deg/s)")
        else:
            p_gyr = 0
        motion_pts += p_gyr

    if motion_pts > 0:
        score += motion_pts
        factor_points["motion"] = motion_pts
        contributing_factors.append(f"Motion detected: {', '.join(motion_reasons)} (+{motion_pts} pts)")

    # 4. Rain Detected (up to 15 pts)
    # Binary sensor: rain alone yields 15 pts, which keeps it within LOW tier (<25)
    rain = readings.get("rain_detected", False)
    if rain is True or str(rain).lower() in ("true", "1"):
        score += 15
        factor_points["rain_detected"] = 15
        contributing_factors.append("Active rain detected (+15 pts)")

    # Clamp total score to [0, 100]
    score = max(0, min(100, score))

    # Determine risk tier
    if score >= 75:
        risk_level = "CRITICAL"
    elif score >= 50:
        risk_level = "HIGH"
    elif score >= 25:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "contributing_factors": contributing_factors,
        "factor_points": factor_points,
    }


def _calculate_legacy_simulator_risk(readings: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback scorer for simulated demo data when USE_SIMULATOR=True."""
    rainfall = readings.get("rainfall", 0)
    soil_moisture = readings.get("soil_moisture", 0)
    humidity = readings.get("humidity", 0)
    tilt = readings.get("tilt", 0)
    pressure = readings.get("pressure", 1013)

    score = 0
    factors = []

    if rainfall >= 100:
        score += 30
        factors.append(f"Extreme simulated rainfall ({rainfall} mm)")
    elif rainfall >= 70:
        score += 20
        factors.append(f"Heavy simulated rainfall ({rainfall} mm)")
    elif rainfall >= 40:
        score += 10
        factors.append(f"Moderate simulated rainfall ({rainfall} mm)")

    if soil_moisture >= 80:
        score += 25
        factors.append(f"High simulated soil moisture ({soil_moisture}%)")
    elif soil_moisture >= 65:
        score += 15
        factors.append(f"Moderate simulated soil moisture ({soil_moisture}%)")
    elif soil_moisture >= 50:
        score += 8

    if humidity >= 90:
        score += 15
    elif humidity >= 80:
        score += 10
    elif humidity >= 70:
        score += 5

    if tilt >= 6:
        score += 25
        factors.append(f"High tilt ({tilt}°)")
    elif tilt >= 3:
        score += 15
        factors.append(f"Moderate tilt ({tilt}°)")
    elif tilt >= 1:
        score += 5

    if pressure < 1000:
        score += 5

    score = min(100, score)

    if score >= 75:
        risk_level = "CRITICAL"
    elif score >= 50:
        risk_level = "HIGH"
    elif score >= 25:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "contributing_factors": factors,
        "factor_points": {},
    }
````

---

## `backend/sensor_data.py`

````python
import random


BASE_SENSORS = [
    {
        "sensor_id": "S001",
        "location": {
            "latitude": 11.4102,
            "longitude": 76.6950
        }
    },
    {
        "sensor_id": "S002",
        "location": {
            "latitude": 11.3850,
            "longitude": 76.7200
        }
    },
    {
        "sensor_id": "S003",
        "location": {
            "latitude": 11.4500,
            "longitude": 76.6800
        }
    }
]


def generate_sensor_data():

    sensors = []

    for sensor in BASE_SENSORS:

        readings = {
            "rainfall": round(random.uniform(40, 130), 1),

            "soil_moisture": round(
                random.uniform(50, 90), 1
            ),

            "temperature": round(
                random.uniform(20, 28), 1
            ),

            "humidity": round(
                random.uniform(70, 98), 1
            ),

            "pressure": round(
                random.uniform(995, 1010), 1
            ),

            "tilt": round(
                random.uniform(1, 8), 1
            )
        }

        sensors.append({
            "sensor_id": sensor["sensor_id"],
            "location": sensor["location"],
            "readings": readings
        })

    return sensors
````

---

## `backend/locations.py`

````python

MONITORING_LOCATIONS = [
    {
        "location_id": "LOC001",
        "name": "Ooty (Udhagamandalam)",
        "latitude": 11.4102,
        "longitude": 76.6950,
        "monitoring_type": "sensor",
        "sensor_id": "S001"
    },
    {
        "location_id": "LOC002",
        "name": "Coonoor",
        "latitude": 11.3498,
        "longitude": 76.7937,
        "monitoring_type": "weather_api",
        "sensor_id": None
    },
    {
        "location_id": "LOC003",
        "name": "Kotagiri",
        "latitude": 11.4200,
        "longitude": 76.8600,
        "monitoring_type": "weather_api",
        "sensor_id": None
    },
    {
        "location_id": "LOC004",
        "name": "Kundah",
        "latitude": 11.3200,
        "longitude": 76.6200,
        "monitoring_type": "weather_api",
        "sensor_id": None
    },
    {
        "location_id": "LOC005",
        "name": "Gudalur",
        "latitude": 11.5207,
        "longitude": 76.4814,
        "monitoring_type": "weather_api",
        "sensor_id": None
    },
    {
        "location_id": "LOC006",
        "name": "Pandalur",
        "latitude": 11.4800,
        "longitude": 76.3600,
        "monitoring_type": "weather_api",
        "sensor_id": None
    }
]


def get_monitoring_locations():
    return MONITORING_LOCATIONS
````

---

## `backend/weather_service.py`

````python

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
````

---

## `backend/weather_risk.py`

````python
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
````

---

## `backend/ml/model.py`

````python
import joblib
import os

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "landslide_random_forest_model.pkl"
)

model = joblib.load(MODEL_PATH)

print("Landslide Random Forest model loaded successfully!")
````

---

## `backend/test_phase2.py`

````python
import os
import sys
import tempfile
import time
from datetime import datetime, timezone, timedelta

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(__file__))

import csv_reader
from csv_reader import CSVReaderEngine
import risk_engine
from risk_engine import calculate_risk

def run_tests():
    print("=" * 80)
    print("PHASE 2 - COMPREHENSIVE BACKEND TEST SUITE")
    print("=" * 80)

    # --------------------------------------------------------------------------
    # TEST 1: The Three Sample Row Patterns in both SOIL_HIGHER_IS_WETTER modes
    # --------------------------------------------------------------------------
    sample_rows = [
        ("Pattern A (Rest)", "2026-10-28T16:03:05.547873+00:00,4,8107,11.353,76.7959,1800,0.05,-0.03,9.81,0.01,-0.02,0.01,True,False,True"),
        ("Pattern B (Motion / Tilt)", "2026-10-28T16:03:09.331474+00:00,6,12107,11.42,76.86,3500,-1.8,1.6,10.2,-15.0,10.0,-8.0,True,False,True"),
        ("Pattern C (Motion / Severe Tilt)", "2026-10-28T16:03:15.321247+00:00,9,18107,11.29,76.58,3500,2.2,-1.4,9.1,18.0,-12.0,7.0,True,False,True"),
    ]

    # For testing sample rows, we allow computing MPU metrics (as per requirement 1 & REQUIRE_MPU_VALID=False)
    csv_reader.REQUIRE_MPU_VALID = False

    for mode in [False, True]:
        csv_reader.SOIL_HIGHER_IS_WETTER = mode
        print(f"\n>>> RUNNING TEST WITH SOIL_HIGHER_IS_WETTER = {mode}")
        print(f"    (SOIL_DRY_RAW=3500, SOIL_WET_RAW=1800)")
        print("-" * 80)

        # Create fresh reader instance with baseline 0.34 deg (the Pattern A resting tilt)
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".csv") as tf:
            tf.write("received_at,sequence,uptime_ms,latitude,longitude,soil_raw,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,gps_valid,mpu_valid,rain_detected\n")
            temp_path = tf.name

        try:
            reader_instance = CSVReaderEngine(temp_path)
            # Set baseline to resting tilt of Pattern A (approx 0.34 deg)
            reader_instance.baseline_deg = 0.34

            for name, row_str in sample_rows:
                rec = reader_instance._parse_row(row_str)
                # Overwrite soil moisture with the tested mode
                rec["soil_moisture"] = reader_instance._convert_soil_moisture(
                    rec["soil_raw"], higher_is_wetter=mode
                )
                risk_res = calculate_risk(rec)

                print(f"\n--- {name} ---")
                print(f"Raw Input: soil_raw={rec['soil_raw']}, accel=({rec['accel_x']}, {rec['accel_y']}, {rec['accel_z']}), gyro=({rec['gyro_x']}, {rec['gyro_y']}, {rec['gyro_z']})")
                print(f"Calculated Metrics:")
                print(f"  * Soil Moisture   : {rec['soil_moisture']}%")
                print(f"  * Tilt (Absolute) : {rec['tilt']} deg  |  Baseline: {rec['tilt_baseline']} deg  |  Tilt Change: {rec['tilt_change']} deg")
                print(f"  * Motion          : Accel Dev = {rec['motion_accel']} m/s2, Gyro Mag = {rec['motion_gyro']} deg/s")
                print(f"  * Rain Detected   : {rec['rain_detected']}")
                print(f"Factor Points Breakdown:")
                pts = risk_res["factor_points"]
                print(f"  * Soil Moisture   : {pts.get('soil_moisture', 0)} / 35 pts")
                print(f"  * Tilt Change     : {pts.get('tilt_change', 0)} / 25 pts")
                print(f"  * Motion          : {pts.get('motion', 0)} / 25 pts")
                print(f"  * Rain Detected   : {pts.get('rain_detected', 0)} / 15 pts")
                print(f"TOTAL SCORE : {risk_res['risk_score']} / 100")
                print(f"RISK TIER   : {risk_res['risk_level']}")
                print(f"Contributing Factors: {risk_res['contributing_factors']}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    # --------------------------------------------------------------------------
    # TEST 2: Bad Line / Corrupted Line
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("TEST 2: BAD / CORRUPTED LINE HANDLING")
    print("=" * 80)
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".csv") as tf:
        tf.write("received_at,sequence,uptime_ms,latitude,longitude,soil_raw,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,gps_valid,mpu_valid,rain_detected\n")
        tf.write("CORRUPTED_LINE_NOT_ENOUGH_COLUMNS,1,2,3\n")
        tf.write("2026-10-28T16:03:05.547873+00:00,4,8107,11.353,76.7959,1800,0.05,-0.03,9.81,0.01,-0.02,0.01,True,False,True\n")
        temp_path = tf.name

    try:
        reader_test = CSVReaderEngine(temp_path)
        reader_test.refresh()
        status = reader_test.get_status()
        assert status["available"] is True, "Reader failed to read valid line after corrupted line"
        assert status["data"]["sequence"] == 4, f"Expected sequence 4, got {status['data']['sequence']}"
        print("[PASS] Corrupted line ignored safely without crash. Valid row parsed successfully.")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    # --------------------------------------------------------------------------
    # TEST 3: Half-Written Last Line
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("TEST 3: HALF-WRITTEN (INCOMPLETE) LAST LINE HANDLING")
    print("=" * 80)
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".csv") as tf:
        tf.write("received_at,sequence,uptime_ms,latitude,longitude,soil_raw,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,gps_valid,mpu_valid,rain_detected\n")
        tf.write("2026-10-28T16:03:05.547873+00:00,4,8107,11.353,76.7959,1800,0.05,-0.03,9.81,0.01,-0.02,0.01,True,False,True\n")
        # Incomplete line with NO trailing newline
        tf.write("2026-10-28T16:03:07.320832+00:00,5,10107,11.353,76.7959,3000,0.15")
        temp_path = tf.name

    try:
        reader_test = CSVReaderEngine(temp_path)
        reader_test.refresh()
        status = reader_test.get_status()
        assert status["available"] is True
        assert status["data"]["sequence"] == 4, f"Expected sequence 4, got {status['data']['sequence']}"
        print("[PASS] Incomplete line without newline held back safely. Only complete row was parsed.")

        # Now gateway completes writing that line with newline
        with open(temp_path, "a", encoding="utf-8") as f:
            f.write(",0.12,9.78,0.1,-0.08,0.04,True,False,True\n")

        reader_test.refresh()
        status2 = reader_test.get_status()
        assert status2["data"]["sequence"] == 5, f"Expected sequence 5 after line completion, got {status2['data']['sequence']}"
        print("[PASS] Completed line subsequently parsed correctly on next refresh.")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    # --------------------------------------------------------------------------
    # TEST 4: Empty File Handling
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("TEST 4: EMPTY FILE HANDLING")
    print("=" * 80)
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".csv") as tf:
        temp_path = tf.name

    try:
        reader_test = CSVReaderEngine(temp_path)
        status = reader_test.get_status()
        assert status["available"] is False
        assert status["data_source"] == "NO_DATA"
        print("[PASS] Empty file handled gracefully without crash (data_source = NO_DATA).")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    # --------------------------------------------------------------------------
    # TEST 5: Staleness Detection
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("TEST 5: STALENESS DETECTION")
    print("=" * 80)
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".csv") as tf:
        # Timestamp from 30 seconds ago (> STALE_AFTER_SECONDS = 10)
        old_time = (datetime.now(timezone.utc) - timedelta(seconds=30)).isoformat()
        tf.write("received_at,sequence,uptime_ms,latitude,longitude,soil_raw,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,gps_valid,mpu_valid,rain_detected\n")
        tf.write(f"{old_time},100,50000,11.353,76.7959,1800,0.05,-0.03,9.81,0.01,-0.02,0.01,True,False,True\n")
        temp_path = tf.name

    try:
        reader_test = CSVReaderEngine(temp_path)
        status = reader_test.get_status()
        assert status["is_stale"] is True, "Old timestamp was not flagged as stale!"
        assert status["data_source"] == "STALE", f"Expected STALE, got {status['data_source']}"
        print(f"[PASS] Stale reading correctly identified: age = {status['age_seconds']}s (> 10s), data_source = STALE.")

        # Now write fresh row (now)
        fresh_time = datetime.now(timezone.utc).isoformat()
        with open(temp_path, "a", encoding="utf-8") as f:
            f.write(f"{fresh_time},101,52000,11.353,76.7959,1800,0.05,-0.03,9.81,0.01,-0.02,0.01,True,False,True\n")

        status2 = reader_test.get_status()
        assert status2["is_stale"] is False, "Fresh timestamp was incorrectly flagged as stale!"
        assert status2["data_source"] == "LIVE_CSV", f"Expected LIVE_CSV, got {status2['data_source']}"
        print(f"[PASS] Fresh reading correctly identified: age = {status2['age_seconds']}s (<= 10s), data_source = LIVE_CSV.")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    # --------------------------------------------------------------------------
    # TEST 6: Real Workspace sensor_data.csv Integration Test
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("TEST 6: REAL WORKSPACE sensor_data.csv STATUS")
    print("=" * 80)
    real_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sensor_data.csv"))
    reader_real = CSVReaderEngine(real_csv)
    real_status = reader_real.get_status()
    print(f"Real CSV File Path: {real_csv}")
    print(f"Available: {real_status['available']}")
    print(f"Data Source: {real_status['data_source']}")
    print(f"Age Seconds: {real_status.get('age_seconds')} seconds")
    print(f"Latest Sequence: {real_status['data']['sequence']}")
    print(f"Packet Loss Count: {real_status['packet_loss_count']}")
    real_risk = calculate_risk(real_status['data'])
    print(f"Risk Score: {real_risk['risk_score']} ({real_risk['risk_level']})")
    print(f"Contributing Factors: {real_risk['contributing_factors']}")

    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    run_tests()
````

---

## `backend/test_weather.py`

````python
from weather_service import get_weather

result = get_weather(11.4200, 76.7400)

print(result)
````

---

## `backend/test_weather_risk.py`

````python
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
````

---

## `backend/requirements.txt`

````text
annotated-doc==0.0.5
annotated-types==0.8.0
anyio==4.15.1
certifi==2026.7.22
click==8.5.0
cloudpickle==3.1.2
fastapi==0.142.4
h11==0.16.0
httpcore==1.0.9
httpx==0.28.1
idna==3.20
joblib==1.6.0
narwhals==2.26.0
numpy==2.5.3
opentelemetry-api==1.45.1
pandas==3.0.6
pydantic==2.13.5
pydantic_core==2.46.5
python-dateutil==2.9.0.post0
scikit-learn==1.9.1
scipy==1.18.1
six==1.17.0
starlette==1.7.0
threadpoolctl==3.7.0
typing-inspection==0.4.4
typing_extensions==4.16.0
tzdata==2026.5
uvicorn==0.54.0
pymongo>=4.0.0
````

---

## `backend/.env.example`

````text
# SlopeGuard AI Backend Environment Configuration

# MPU validity check.
# Set to False for test CSV data where mpu_valid is False on every row.
# In production with functioning hardware MPU, keep this True.
REQUIRE_MPU_VALID=False # for the test CSV only

# Path to the CSV file generated by serial_bridge / gateway.
# Can be absolute or relative to the backend directory.
CSV_FILE_PATH=../sensor_data.csv

# Sensor data staleness threshold in seconds (compared against row received_at)
STALE_AFTER_SECONDS=10

# Soil moisture calibration (capacitive ADC)
# Leave commented out to use code defaults (3500 dry / 1800 wet) with calibrated=false.
# Uncomment and set when calibrated with your physical soil sensor:
# SOIL_DRY_RAW=3500
# SOIL_WET_RAW=1800
SOIL_HIGHER_IS_WETTER=False

# Tilt baseline in degrees (optional float).
# If unset or empty, the average of the first 5 valid readings after backend starts will be used.
# TILT_BASELINE_DEG=0.0

# Set to True only to force synthetic random data generator fallback (for demos without hardware or CSV)
USE_SIMULATOR=False
````

---

## `frontend/index.html`

````html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>frontend</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
````

---

## `frontend/package.json`

````json
{
  "name": "frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "oxlint",
    "preview": "vite preview"
  },
  "dependencies": {
    "georaster": "^1.6.0",
    "georaster-layer-for-leaflet": "^4.1.2",
    "leaflet": "^1.9.4",
    "lucide-react": "^1.53.0",
    "react": "^19.2.8",
    "react-dom": "^19.2.8",
    "react-leaflet": "^5.0.0",
    "react-router-dom": "^7.18.4",
    "recharts": "^3.10.1"
  },
  "devDependencies": {
    "@types/react": "^19.2.18",
    "@types/react-dom": "^19.2.7",
    "@vitejs/plugin-react": "^6.1.1",
    "oxlint": "^1.81.0",
    "vite": "^8.3.0"
  }
}
````

---

## `frontend/vite.config.js`

````javascript
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
})
````

---

## `frontend/.oxlintrc.json`

````json
{
  "$schema": "./node_modules/oxlint/configuration_schema.json",
  "plugins": ["react", "oxc"],
  "rules": {
    "react/rules-of-hooks": "error",
    "react/only-export-components": ["warn", { "allowConstantExport": true }]
  }
}
````

---

## `frontend/src/main.jsx`

````jsx
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import App from "./App";
import "./index.css";
import "./App.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
````

---

## `frontend/src/App.jsx`

````jsx
import { Routes, Route } from "react-router-dom";

import Sidebar from "./components/Sidebar";
import Header from "./components/Header";

import Dashboard from "./pages/Dashboard";
import GIS from "./pages/GIS";
import Sensors from "./pages/Sensors";
import MLPrediction from "./pages/MLPrediction";
import Alerts from "./pages/Alerts";
import History from "./pages/History";

import "./App.css";

function App() {
  return (
    <div className="app-layout">

      <Sidebar />

      <div className="main-area">

        <Header />

        <main className="content-area">

          <Routes>

            <Route path="/" element={<Dashboard />} />
            <Route path="/gis" element={<GIS />} />
            <Route path="/sensors" element={<Sensors />} />
            <Route path="/ml" element={<MLPrediction />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/history" element={<History />} />

          </Routes>

        </main>

      </div>

    </div>
  );
}

export default App;
````

---

## `frontend/src/App.css`

````css
/* =========================
   GLOBAL LAYOUT
========================= */

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: Inter, Arial, sans-serif;
  background: #f4f7f8;
  color: #172a2a;
}

button,
input {
  font-family: inherit;
}

.app-layout {
  display: flex;
  min-height: 100vh;
}

/* =========================
   SIDEBAR
========================= */

.sidebar {
  width: 245px;
  min-height: 100vh;
  background: #103f3e;
  color: white;
  display: flex;
  flex-direction: column;
  padding: 24px 16px;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 10px 30px;
}

.logo-icon {
  width: 42px;
  height: 42px;
  border-radius: 11px;
  background: #2f7f78;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar-logo h2 {
  margin: 0;
  font-size: 17px;
  font-weight: 700;
}

.sidebar-logo span {
  display: block;
  margin-top: 3px;
  font-size: 11px;
  color: #a8c5c2;
}

.sidebar-nav {
  flex: 1;
}

.nav-title {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1px;
  color: #86aaa6;
  padding: 0 12px;
  margin-bottom: 10px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 13px;
  text-decoration: none;
  color: #c5d8d6;
  padding: 12px 13px;
  margin-bottom: 5px;
  border-radius: 9px;
  font-size: 14px;
  font-weight: 500;
  transition: 0.2s ease;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.08);
  color: white;
}

.nav-item.active {
  background: #2e7773;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.sidebar-status {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 13px;
  background: #0b3433;
  border-radius: 10px;
}

.status-icon {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: #174e4b;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #7dd3a8;
}

.sidebar-status strong {
  display: block;
  font-size: 12px;
}

.sidebar-status span:not(.online-dot) {
  display: block;
  margin-top: 3px;
  color: #8eafac;
  font-size: 10px;
}

.online-dot {
  width: 7px;
  height: 7px;
  background: #42d98b;
  border-radius: 50%;
  position: absolute;
  right: 12px;
  top: 13px;
}

/* =========================
   MAIN AREA
========================= */

.main-area {
  margin-left: 245px;
  width: calc(100% - 245px);
  min-height: 100vh;
}

.top-header {
  height: 72px;
  background: white;
  border-bottom: 1px solid #e4ebeb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
}

.header-title h1 {
  margin: 0;
  font-size: 17px;
  font-weight: 700;
  color: #193737;
}

.header-title p {
  margin: 4px 0 0;
  color: #819493;
  font-size: 11px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.live-status {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #239a62;
  font-size: 10px;
  font-weight: 700;
}

.notification-btn {
  position: relative;
  width: 38px;
  height: 38px;
  border: 1px solid #e2e9e8;
  background: white;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #526967;
  cursor: pointer;
}

.notification-count {
  position: absolute;
  right: -4px;
  top: -5px;
  min-width: 17px;
  height: 17px;
  padding: 0 4px;
  background: #dc5b5b;
  color: white;
  border-radius: 20px;
  font-size: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.content-area {
  padding: 30px;
}

/* =========================
   PAGE
========================= */

.page {
  max-width: 1400px;
  margin: 0 auto;
}

.page-heading {
  margin-bottom: 25px;
}

.page-heading h1 {
  margin: 0;
  font-size: 25px;
  color: #173b3a;
}

.page-heading p {
  margin: 7px 0 0;
  color: #7a8d8b;
  font-size: 13px;
}

/* =========================
   DASHBOARD
========================= */

.dashboard-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border: 1px solid #e3ebea;
  border-radius: 14px;
  padding: 20px;
  min-height: 135px;
  box-shadow: 0 2px 8px rgba(24, 55, 54, 0.04);
}

.stat-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-card-header span {
  font-size: 12px;
  color: #718583;
  font-weight: 600;
}

.stat-icon {
  width: 36px;
  height: 36px;
  border-radius: 9px;
  background: #edf6f5;
  color: #2e7773;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-value {
  margin-top: 18px;
  font-size: 27px;
  font-weight: 750;
  color: #173b3a;
}

.risk-badge {
  display: inline-flex;
  align-items: center;
  margin-top: 17px;
  padding: 7px 13px;
  border-radius: 20px;
  background: #fff3d9;
  color: #a66b00;
  font-size: 13px;
  font-weight: 700;
}

.dashboard-section {
  background: white;
  border: 1px solid #e3ebea;
  border-radius: 14px;
  padding: 20px;
  margin-bottom: 22px;
  box-shadow: 0 2px 8px rgba(24, 55, 54, 0.04);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h2 {
  margin: 0;
  font-size: 16px;
  color: #173b3a;
}

.map-placeholder {
  height: 390px;
  border-radius: 11px;
  background: #eaf0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #78908e;
  font-size: 14px;
  text-align: center;
}

.map-placeholder svg {
  display: block;
  margin: 0 auto 10px;
  color: #4d8581;
}

.map-placeholder p {
  margin: 0;
}

/* =========================
   ML PREDICTION
========================= */

.prediction-container {
  max-width: 1000px;
}

.prediction-card {
  background: white;
  border: 1px solid #e3ebea;
  border-radius: 14px;
  padding: 25px;
  box-shadow: 0 2px 8px rgba(24, 55, 54, 0.04);
}

.prediction-form {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 18px 22px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.form-group label {
  font-size: 12px;
  font-weight: 650;
  color: #405957;
}

.form-group input {
  width: 100%;
  height: 43px;
  padding: 0 12px;
  border: 1px solid #d7e2e0;
  border-radius: 8px;
  outline: none;
  font-size: 13px;
  color: #243c3b;
  background: #fbfcfc;
}

.form-group input:focus {
  border-color: #3c8580;
  box-shadow: 0 0 0 3px rgba(60, 133, 128, 0.1);
}

.predict-btn {
  grid-column: 1 / -1;
  height: 46px;
  border: none;
  border-radius: 8px;
  background: #246c68;
  color: white;
  font-weight: 650;
  cursor: pointer;
  transition: 0.2s ease;

  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.predict-btn:hover {
  background: #1d5b57;
}

.predict-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.prediction-result {
  margin-top: 22px;
  padding: 20px;
  border-radius: 11px;
  background: #f1f7f6;
  border: 1px solid #d6e7e4;
}

.prediction-result h2 {
  margin: 0 0 15px;
  font-size: 17px;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.result-item {
  background: white;
  padding: 14px;
  border-radius: 8px;
}

.result-item span {
  display: block;
  color: #7b8e8c;
  font-size: 11px;
  margin-bottom: 5px;
}

.result-item strong {
  font-size: 16px;
  color: #173b3a;
}

/* =========================
   RESPONSIVE
========================= */

@media (max-width: 1000px) {
  .dashboard-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .sidebar {
    width: 210px;
  }

  .main-area {
    margin-left: 210px;
    width: calc(100% - 210px);
  }
}

@media (max-width: 700px) {
  .sidebar {
    width: 70px;
    padding: 20px 10px;
  }

  .sidebar-logo div:last-child,
  .nav-item span,
  .nav-title,
  .sidebar-status div:last-of-type,
  .online-dot {
    display: none;
  }

  .sidebar-logo {
    justify-content: center;
    padding: 4px 0 30px;
  }

  .nav-item {
    justify-content: center;
  }

  .main-area {
    margin-left: 70px;
    width: calc(100% - 70px);
  }

  .content-area {
    padding: 20px;
  }

  .dashboard-cards {
    grid-template-columns: 1fr;
  }

  .prediction-form {
    grid-template-columns: 1fr;
  }

  .result-grid {
    grid-template-columns: 1fr;
  }
}
/* =========================
   GIS MAP
========================= */

.gis-toolbar {
  background: white;
  border: 1px solid #e3ebea;
  border-radius: 14px;
  padding: 15px 18px;
  margin-bottom: 18px;

  display: flex;
  align-items: center;
  justify-content: space-between;

  box-shadow: 0 2px 8px rgba(24, 55, 54, 0.04);
}

.gis-info {
  display: flex;
  align-items: center;
  gap: 11px;
}

.gis-info strong {
  display: block;
  color: #173b3a;
  font-size: 13px;
}

.gis-info span {
  display: block;
  margin-top: 3px;
  color: #7a8d8b;
  font-size: 11px;
}

.gis-tools {
  display: flex;
  gap: 9px;
}

.gis-tool {
  display: flex;
  align-items: center;
  gap: 7px;

  padding: 8px 11px;

  border: 1px solid #dce6e4;
  border-radius: 7px;

  color: #58706e;
  font-size: 11px;
  font-weight: 600;
}

.gis-map-card {
  background: white;
  border: 1px solid #e3ebea;
  border-radius: 14px;
  padding: 10px;

  box-shadow: 0 2px 8px rgba(24, 55, 54, 0.04);
}

.gis-map {
  height: 620px;
  width: 100%;
  border-radius: 10px;
  overflow: hidden;
}

.leaflet-control-attribution {
  font-size: 9px;
}
/* =========================
   GIS LEGEND
========================= */

.gis-legend {
  margin-top: 14px;
  background: white;
  border: 1px solid #e3ebea;
  border-radius: 12px;
  padding: 15px 18px;
  box-shadow: 0 2px 8px rgba(24, 55, 54, 0.04);
}

.legend-title {
  font-size: 12px;
  font-weight: 700;
  color: #173b3a;
  margin-bottom: 12px;
}

.legend-items {
  display: flex;
  align-items: center;
  gap: 22px;
  flex-wrap: wrap;
}

.legend-items > div {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 11px;
  color: #627572;
}

.legend-color {
  width: 18px;
  height: 10px;
  border-radius: 3px;
}

.very-low {
  background: #2e8b57;
}

.low {
  background: #9acd32;
}

.medium {
  background: #f1c40f;
}

.high {
  background: #e67e22;
}

.very-high {
  background: #c0392b;
}

.raster-status {
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid #edf1f0;
  font-size: 10px;
}

.status-success {
  color: #23845a;
}

.status-loading {
  color: #a66b00;
}

.gis-loading {
  position: absolute;
  z-index: 1000;
  top: 12px;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  padding: 8px 13px;
  border-radius: 7px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
  font-size: 11px;
  color: #526967;
}
.sensor-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-top: 20px;
}

.sensor-card {
  background: white;
  border: 1px solid #e3ebea;
  border-radius: 12px;
  padding: 18px;
  box-shadow: 0 2px 8px rgba(24, 55, 54, 0.04);
}

.sensor-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 14px;
  border-bottom: 1px solid #edf1f0;
}

.sensor-card-header h3 {
  margin: 0;
  color: #173b3a;
  font-size: 16px;
}

.sensor-card-header span {
  display: block;
  margin-top: 4px;
  font-size: 11px;
  color: #23845a;
}

.sensor-status-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: #2e9b6f;
}

.sensor-location {
  margin: 14px 0;
  font-size: 11px;
  color: #71817f;
}

.sensor-readings {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.sensor-reading {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 10px;
  background: #f7faf9;
  border-radius: 8px;
}

.sensor-reading svg {
  color: #2e7773;
  flex-shrink: 0;
}

.sensor-reading span {
  display: block;
  font-size: 10px;
  color: #71817f;
}

.sensor-reading strong {
  display: block;
  margin-top: 3px;
  font-size: 12px;
  color: #173b3a;
}

@media (max-width: 1000px) {
  .sensor-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 650px) {
  .sensor-grid {
    grid-template-columns: 1fr;
  }
}
.sensor-risk {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 14px 0;
  padding: 12px;
  border-radius: 8px;
  background: #f7faf9;
}

.sensor-risk span {
  display: block;
  font-size: 10px;
  color: #71817f;
}

.sensor-risk strong {
  display: block;
  margin-top: 3px;
  font-size: 14px;
  color: #c0392b;
}

.risk-score {
  font-size: 20px;
  font-weight: 700;
  color: #173b3a;
}
.sensor-risk-legend {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #edf1f0;
}

.risk-dot {
  width: 11px;
  height: 11px;
  border-radius: 50%;
  display: inline-block;
}

.risk-low {
  background: #2e8b57;
}

.risk-medium {
  background: #f1c40f;
}

.risk-high {
  background: #e67e22;
}

.risk-critical {
  background: #c0392b;
}
.dashboard-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 16px;
  margin-top: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.section-header h2 {
  margin: 0;
  font-size: 15px;
  color: #173b3a;
}

.section-header p {
  margin: 4px 0 0;
  font-size: 11px;
  color: #71817f;
}

.section-header > svg {
  color: #2e7773;
}

.risk-summary {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.risk-summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 11px 0;
  border-bottom: 1px solid #edf1f0;
}

.risk-summary-row:last-child {
  border-bottom: none;
}

.risk-summary-row span {
  font-size: 11px;
  color: #71817f;
}

.risk-summary-row strong {
  font-size: 12px;
  color: #173b3a;
}

.empty-state {
  min-height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 10px;
  color: #71817f;
  font-size: 12px;
}

.empty-state svg {
  color: #2e7773;
}

.sensor-overview {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.sensor-overview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 13px;
  background: #f7faf9;
  border-radius: 8px;
}

.sensor-overview-item > div {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sensor-overview-item strong {
  font-size: 13px;
  color: #173b3a;
}

.sensor-overview-item span {
  font-size: 10px;
  color: #71817f;
}

.overview-risk {
  padding: 5px 9px;
  border-radius: 5px;
  font-size: 9px !important;
  font-weight: 700;
}

.overview-risk.low {
  background: #e4f4eb;
  color: #23845a;
}

.overview-risk.medium {
  background: #fff5d9;
  color: #a66b00;
}

.overview-risk.high {
  background: #fff0df;
  color: #c06b16;
}

.overview-risk.critical {
  background: #fde5e3;
  color: #b9362e;
}

@media (max-width: 900px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .sensor-overview {
    grid-template-columns: 1fr;
  }
}
/* =========================================
   DASHBOARD UI REFINEMENT
   ========================================= */

.dashboard-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 18px;
}

.dashboard-cards .stat-card {
  min-height: 92px;
  padding: 16px 18px;
  display: flex;
  align-items: center;
  gap: 13px;
}

.dashboard-cards .stat-label {
  display: block;
  font-size: 11px;
  font-weight: 500;
  color: #71817f;
  margin-bottom: 5px;
}

.dashboard-cards .stat-value {
  font-size: 24px;
  line-height: 1.1;
  font-weight: 700;
  color: #173b3a;
}

.dashboard-cards .stat-icon {
  width: 38px;
  height: 38px;
  min-width: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
}


/* Dashboard sections */

.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) minmax(300px, 0.85fr);
  gap: 16px;
  margin-top: 0;
}

.dashboard-section {
  background: white;
  border: 1px solid #e3ebea;
  border-radius: 12px;
  padding: 18px;
  box-shadow: 0 2px 8px rgba(24, 55, 54, 0.04);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 14px;
}

.section-header h2 {
  margin: 0;
  font-size: 14px;
  line-height: 1.3;
  font-weight: 650;
  color: #173b3a;
}

.section-header p {
  margin: 4px 0 0;
  font-size: 10px;
  line-height: 1.4;
  color: #71817f;
}

.section-header > svg {
  width: 18px;
  height: 18px;
  color: #2e7773;
}


/* GIS preview */

.map-placeholder {
  min-height: 260px;
  border-radius: 10px;
  background: #f1f6f5;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  text-align: center;
  padding: 20px;
  box-sizing: border-box;
}

.map-placeholder svg {
  width: 34px;
  height: 34px;
  color: #4c8985;
  margin-bottom: 10px;
}

.map-placeholder strong {
  display: block;
  font-size: 13px;
  font-weight: 650;
  color: #3f7774;
  margin-bottom: 5px;
}

.map-placeholder span {
  display: block;
  max-width: 360px;
  font-size: 10px;
  line-height: 1.5;
  color: #71817f;
}


/* Risk summary */

.risk-summary {
  display: flex;
  flex-direction: column;
}

.risk-summary-row {
  min-height: 38px;
  box-sizing: border-box;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #edf1f0;
}

.risk-summary-row:last-child {
  border-bottom: none;
}

.risk-summary-row span {
  font-size: 10px;
  color: #71817f;
}

.risk-summary-row strong {
  font-size: 11px;
  font-weight: 650;
  color: #173b3a;
}


/* Sensor overview */

.dashboard-section:last-child {
  margin-top: 16px;
}

.sensor-overview {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.sensor-overview-item {
  min-height: 52px;
  box-sizing: border-box;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: #f7faf9;
  border-radius: 8px;
}

.sensor-overview-item > div {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.sensor-overview-item strong {
  font-size: 11px;
  font-weight: 650;
  color: #173b3a;
}

.sensor-overview-item span {
  font-size: 9px;
  color: #71817f;
}

.overview-risk {
  padding: 4px 7px;
  border-radius: 5px;
  font-size: 8px !important;
  font-weight: 700;
}


/* Empty state */

.empty-state {
  min-height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 8px;
  color: #71817f;
  font-size: 11px;
}


/* Responsive */

@media (max-width: 1100px) {

  .dashboard-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .sensor-overview {
    grid-template-columns: repeat(2, 1fr);
  }

}


@media (max-width: 650px) {

  .dashboard-cards {
    grid-template-columns: 1fr;
  }

  .sensor-overview {
    grid-template-columns: 1fr;
  }

}
/* =========================================
   REMOVE EXTRA DASHBOARD SPACE
   ========================================= */

.dashboard-grid {
  align-items: start;
}

.dashboard-grid > .dashboard-section {
  align-self: start;
}

/* Keep Risk Summary compact */
.dashboard-grid > .dashboard-section:nth-child(2) {
  height: fit-content;
}

/* Slightly reduce GIS preview height */
.dashboard-grid .map-placeholder {
  min-height: 230px;
  height: 230px;
}

/* =========================================
   ALERTS PAGE
   ========================================= */

.alert-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.alert-item {
  display: flex;
  align-items: flex-start;
  gap: 13px;
  padding: 14px;
  border-radius: 9px;
  border: 1px solid #e3ebea;
  background: #fafcfc;
}

.alert-item.critical {
  border-left: 4px solid #c0392b;
  background: #fff8f7;
}

.alert-item.high {
  border-left: 4px solid #e67e22;
  background: #fffaf5;
}

.alert-icon {
  width: 38px;
  height: 38px;
  min-width: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
}

.alert-item.critical .alert-icon {
  background: #fde5e3;
  color: #c0392b;
}

.alert-item.high .alert-icon {
  background: #fff0df;
  color: #d47720;
}

.alert-content {
  flex: 1;
  min-width: 0;
}

.alert-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.alert-title-row strong {
  font-size: 12px;
  color: #173b3a;
}

.alert-time {
  font-size: 9px;
  color: #23845a;
  font-weight: 600;
}

.alert-content p {
  margin: 5px 0 10px;
  font-size: 10px;
  line-height: 1.5;
  color: #71817f;
}

.alert-details {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.alert-details span {
  padding: 5px 8px;
  background: white;
  border: 1px solid #e7eeee;
  border-radius: 5px;
  font-size: 9px;
  color: #71817f;
}

.alert-details strong {
  color: #173b3a;
}

.alert-empty {
  min-height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 7px;
  text-align: center;
  color: #71817f;
  font-size: 11px;
}

.alert-empty svg {
  color: #2e7773;
}

.alert-empty strong {
  font-size: 13px;
  color: #173b3a;
}

.alert-empty span {
  font-size: 10px;
}


/* =========================================
   DASHBOARD WEATHER CARD REFINEMENT
   ========================================= */

.weather-section {
  margin-top: 22px;
}

.weather-location-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
  margin-top: 20px;
  align-items: stretch;
}

.weather-location-card {
  min-width: 0;
  padding: 20px;
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 16px;
  background: var(--card-bg, #ffffff);
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.045);
  transition: transform 0.2s ease, box-shadow 0.2s ease,
    border-color 0.2s ease;
}

.weather-location-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 9px 22px rgba(15, 23, 42, 0.09);
  border-color: #93b4d8;
}

.weather-location-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 20px;
}

.weather-location-heading h3 {
  margin: 0 0 7px;
  font-size: 17px;
  font-weight: 700;
  line-height: 1.4;
  overflow-wrap: anywhere;
}

.weather-location-heading > svg {
  flex-shrink: 0;
  color: #4385c5;
  margin-top: 2px;
}

.weather-location-id {
  display: block;
  color: #718096;
  font-size: 11px;
  line-height: 1.5;
}

.weather-primary-value {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 9px;
  padding: 15px;
  margin-bottom: 16px;
  border-radius: 12px;
  background: #eff6ff;
  color: #245b96;
}

.weather-primary-value > svg {
  flex-shrink: 0;
}

.weather-primary-value strong {
  font-size: 25px;
  font-weight: 750;
  line-height: 1.2;
}

.weather-primary-value span {
  width: 100%;
  padding-left: 29px;
  color: #58718d;
  font-size: 12px;
}

.weather-readings {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.weather-readings > div {
  display: grid;
  grid-template-columns: 18px minmax(0, 1fr);
  align-items: center;
  column-gap: 7px;
  row-gap: 7px;
  min-width: 0;
  padding: 12px;
  border: 1px solid #edf0f4;
  border-radius: 10px;
  background: #fafbfd;
}

.weather-readings > div > svg {
  color: #68819b;
}

.weather-readings > div > span {
  min-width: 0;
  color: #718096;
  font-size: 11px;
  line-height: 1.4;
}

.weather-readings > div > strong {
  grid-column: 1 / -1;
  color: #26364a;
  font-size: 15px;
  font-weight: 700;
  overflow-wrap: anywhere;
}

.weather-source {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 8px;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #edf0f4;
  color: #7b8796;
  font-size: 10px;
  line-height: 1.6;
}

.weather-source span {
  min-width: 0;
  overflow-wrap: anywhere;
}

.weather-prediction-note {
  display: flex;
  flex-direction: column;
  gap: 7px;
  margin-top: 15px;
  padding: 12px;
  border: 1px solid #f0dfb7;
  border-radius: 10px;
  background: #fffbef;
}

.weather-prediction-note strong {
  color: #8a641c;
  font-size: 12px;
  line-height: 1.5;
}

.weather-prediction-note span {
  color: #76684b;
  font-size: 11px;
  line-height: 1.6;
}

.weather-unavailable {
  padding: 18px 12px;
  border-radius: 10px;
  background: #f8fafc;
  color: #718096;
  font-size: 13px;
  line-height: 1.6;
  text-align: center;
}

/* Medium screens */
@media (max-width: 1100px) {
  .weather-location-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

/* Mobile screens */
@media (max-width: 650px) {
  .weather-location-grid {
    grid-template-columns: minmax(0, 1fr);
    gap: 14px;
  }

  .weather-location-card {
    padding: 16px;
  }

  .weather-location-heading h3 {
    font-size: 16px;
  }

  .weather-primary-value strong {
    font-size: 23px;
  }
}

/* Dashboard and weather-card visual refinements */
.dashboard-grid {
  grid-template-columns: minmax(0, 1.45fr) minmax(280px, 0.85fr);
  align-items: stretch;
  gap: 18px;
}

.dashboard-grid > .dashboard-section {
  min-width: 0;
  height: auto;
  align-self: stretch;
  padding: 20px;
  border-radius: 14px;
}

.dashboard-grid .section-header {
  align-items: center;
  min-height: 38px;
  margin-bottom: 16px;
}

.dashboard-grid .section-header h2 {
  font-size: 15px;
  line-height: 1.4;
}

.dashboard-grid .section-header p {
  font-size: 11px;
  line-height: 1.5;
}

.dashboard-grid > .dashboard-section:nth-child(2) {
  height: auto;
}

.dashboard-grid .map-placeholder {
  min-height: 264px;
  height: 264px;
  border: 1px solid #e1eeeb;
  border-radius: 12px;
  background: linear-gradient(145deg, #f2f8f6, #eaf3f1);
  gap: 2px;
  padding: 24px;
}

.dashboard-grid .map-placeholder svg {
  width: 38px;
  height: 38px;
  color: #2e7773;
  margin-bottom: 12px;
}

.dashboard-grid .map-placeholder strong {
  color: #173b3a;
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 6px;
}

.dashboard-grid .map-placeholder span {
  color: #607875;
  font-size: 11px;
  line-height: 1.6;
}

.dashboard-grid .map-placeholder a {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 36px;
  margin-top: 14px;
  padding: 0 14px;
  border: 1px solid #2e7773;
  border-radius: 8px;
  background: #2e7773;
  color: #ffffff;
  font-size: 11px;
  font-weight: 650;
  text-decoration: none;
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

.dashboard-grid .map-placeholder a:hover {
  border-color: #205f5b;
  background: #205f5b;
}

.dashboard-grid .risk-summary {
  min-height: 264px;
  justify-content: center;
}

.dashboard-grid .risk-summary-row {
  min-height: 40px;
  gap: 14px;
  padding: 9px 2px;
  border-bottom-color: #e8efed;
}

.dashboard-grid .risk-summary-row span {
  color: #718583;
  font-size: 11px;
}

.dashboard-grid .risk-summary-row strong {
  color: #173b3a;
  font-size: 12px;
  font-weight: 700;
  text-align: right;
  overflow-wrap: anywhere;
}

.weather-section .section-header h2 {
  font-size: 16px;
  line-height: 1.4;
}

.weather-section .section-header p {
  color: #637b77;
  font-size: 11px;
  line-height: 1.5;
}

.weather-section .section-header > svg {
  color: #2e7773;
}

.weather-location-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-top: 18px;
}

.weather-location-card {
  display: flex;
  min-width: 0;
  flex-direction: column;
  padding: 18px;
  border: 1px solid #dce9e6;
  border-radius: 14px;
  background: linear-gradient(160deg, #ffffff 0%, #fbfdfc 100%);
  box-shadow: 0 3px 12px rgba(16, 63, 62, 0.055);
}

.weather-location-card:hover {
  transform: translateY(-2px);
  border-color: #8cb8b1;
  box-shadow: 0 8px 20px rgba(16, 63, 62, 0.1);
}

.weather-location-heading {
  gap: 10px;
  margin-bottom: 16px;
}

.weather-location-heading h3 {
  margin-bottom: 5px;
  color: #173b3a;
  font-size: 16px;
  line-height: 1.35;
}

.weather-location-heading > svg {
  color: #2e7773;
}

.weather-location-id {
  color: #6b817e;
  font-size: 11px;
  line-height: 1.45;
}

.weather-primary-value {
  gap: 8px;
  padding: 14px;
  margin-bottom: 14px;
  border: 1px solid #dcece8;
  border-radius: 11px;
  background: #eff7f4;
  color: #246b65;
}

.weather-primary-value > svg {
  color: #2e7773;
}

.weather-primary-value strong {
  color: #173b3a;
  font-size: 24px;
}

.weather-primary-value span {
  padding-left: 28px;
  color: #607875;
  font-size: 11px;
  font-weight: 550;
}

.weather-readings {
  gap: 9px;
}

.weather-readings > div {
  column-gap: 6px;
  row-gap: 6px;
  padding: 11px;
  border-color: #e6efed;
  border-radius: 9px;
  background: #f7faf9;
}

.weather-readings > div > svg {
  color: #397d76;
}

.weather-readings > div > span {
  color: #637b77;
  font-size: 10px;
  font-weight: 550;
}

.weather-readings > div > strong {
  color: #173b3a;
  font-size: 15px;
  line-height: 1.25;
}

.weather-location-card .weather-source {
  gap: 6px 10px;
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid #e6efed;
  color: #657b78;
  font-size: 10px;
}

.weather-location-card .weather-source span:last-child {
  color: #536d69;
  font-weight: 550;
}

.weather-location-card .weather-source span:last-child svg {
  color: #2e7773;
}

.weather-prediction-note {
  gap: 6px;
  margin-top: 13px;
  padding: 11px 12px;
  border-color: #dce9e6;
  border-radius: 9px;
  background: #f3f8f6;
}

.weather-screening-heading {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.weather-screening-heading > strong {
  color: #285f5a;
  font-size: 12px;
  line-height: 1.4;
}

.weather-screening-status {
  display: inline-flex;
  align-items: center;
  min-height: 23px;
  padding: 3px 8px;
  border: 1px solid #cbdcd8;
  border-radius: 999px;
  background: #eaf1ef;
  color: #405d58;
  font-size: 9px;
  font-weight: 750;
  letter-spacing: 0.04em;
  line-height: 1;
}

.weather-risk-metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-top: 4px;
}

.weather-risk-metric {
  display: grid;
  grid-template-columns: 18px minmax(0, 1fr);
  align-items: center;
  column-gap: 6px;
  row-gap: 5px;
  min-width: 0;
  padding: 9px;
  border: 1px solid #dfeae7;
  border-radius: 8px;
  background: #ffffff;
}

.weather-risk-metric > svg {
  color: #397d76;
}

.weather-risk-metric > span {
  min-width: 0;
  color: #637b77;
  font-size: 9px;
  line-height: 1.35;
}

.weather-risk-metric > strong {
  grid-column: 1 / -1;
  color: #173b3a;
  font-size: 14px;
  line-height: 1.3;
  overflow-wrap: anywhere;
}

.weather-prediction-note .weather-risk-observed {
  color: #72827f;
  font-size: 9px;
  line-height: 1.4;
}

.weather-risk-explanation {
  border-top: 1px solid #dce9e6;
  padding-top: 8px;
}

.weather-risk-explanation summary {
  color: #285f5a;
  cursor: pointer;
  font-size: 10px;
  font-weight: 650;
  line-height: 1.5;
}

.weather-risk-explanation summary:hover {
  color: #173b3a;
}

.weather-risk-explanation > div {
  padding-top: 5px;
}

.weather-risk-explanation p {
  margin: 5px 0 0;
  color: #607875;
  font-size: 10px;
  line-height: 1.55;
}

.weather-prediction-note .weather-risk-disclaimer {
  margin: 2px 0 0;
  padding-top: 8px;
  border-top: 1px solid #dce9e6;
  color: #285f5a;
  font-size: 10px;
  font-weight: 650;
  line-height: 1.5;
}

.weather-unavailable {
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  min-height: 130px;
  border: 1px dashed #d7e5e1;
  background: #f7faf9;
  color: #637b77;
  font-size: 12px;
}

@media (max-width: 1100px) {
  .weather-location-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
  }
}

@media (max-width: 650px) {
  .dashboard-grid {
    grid-template-columns: minmax(0, 1fr);
    gap: 14px;
  }

  .dashboard-grid .map-placeholder {
    min-height: 230px;
    height: 230px;
    padding: 18px;
  }

  .weather-location-grid {
    grid-template-columns: minmax(0, 1fr);
    gap: 12px;
  }

  .weather-risk-metrics {
    gap: 7px;
  }

  .weather-risk-metric {
    padding: 8px;
  }
}

/* Risk History page */

.history-panel {
  margin-top: 24px;
  padding: 24px;
  background: #ffffff;
  border: 1px solid #e2e8e8;
  border-radius: 14px;
  overflow: hidden;
}

.history-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.history-toolbar h2 {
  margin: 0 0 6px;
  font-size: 20px;
}

.history-toolbar p {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

.history-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.history-actions select,
.history-actions button {
  min-height: 40px;
  padding: 9px 12px;
  border: 1px solid #d6e0e0;
  border-radius: 8px;
  background: #ffffff;
  font: inherit;
}

.history-actions button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
}

.history-actions button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.history-table-wrapper {
  width: 100%;
  overflow-x: auto;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 13px;
}

.history-table th,
.history-table td {
  padding: 13px 12px;
  border-bottom: 1px solid #e8eeee;
  white-space: nowrap;
}

.history-table th {
  background: #f4f8f8;
  color: #475569;
  font-weight: 600;
}

.history-table tbody tr:hover {
  background: #f8fbfb;
}

.history-risk {
  display: inline-block;
  padding: 5px 9px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.history-risk.high {
  background: #fee2e2;
  color: #b91c1c;
}

.history-risk.medium {
  background: #fef3c7;
  color: #92400e;
}

.history-risk.low {
  background: #dcfce7;
  color: #166534;
}

.history-risk.unknown {
  background: #e2e8f0;
  color: #475569;
}

.history-message {
  padding: 24px 12px;
  color: #64748b;
  text-align: center;
}

.history-error {
  padding: 12px;
  border-radius: 8px;
  background: #fee2e2;
  color: #b91c1c;
}

@media (max-width: 768px) {
  .history-panel {
    padding: 16px;
  }

  .history-toolbar {
    align-items: flex-start;
  }

  .history-actions {
    width: 100%;
  }

  .history-actions select,
  .history-actions button {
    max-width: 100%;
  }
}

/* =========================
   DATA SOURCE BADGES & NOTICE
========================= */

.data-source-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 9px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.data-source-badge.live {
  background: #e4f4eb;
  color: #23845a;
  border: 1px solid #c2e7d3;
}

.data-source-badge.stale {
  background: #fff5d9;
  color: #a66b00;
  border: 1px solid #f9df97;
}

.data-source-badge.simulated {
  background: #e8eef6;
  color: #2b5c8f;
  border: 1px solid #c8d9ed;
}

.data-source-badge.nodata {
  background: #fde5e3;
  color: #b9362e;
  border: 1px solid #f8b8b3;
}

.stale-banner {
  background: #fffbeb;
  border: 1px solid #fde68a;
  color: #92400e;
  padding: 12px 16px;
  border-radius: 10px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  font-weight: 500;
}

.calibration-notice {
  display: inline-block;
  margin-left: 6px;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 9px;
  font-weight: 600;
  background: #fef3c7;
  color: #92400e;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
````

---

## `frontend/src/index.css`

````css
html,
body,
#root {
  margin: 0;
  min-height: 100%;
  width: 100%;
}

html {
  font-family: Inter, Arial, sans-serif;
}

body {
  margin: 0;
}
````

---

## `frontend/src/components/Header.jsx`

````jsx
import { Bell, Circle } from "lucide-react";

function Header() {
  return (
    <header className="top-header">

      <div className="header-title">
        <h1>Landslide Monitoring Dashboard</h1>
        <p>Nilgiris District, Tamil Nadu</p>
      </div>

      <div className="header-actions">

        <div className="live-status">
          <Circle size={9} fill="currentColor" />
          <span>LIVE</span>
        </div>

        <button className="notification-btn">
          <Bell size={19} />
          <span className="notification-count">3</span>
        </button>

      </div>

    </header>
  );
}

export default Header;
````

---

## `frontend/src/components/LiveTelemetry.jsx`

````jsx
import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000/api/telemetry/latest";

function display(value, digits = 2) {
  if (value === null || value === undefined || !Number.isFinite(value)) {
    return "—";
  }
  return Number(value).toFixed(digits);
}

export default function LiveTelemetry() {
  const [reading, setReading] = useState(null);
  const [message, setMessage] = useState("Waiting for sensor data");

  useEffect(() => {
    let active = true;

    async function refresh() {
      try {
        const response = await fetch(API_URL);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const result = await response.json();
        if (!active) return;

        setReading(result.available ? result.data : null);
        setMessage(
          result.available
            ? "Live telemetry connected"
            : "Waiting for the first reading"
        );
      } catch (error) {
        if (!active) return;
        setMessage(`Backend connection error: ${error.message}`);
      }
    }

    refresh();
    const timer = setInterval(refresh, 2000);

    return () => {
      active = false;
      clearInterval(timer);
    };
  }, []);

  return (
    <section style={{ padding: 20 }}>
      <h2>ESP32 Live Telemetry</h2>
      <p>{message}</p>

      {!reading ? (
        <p>Start both ESP32 boards and the Python bridge to see data.</p>
      ) : (
        <>
          <p>Sequence: {reading.sequence}</p>
          <p>Uptime: {reading.uptime_ms} ms</p>
          <p>GPS valid: {reading.gps_valid ? "Yes" : "No"}</p>
          <p>MPU6050 valid: {reading.mpu_valid ? "Yes" : "No"}</p>
          <p>
            Rain input:{" "}
            {reading.rain_detected ? "Triggered" : "Not triggered"}
          </p>

          <h3>Sensor values</h3>
          <ul>
            <li>Soil raw ADC: {reading.soil_raw}</li>
            <li>Latitude: {display(reading.latitude, 6)}</li>
            <li>Longitude: {display(reading.longitude, 6)}</li>
            <li>Acceleration X: {display(reading.accel_x)} m/s²</li>
            <li>Acceleration Y: {display(reading.accel_y)} m/s²</li>
            <li>Acceleration Z: {display(reading.accel_z)} m/s²</li>
            <li>Gyroscope X: {display(reading.gyro_x)}</li>
            <li>Gyroscope Y: {display(reading.gyro_y)}</li>
            <li>Gyroscope Z: {display(reading.gyro_z)}</li>
          </ul>

          <p>
            Prototype readings only. Soil ADC is not a calibrated
            moisture percentage, and the digital rain flag is not rainfall
            in millimetres.
          </p>
        </>
      )}
    </section>
  );
}
````

---

## `frontend/src/components/Sidebar.jsx`

````jsx
import {
  LayoutDashboard,
  Map,
  RadioTower,
  BrainCircuit,
  BellRing,
  History,
  ShieldAlert,
  Activity,
} from "lucide-react";

import { NavLink } from "react-router-dom";

function Sidebar() {
  const menuItems = [
    {
      name: "Dashboard",
      path: "/",
      icon: LayoutDashboard,
    },
    {
      name: "Live GIS",
      path: "/gis",
      icon: Map,
    },
    {
      name: "Sensors",
      path: "/sensors",
      icon: RadioTower,
    },
    {
      name: "ML Prediction",
      path: "/ml",
      icon: BrainCircuit,
    },
    {
      name: "Alerts",
      path: "/alerts",
      icon: BellRing,
    },
    {
      name: "History",
      path: "/history",
      icon: History,
    },
  ];

  return (
    <aside className="sidebar">

      <div className="sidebar-logo">
        <div className="logo-icon">
          <ShieldAlert size={24} />
        </div>

        <div>
          <h2>Landslide</h2>
          <span>Early Warning</span>
        </div>
      </div>

      <nav className="sidebar-nav">

        <div className="nav-title">
          MONITORING
        </div>

        {menuItems.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                isActive ? "nav-item active" : "nav-item"
              }
            >
              <Icon size={19} />
              <span>{item.name}</span>
            </NavLink>
          );
        })}

      </nav>

      <div className="sidebar-status">
        <div className="status-icon">
          <Activity size={18} />
        </div>

        <div>
          <strong>System Online</strong>
          <span>Monitoring active</span>
        </div>

        <span className="online-dot"></span>
      </div>

    </aside>
  );
}

export default Sidebar;
````

---

## `frontend/src/pages/Dashboard.jsx`

````jsx
import { useEffect, useState } from "react";
import {
  ShieldAlert,
  RadioTower,
  Activity,
  AlertTriangle,
  Map,
  BrainCircuit,
  CheckCircle2,
  CloudRain,
  Thermometer,
  Droplets,
  Gauge,
  MapPin,
  Clock,
  AlertCircle,
} from "lucide-react";

function DataSourceBadge({ source }) {
  const norm = (source || "SIMULATED").toUpperCase();
  let cls = "simulated";
  let label = "SIMULATED";

  if (norm === "LIVE_CSV" || norm === "LIVE") {
    cls = "live";
    label = "LIVE CSV";
  } else if (norm === "STALE") {
    cls = "stale";
    label = "STALE DATA";
  } else if (norm === "NO_DATA") {
    cls = "nodata";
    label = "NO DATA";
  }

  return <span className={`data-source-badge ${cls}`}>{label}</span>;
}

function Dashboard() {
  const [sensors, setSensors] = useState([]);
  const [dataSource, setDataSource] = useState("SIMULATED");
  const [weatherLocations, setWeatherLocations] = useState([]);
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [weatherLoading, setWeatherLoading] = useState(true);
  const [weatherError, setWeatherError] = useState("");

  // Load sensor-risk data every 3 seconds
  useEffect(() => {
    let active = true;

    const fetchRiskData = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/risk");
        if (!response.ok) {
          throw new Error("Could not load sensor risk data");
        }
        const data = await response.json();
        if (active) {
          setSensors(data.sensors || []);
          setDataSource(data.data_source || "SIMULATED");
          setError("");
          setLoading(false);
        }
      } catch (err) {
        if (active) {
          console.error("Dashboard risk loading error:", err);
          setError("Backend connection error. Ensure FastAPI is running on port 8000.");
          setLoading(false);
        }
      }
    };

    fetchRiskData();
    const interval = setInterval(fetchRiskData, 3000);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  // Load named monitoring locations.
  useEffect(() => {
    let active = true;

    const fetchLocations = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/locations");
        if (!response.ok) {
          throw new Error("Could not load monitoring locations");
        }
        const data = await response.json();
        if (active) {
          setLocations(data.locations || []);
        }
      } catch (err) {
        console.error("Location loading error:", err);
      }
    };

    fetchLocations();
    return () => {
      active = false;
    };
  }, []);

  // Load weather API readings
  useEffect(() => {
    let active = true;

    const fetchWeather = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/weather-risk");
        if (!response.ok) {
          throw new Error("Could not load weather data");
        }
        const data = await response.json();
        if (active) {
          setWeatherLocations(data.locations || []);
          setWeatherError("");
          setWeatherLoading(false);
        }
      } catch (err) {
        if (active) {
          console.error("Weather loading error:", err);
          setWeatherError("Weather data could not be loaded.");
          setWeatherLoading(false);
        }
      }
    };

    fetchWeather();
    const interval = setInterval(fetchWeather, 60000);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  // Calculate sensor dashboard values.
  const highestScore =
    sensors.length > 0 ? Math.max(...sensors.map((sensor) => sensor.risk_score ?? 0)) : 0;

  const highestRiskSensor =
    sensors.length > 0
      ? sensors.reduce((highest, sensor) =>
          (sensor.risk_score ?? 0) > (highest.risk_score ?? 0) ? sensor : highest
        )
      : null;

  const averageScore =
    sensors.length > 0
      ? Math.round(
          sensors.reduce((total, sensor) => total + (sensor.risk_score ?? 0), 0) / sensors.length
        )
      : 0;

  const highRiskSensors = sensors.filter(
    (sensor) => sensor.risk_level === "HIGH" || sensor.risk_level === "CRITICAL"
  ).length;

  let overallRisk = "LOW";
  if (highestScore >= 75) {
    overallRisk = "CRITICAL";
  } else if (highestScore >= 50) {
    overallRisk = "HIGH";
  } else if (highestScore >= 25) {
    overallRisk = "MEDIUM";
  }

  const getSensorLocationName = (sensor) => {
    if (sensor.location?.latitude != null && sensor.location?.gps_valid) {
      return `GPS: ${sensor.location.latitude.toFixed(4)}, ${sensor.location.longitude.toFixed(4)}`;
    }
    const location = locations.find((item) => item.sensor_id === sensor.sensor_id);
    if (location?.name) return location.name;
    return sensor.sensor_id === "NODE-01" ? "Field Node (No GPS fix)" : `Sensor ${sensor.sensor_id}`;
  };

  const formatValue = (value, unit = "") => {
    return value === null || value === undefined ? "N/A" : `${value}${unit}`;
  };

  const formatObservedTime = (time) => {
    if (!time) return "Time unavailable";
    return time.replace("T", " ");
  };

  return (
    <div className="page">
      <div className="page-heading">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "10px" }}>
          <div>
            <h1>Dashboard</h1>
            <p>Landslide monitoring and environmental conditions across Nilgiris District</p>
          </div>
          <div>
            <DataSourceBadge source={dataSource} />
          </div>
        </div>
      </div>

      {/* Backend error notice */}
      {error && (
        <div className="history-error" style={{ marginBottom: "20px", display: "flex", alignItems: "center", gap: "10px" }}>
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* Main statistics */}
      <div className="dashboard-cards">
        <div className="stat-card">
          <div className="stat-icon">
            <ShieldAlert size={20} />
          </div>
          <div>
            <span className="stat-label">Overall Sensor Risk</span>
            <div className="stat-value">{loading ? "..." : overallRisk}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <RadioTower size={20} />
          </div>
          <div>
            <span className="stat-label">Active Sensors</span>
            <div className="stat-value">{loading ? "..." : sensors.length}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <Activity size={20} />
          </div>
          <div>
            <span className="stat-label">Average Risk Score</span>
            <div className="stat-value">{loading ? "..." : `${averageScore}/100`}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <AlertTriangle size={20} />
          </div>
          <div>
            <span className="stat-label">High/Critical Sensors</span>
            <div className="stat-value">{loading ? "..." : highRiskSensors}</div>
          </div>
        </div>
      </div>

      {/* Main dashboard sections */}
      <div className="dashboard-grid">
        <div className="dashboard-section">
          <div className="section-header">
            <div>
              <h2>Live GIS Monitoring</h2>
              <p>Susceptibility raster and real node positions</p>
            </div>
            <Map size={20} />
          </div>

          <div className="map-placeholder">
            <Map size={40} />
            <strong>Live GIS Map</strong>
            <span>View physical gateway coordinates and susceptibility overlay on the GIS page.</span>
            <a href="/gis">Open Live GIS</a>
          </div>
        </div>

        <div className="dashboard-section">
          <div className="section-header">
            <div>
              <h2>Risk Summary</h2>
              <p>Highest-risk active sensor node</p>
            </div>
            <BrainCircuit size={20} />
          </div>

          {highestRiskSensor ? (
            <div className="risk-summary">
              <div className="risk-summary-row">
                <span>Location</span>
                <strong>{getSensorLocationName(highestRiskSensor)}</strong>
              </div>

              <div className="risk-summary-row">
                <span>Sensor ID</span>
                <strong>{highestRiskSensor.sensor_id}</strong>
              </div>

              <div className="risk-summary-row">
                <span>Risk Level</span>
                <strong
                  style={{
                    color:
                      highestRiskSensor.risk_level === "CRITICAL"
                        ? "#c0392b"
                        : highestRiskSensor.risk_level === "HIGH"
                        ? "#e67e22"
                        : highestRiskSensor.risk_level === "MEDIUM"
                        ? "#f1c40f"
                        : "#2e8b57",
                  }}
                >
                  {highestRiskSensor.risk_level}
                </strong>
              </div>

              <div className="risk-summary-row">
                <span>Risk Score</span>
                <strong>{highestRiskSensor.risk_score ?? 0} / 100</strong>
              </div>

              {highestRiskSensor.readings?.rain_detected !== undefined ? (
                <>
                  <div className="risk-summary-row">
                    <span>Rain Sensor</span>
                    <strong style={{ color: highestRiskSensor.readings.rain_detected ? "#c0392b" : "#23845a" }}>
                      {highestRiskSensor.readings.rain_detected ? "Detected" : "Not detected"}
                    </strong>
                  </div>

                  <div className="risk-summary-row">
                    <span>Soil Moisture</span>
                    <strong>
                      {highestRiskSensor.readings.soil_moisture != null
                        ? `${highestRiskSensor.readings.soil_moisture}%`
                        : "N/A"}
                    </strong>
                  </div>

                  <div className="risk-summary-row">
                    <span>Ground Tilt</span>
                    <strong>
                      {highestRiskSensor.readings.tilt != null
                        ? `${highestRiskSensor.readings.tilt}° (Δ ${highestRiskSensor.readings.tilt_change ?? 0}°)`
                        : "Unavailable"}
                    </strong>
                  </div>

                  <div className="risk-summary-row">
                    <span>Slope Motion</span>
                    <strong>
                      {highestRiskSensor.readings.motion_accel != null || highestRiskSensor.readings.motion_gyro != null
                        ? `Accel: ${highestRiskSensor.readings.motion_accel ?? 0} m/s² | Gyro: ${highestRiskSensor.readings.motion_gyro ?? 0}°/s`
                        : "Unavailable"}
                    </strong>
                  </div>
                </>
              ) : (
                <>
                  <div className="risk-summary-row">
                    <span>Rainfall</span>
                    <strong>{formatValue(highestRiskSensor.readings?.rainfall, " mm")}</strong>
                  </div>
                  <div className="risk-summary-row">
                    <span>Soil Moisture</span>
                    <strong>{formatValue(highestRiskSensor.readings?.soil_moisture, "%")}</strong>
                  </div>
                  <div className="risk-summary-row">
                    <span>Ground Tilt</span>
                    <strong>{formatValue(highestRiskSensor.readings?.tilt, "°")}</strong>
                  </div>
                </>
              )}

              {highestRiskSensor.contributing_factors && highestRiskSensor.contributing_factors.length > 0 && (
                <div style={{ marginTop: "12px", paddingTop: "10px", borderTop: "1px solid #edf1f0" }}>
                  <span style={{ fontSize: "11px", color: "#71817f", display: "block", marginBottom: "6px" }}>
                    Contributing Factors:
                  </span>
                  <ul style={{ margin: 0, paddingLeft: "18px", fontSize: "11px", color: "#173b3a" }}>
                    {highestRiskSensor.contributing_factors.map((f, i) => (
                      <li key={i} style={{ marginBottom: "3px" }}>
                        {f}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="empty-state">
              <CheckCircle2 size={24} />
              <span>No sensor data available</span>
            </div>
          )}
        </div>
      </div>

      {/* Weather API monitoring */}
      <div className="dashboard-section weather-section" style={{ marginTop: "20px" }}>
        <div className="section-header">
          <div>
            <h2>Weather Monitoring by Location</h2>
            <p>Regional precipitation and pressure readings from Open-Meteo</p>
          </div>
          <CloudRain size={20} />
        </div>

        {weatherLoading ? (
          <div className="alert-empty">Loading weather data...</div>
        ) : weatherError ? (
          <div className="alert-empty">{weatherError}</div>
        ) : weatherLocations.length === 0 ? (
          <div className="alert-empty">No weather locations were returned by the backend.</div>
        ) : (
          <div className="weather-location-grid">
            {weatherLocations.map((location) => {
              const weather = location.weather;
              const readings = weather?.readings;
              const weatherRisk = location.weather_risk;

              return (
                <div className="weather-location-card" key={location.location_id}>
                  <div className="weather-location-heading">
                    <div>
                      <h3>
                        <MapPin
                          size={16}
                          style={{
                            display: "inline",
                            verticalAlign: "middle",
                            marginRight: "5px",
                          }}
                        />
                        {location.name}
                      </h3>
                      <span className="weather-location-id">{location.location_id} · Weather API</span>
                    </div>
                    <CloudRain size={21} />
                  </div>

                  {weather?.available && readings ? (
                    <>
                      <div className="weather-primary-value">
                        <Thermometer size={20} />
                        <strong>{formatValue(readings.temperature_c, " °C")}</strong>
                        <span>Temperature</span>
                      </div>

                      <div className="weather-readings">
                        <div>
                          <Droplets size={16} />
                          <span>Humidity</span>
                          <strong>{formatValue(readings.humidity_percent, "%")}</strong>
                        </div>

                        <div>
                          <CloudRain size={16} />
                          <span>Rain</span>
                          <strong>{formatValue(readings.rain_mm, " mm")}</strong>
                        </div>

                        <div>
                          <CloudRain size={16} />
                          <span>Precipitation</span>
                          <strong>{formatValue(readings.precipitation_mm, " mm")}</strong>
                        </div>

                        <div>
                          <Gauge size={16} />
                          <span>Surface Pressure</span>
                          <strong>{formatValue(readings.pressure_hpa, " hPa")}</strong>
                        </div>
                      </div>

                      <div className="weather-source">
                        <span>Source: {weather.source || "Weather API"}</span>
                        <span>
                          <Clock
                            size={13}
                            style={{
                              display: "inline",
                              verticalAlign: "middle",
                              marginRight: "4px",
                            }}
                          />
                          {formatObservedTime(weather.observed_at)}
                        </span>
                      </div>
                    </>
                  ) : (
                    <div className="weather-unavailable">Weather data is currently unavailable for this location.</div>
                  )}

                  <div className="weather-prediction-note">
                    <div className="weather-screening-heading">
                      <strong>Weather-Based Screening</strong>
                      <span className="weather-screening-status">
                        {weatherRisk?.status === "unassessed"
                          ? "UNASSESSED"
                          : weatherRisk?.category || "UNAVAILABLE"}
                      </span>
                    </div>

                    <div className="weather-risk-metrics">
                      <div className="weather-risk-metric">
                        <CloudRain size={16} aria-hidden="true" />
                        <span>Current rain</span>
                        <strong>{formatValue(readings?.rain_mm, " mm")}</strong>
                      </div>
                      <div className="weather-risk-metric">
                        <Droplets size={16} aria-hidden="true" />
                        <span>Precipitation</span>
                        <strong>{formatValue(readings?.precipitation_mm, " mm")}</strong>
                      </div>
                    </div>

                    <span className="weather-risk-observed">
                      Observation time: {formatObservedTime(weatherRisk?.observed_at || weather?.observed_at)}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Sensor overview */}
      <div className="dashboard-section" style={{ marginTop: "20px" }}>
        <div className="section-header">
          <div>
            <h2>Sensor Overview</h2>
            <p>Real-time physical gateway readings and risk levels</p>
          </div>
          <RadioTower size={20} />
        </div>

        <div className="sensor-overview">
          {sensors.map((sensor) => (
            <div className="sensor-overview-item" key={sensor.sensor_id}>
              <div>
                <strong>{getSensorLocationName(sensor)}</strong>
                <span>
                  {sensor.sensor_id} · Risk score: {sensor.risk_score ?? 0}
                </span>
              </div>

              <span className={`overview-risk ${(sensor.risk_level || "LOW").toLowerCase()}`}>
                {sensor.risk_level || "LOW"}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
````

---

## `frontend/src/pages/Sensors.jsx`

````jsx
import { useEffect, useState } from "react";
import {
  RadioTower,
  Droplets,
  Activity,
  ShieldAlert,
  Compass,
  Cpu,
  Clock,
  WifiOff,
  AlertCircle,
  CloudRain,
  MapPin,
} from "lucide-react";

function formatTimestamp(isoStr) {
  if (!isoStr) return "N/A";
  try {
    const d = new Date(isoStr);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  } catch {
    return isoStr;
  }
}

function DataSourceBadge({ source }) {
  const norm = (source || "SIMULATED").toUpperCase();
  let cls = "simulated";
  let label = "SIMULATED";

  if (norm === "LIVE_CSV" || norm === "LIVE") {
    cls = "live";
    label = "LIVE CSV";
  } else if (norm === "STALE") {
    cls = "stale";
    label = "STALE DATA";
  } else if (norm === "NO_DATA") {
    cls = "nodata";
    label = "NO DATA";
  }

  return <span className={`data-source-badge ${cls}`}>{label}</span>;
}

function Sensors() {
  const [sensors, setSensors] = useState([]);
  const [dataSource, setDataSource] = useState("SIMULATED");
  const [packetLoss, setPacketLoss] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;

    const fetchSensorData = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/risk");
        if (!response.ok) {
          throw new Error(`Server returned HTTP ${response.status}`);
        }
        const data = await response.json();
        if (!active) return;

        setSensors(data.sensors || []);
        setDataSource(data.data_source || "SIMULATED");
        setPacketLoss(data.packet_loss_count ?? 0);
        setError(null);
        setLoading(false);
      } catch (err) {
        if (!active) return;
        console.error("Sensor data loading error:", err);
        setError("Unable to connect to backend server. Make sure FastAPI is running.");
        setLoading(false);
      }
    };

    fetchSensorData();
    const interval = setInterval(fetchSensorData, 3000);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="page">
      <div className="page-heading">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "10px" }}>
          <div>
            <h1>Sensors</h1>
            <p>Real-time physical gateway telemetry and landslide risk factors</p>
          </div>
          <div>
            <DataSourceBadge source={dataSource} />
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="dashboard-cards">
        <div className="stat-card">
          <div className="stat-icon">
            <RadioTower size={20} />
          </div>
          <div>
            <span className="stat-label">Connected Sensors</span>
            <div className="stat-value">{loading ? "..." : sensors.length}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <ShieldAlert size={20} />
          </div>
          <div>
            <span className="stat-label">Telemetry Source</span>
            <div className="stat-value" style={{ fontSize: "16px", marginTop: "4px" }}>
              {dataSource === "LIVE_CSV" ? "Live Gateway CSV" : dataSource === "STALE" ? "Stale (>10s)" : dataSource}
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <WifiOff size={20} />
          </div>
          <div>
            <span className="stat-label">Sequence Packet Loss</span>
            <div className="stat-value">{packetLoss} pkts</div>
          </div>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="history-error" style={{ marginBottom: "20px", display: "flex", alignItems: "center", gap: "10px" }}>
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* Loading state */}
      {loading ? (
        <div className="dashboard-section">
          <p>Loading gateway sensor data...</p>
        </div>
      ) : sensors.length === 0 ? (
        <div className="dashboard-section">
          <div className="empty-state">
            <RadioTower size={36} />
            <strong>No sensor data available</strong>
            <span>Waiting for gateway or test CSV readings to arrive.</span>
          </div>
        </div>
      ) : (
        <div className="sensor-grid">
          {sensors.map((sensor) => {
            const readings = sensor.readings || {};
            const isCalibrated = sensor.calibrated ?? readings.calibrated ?? true;
            const hasGps = sensor.gps_valid && sensor.location?.latitude != null;
            const mpuValid = sensor.mpu_valid ?? readings.mpu_available ?? false;

            return (
              <div className="sensor-card" key={sensor.sensor_id}>
                {/* Header */}
                <div className="sensor-card-header">
                  <div>
                    <h3>{sensor.sensor_id}</h3>
                    <span>{sensor.data_source === "STALE" ? "Stale Data" : "Active Node"}</span>
                  </div>
                  <div
                    className="sensor-status-dot"
                    style={{
                      background: sensor.data_source === "STALE" ? "#e67e22" : "#2e9b6f",
                    }}
                  />
                </div>

                {/* Risk Overview */}
                <div className="sensor-risk">
                  <div>
                    <span>Current Risk</span>
                    <strong
                      style={{
                        color:
                          sensor.risk_level === "CRITICAL"
                            ? "#c0392b"
                            : sensor.risk_level === "HIGH"
                            ? "#e67e22"
                            : sensor.risk_level === "MEDIUM"
                            ? "#f1c40f"
                            : "#2e8b57",
                      }}
                    >
                      {sensor.risk_level || "LOW"}
                    </strong>
                  </div>
                  <div className="risk-score">{sensor.risk_score ?? 0} / 100</div>
                </div>

                {/* Location & GPS */}
                <div className="sensor-location" style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  <MapPin size={14} />
                  <span>
                    GPS:{" "}
                    {hasGps
                      ? `${sensor.location.latitude.toFixed(4)}, ${sensor.location.longitude.toFixed(4)}`
                      : "No GPS fix"}
                  </span>
                </div>

                {/* Real Physical Sensor Readings */}
                <div className="sensor-readings">
                  {/* Soil Moisture */}
                  <div className="sensor-reading">
                    <Droplets size={18} />
                    <div style={{ width: "100%" }}>
                      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                        <span>Soil Moisture</span>
                        {!isCalibrated && (
                          <span className="calibration-notice">estimate - calibration pending</span>
                        )}
                      </div>
                      <strong>
                        {readings.soil_moisture != null ? `${readings.soil_moisture}%` : "N/A"}
                        <span style={{ fontSize: "10px", color: "#819493", marginLeft: "6px", fontWeight: "normal" }}>
                          (ADC: {readings.soil_raw ?? "—"})
                        </span>
                      </strong>
                    </div>
                  </div>

                  {/* Tilt Angle & Change */}
                  <div className="sensor-reading">
                    <Compass size={18} />
                    <div>
                      <span>Tilt (Abs / Change)</span>
                      <strong>
                        {readings.tilt != null
                          ? `${readings.tilt}° (Δ ${readings.tilt_change ?? 0}°, base: ${readings.tilt_baseline ?? 0}°)`
                          : "Unavailable (MPU invalid)"}
                      </strong>
                    </div>
                  </div>

                  {/* Motion (Accel dev + Gyro mag) */}
                  <div className="sensor-reading">
                    <Activity size={18} />
                    <div>
                      <span>Slope Motion</span>
                      <strong>
                        {readings.motion_accel != null || readings.motion_gyro != null
                          ? `Accel: ${readings.motion_accel ?? 0} m/s² | Gyro: ${readings.motion_gyro ?? 0}°/s`
                          : "Unavailable (MPU invalid)"}
                      </strong>
                    </div>
                  </div>

                  {/* Rain Detection */}
                  <div className="sensor-reading">
                    <CloudRain size={18} />
                    <div>
                      <span>Precipitation Sensor</span>
                      <strong style={{ color: readings.rain_detected ? "#c0392b" : "#23845a" }}>
                        {readings.rain_detected ? "Detected" : "Not detected"}
                      </strong>
                    </div>
                  </div>

                  {/* MPU Status */}
                  <div className="sensor-reading">
                    <Cpu size={18} />
                    <div>
                      <span>MPU6050 Status</span>
                      <strong style={{ color: mpuValid ? "#23845a" : "#a66b00" }}>
                        {mpuValid ? "Valid Hardware" : "Test Data / Invalid"}
                      </strong>
                    </div>
                  </div>

                  {/* Last Updated */}
                  <div className="sensor-reading">
                    <Clock size={18} />
                    <div>
                      <span>Last Telemetry</span>
                      <strong>
                        {formatTimestamp(sensor.last_updated)}
                        {sensor.age_seconds != null && (
                          <span style={{ fontSize: "10px", color: "#819493", marginLeft: "4px" }}>
                            ({sensor.age_seconds}s ago)
                          </span>
                        )}
                      </strong>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default Sensors;
````

---

## `frontend/src/pages/Alerts.jsx`

````jsx
import { useEffect, useState } from "react";
import {
  BellRing,
  ShieldAlert,
  TriangleAlert,
  CheckCircle2,
  RadioTower,
  MapPin,
  Clock,
  AlertCircle,
} from "lucide-react";

function DataSourceBadge({ source }) {
  const norm = (source || "SIMULATED").toUpperCase();
  let cls = "simulated";
  let label = "SIMULATED";

  if (norm === "LIVE_CSV" || norm === "LIVE") {
    cls = "live";
    label = "LIVE CSV";
  } else if (norm === "STALE") {
    cls = "stale";
    label = "STALE DATA";
  } else if (norm === "NO_DATA") {
    cls = "nodata";
    label = "NO DATA";
  }

  return <span className={`data-source-badge ${cls}`}>{label}</span>;
}

function Alerts() {
  const [sensors, setSensors] = useState([]);
  const [dataSource, setDataSource] = useState("SIMULATED");
  const [isStale, setIsStale] = useState(false);
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    const fetchData = async () => {
      try {
        const [riskResponse, locationResponse] = await Promise.all([
          fetch("http://127.0.0.1:8000/api/risk"),
          fetch("http://127.0.0.1:8000/api/locations"),
        ]);

        if (!riskResponse.ok || !locationResponse.ok) {
          throw new Error("Failed to load risk or location data");
        }

        const riskData = await riskResponse.json();
        const locationData = await locationResponse.json();

        if (active) {
          setSensors(riskData.sensors || []);
          setDataSource(riskData.data_source || "SIMULATED");
          setIsStale(riskData.is_stale || riskData.data_source === "STALE");
          setLocations(locationData.locations || []);
          setError("");
          setLoading(false);
        }
      } catch (err) {
        if (active) {
          console.error("Alert loading error:", err);
          setError("Unable to load alerts. Check that the backend server is running.");
          setLoading(false);
        }
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 3000);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  const getLocationName = (sensor) => {
    if (sensor.location?.latitude != null && sensor.location?.gps_valid) {
      return `GPS: ${sensor.location.latitude.toFixed(4)}, ${sensor.location.longitude.toFixed(4)}`;
    }
    const matchingLocation = locations.find(
      (location) => location.sensor_id === sensor.sensor_id
    );
    if (matchingLocation?.name) {
      return matchingLocation.name;
    }
    return sensor.sensor_id === "NODE-01" ? "Field Node (No GPS fix)" : `Node ${sensor.sensor_id}`;
  };

  const highRiskSensors = sensors.filter((sensor) => sensor.risk_level === "HIGH");
  const criticalSensors = sensors.filter((sensor) => sensor.risk_level === "CRITICAL");
  const totalAlerts = highRiskSensors.length + criticalSensors.length;
  const alertSensors = [...criticalSensors, ...highRiskSensors];

  return (
    <div className="page">
      <div className="page-heading">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "10px" }}>
          <div>
            <h1>Alerts</h1>
            <p>Active landslide early warnings triggered by physical sensor thresholds</p>
          </div>
          <div>
            <DataSourceBadge source={dataSource} />
          </div>
        </div>
      </div>

      {/* Staleness Notice Banner */}
      {isStale && (
        <div className="stale-banner">
          <Clock size={18} />
          <span>
            <strong>Notice: Telemetry data is STALE.</strong> No new packets received for over 10 seconds.
            Alerts represent the last recorded condition from the gateway CSV.
          </span>
        </div>
      )}

      {/* Backend connection error */}
      {error && (
        <div className="history-error" style={{ marginBottom: "20px", display: "flex", alignItems: "center", gap: "10px" }}>
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      <div className="dashboard-cards">
        <div className="stat-card">
          <div className="stat-icon">
            <BellRing size={20} />
          </div>
          <div>
            <span className="stat-label">Active Alerts</span>
            <div className="stat-value">{loading ? "..." : totalAlerts}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <ShieldAlert size={20} />
          </div>
          <div>
            <span className="stat-label">Critical</span>
            <div className="stat-value">{loading ? "..." : criticalSensors.length}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <TriangleAlert size={20} />
          </div>
          <div>
            <span className="stat-label">High Risk</span>
            <div className="stat-value">{loading ? "..." : highRiskSensors.length}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <RadioTower size={20} />
          </div>
          <div>
            <span className="stat-label">Sensors Monitored</span>
            <div className="stat-value">{loading ? "..." : sensors.length}</div>
          </div>
        </div>
      </div>

      <div className="dashboard-section">
        <div className="section-header">
          <div>
            <h2>Current Alerts</h2>
            <p>Warnings generated from real sensor scoring: Soil Moisture, Tilt Change, Motion, Rain</p>
          </div>
          <BellRing size={20} />
        </div>

        {loading ? (
          <div className="alert-empty">Loading alert data...</div>
        ) : error ? (
          <div className="alert-empty">{error}</div>
        ) : totalAlerts === 0 ? (
          <div className="alert-empty">
            <CheckCircle2 size={28} />
            <strong>No Active Alerts</strong>
            <span>All monitored slope sensors are operating within safe baseline limits (Risk score &lt; 50).</span>
          </div>
        ) : (
          <div className="alert-list">
            {alertSensors.map((sensor) => {
              const isCritical = sensor.risk_level === "CRITICAL";
              const placeName = getLocationName(sensor);
              const readings = sensor.readings || {};

              return (
                <div className={`alert-item ${sensor.risk_level.toLowerCase()}`} key={sensor.sensor_id}>
                  <div className="alert-icon">
                    {isCritical ? <ShieldAlert size={22} /> : <TriangleAlert size={22} />}
                  </div>

                  <div className="alert-content">
                    <div className="alert-title-row">
                      <strong>
                        {isCritical ? "Critical Landslide Risk Condition" : "High Landslide Risk Warning"}
                      </strong>
                      <span className="alert-time">
                        {sensor.data_source === "STALE" ? "Stale Data" : "Real-time Gateway"}
                      </span>
                    </div>

                    <p style={{ marginTop: "4px" }}>
                      <MapPin
                        size={15}
                        style={{
                          display: "inline",
                          verticalAlign: "middle",
                          marginRight: "5px",
                        }}
                      />
                      <strong>{placeName}</strong>
                    </p>

                    <p>
                      Sensor ID: <strong>{sensor.sensor_id}</strong> is reporting a{" "}
                      <strong>{sensor.risk_level}</strong> risk condition (Risk Score:{" "}
                      <strong>{sensor.risk_score}/100</strong>).
                    </p>

                    {/* Contributing factors */}
                    {sensor.contributing_factors && sensor.contributing_factors.length > 0 && (
                      <div style={{ margin: "8px 0", padding: "8px 12px", background: "rgba(0,0,0,0.03)", borderRadius: "6px" }}>
                        <strong style={{ fontSize: "11px", color: "#173b3a" }}>Contributing Risk Factors:</strong>
                        <ul style={{ margin: "4px 0 0 16px", padding: 0, fontSize: "11px" }}>
                          {sensor.contributing_factors.map((factor, idx) => (
                            <li key={idx} style={{ marginBottom: "2px" }}>
                              {factor}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className="alert-details">
                      <span>
                        Risk Score: <strong>{sensor.risk_score}/100</strong>
                      </span>

                      {readings.rain_detected !== undefined ? (
                        <>
                          <span>
                            Rain Sensor:{" "}
                            <strong style={{ color: readings.rain_detected ? "#c0392b" : "#23845a" }}>
                              {readings.rain_detected ? "Detected" : "Not detected"}
                            </strong>
                          </span>

                          <span>
                            Soil Moisture:{" "}
                            <strong>{readings.soil_moisture != null ? `${readings.soil_moisture}%` : "N/A"}</strong>
                          </span>

                          <span>
                            Tilt Change:{" "}
                            <strong>{readings.tilt_change != null ? `${readings.tilt_change}°` : "N/A"}</strong>
                          </span>

                          <span>
                            Motion Gyro:{" "}
                            <strong>{readings.motion_gyro != null ? `${readings.motion_gyro}°/s` : "N/A"}</strong>
                          </span>
                        </>
                      ) : (
                        <>
                          <span>
                            Rainfall: <strong>{readings.rainfall ?? "N/A"} mm</strong>
                          </span>
                          <span>
                            Soil Moisture: <strong>{readings.soil_moisture ?? "N/A"}%</strong>
                          </span>
                          <span>
                            Tilt: <strong>{readings.tilt ?? "N/A"}°</strong>
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export default Alerts;
````

---

## `frontend/src/pages/History.jsx`

````jsx
import { useEffect, useMemo, useState } from "react";
import {
  History as HistoryIcon,
  RefreshCw,
  Trash2,
  AlertTriangle,
  AlertCircle,
} from "lucide-react";

const API_URL = "http://127.0.0.1:8000/api/risk";
const STORAGE_KEY = "landslide-risk-history";

function History() {
  const [records, setRecords] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const [filter, setFilter] = useState("ALL");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    const fetchHistory = async () => {
      try {
        const response = await fetch(API_URL);
        if (!response.ok) {
          throw new Error("Unable to fetch risk data.");
        }

        const data = await response.json();
        const sensors = data.sensors || [];

        if (!active) return;

        const timestamp = new Date().toISOString();

        const newRecords = sensors.map((sensor) => ({
          id: `${timestamp}-${sensor.sensor_id}`,
          timestamp,
          sensor_id: sensor.sensor_id,
          location: sensor.location || "Unknown location",
          risk_level: sensor.risk_level || "UNKNOWN",
          risk_score: sensor.risk_score ?? null,
          readings: sensor.readings || {},
          data_source: sensor.data_source || data.data_source || "SIMULATED",
        }));

        setRecords((previous) => {
          // Avoid appending exact duplicates if timestamp hasn't changed or sensor is identical
          const updated = [...newRecords, ...previous].slice(0, 500);

          try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
          } catch (storageError) {
            console.error("Could not save history:", storageError);
          }

          return updated;
        });

        setError("");
      } catch (err) {
        if (active) {
          setError("Could not load history. Check that backend is running.");
          console.error("History loading error:", err);
        }
      } finally {
        if (active) setLoading(false);
      }
    };

    fetchHistory();
    const interval = setInterval(fetchHistory, 3000);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  const filteredRecords = useMemo(() => {
    if (filter === "ALL") return records;
    return records.filter(
      (record) => (record.risk_level || "").toUpperCase() === filter
    );
  }, [records, filter]);

  const formatDate = (value) => {
    if (!value) return "—";
    try {
      return new Date(value).toLocaleString();
    } catch {
      return value;
    }
  };

  const clearHistory = () => {
    const confirmed = window.confirm("Are you sure you want to clear all saved history?");
    if (!confirmed) return;
    localStorage.removeItem(STORAGE_KEY);
    setRecords([]);
  };

  const riskClass = (level) => {
    const value = (level || "UNKNOWN").toLowerCase();
    if (value.includes("critical")) return "critical";
    if (value.includes("high")) return "high";
    if (value.includes("medium")) return "medium";
    if (value.includes("low")) return "low";
    return "unknown";
  };

  return (
    <div className="page">
      <div className="page-heading">
        <h1>Risk History</h1>
        <p>Historical telemetry records and landslide risk calculations</p>
      </div>

      <div className="dashboard-cards">
        <div className="stat-card">
          <div className="stat-icon">
            <HistoryIcon size={22} />
          </div>
          <div>
            <span className="stat-label">Total Records</span>
            <h2>{records.length}</h2>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <AlertTriangle size={22} />
          </div>
          <div>
            <span className="stat-label">High-Risk Records</span>
            <h2>
              {
                records.filter((record) =>
                  (record.risk_level || "").toUpperCase().includes("HIGH") ||
                  (record.risk_level || "").toUpperCase().includes("CRITICAL")
                ).length
              }
            </h2>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <RefreshCw size={22} />
          </div>
          <div>
            <span className="stat-label">Polling Rate</span>
            <h2>3 seconds</h2>
          </div>
        </div>
      </div>

      <div className="history-panel">
        <div className="history-toolbar">
          <div>
            <h2>Recorded Events</h2>
            <p>Newest readings appear first.</p>
          </div>

          <div className="history-actions">
            <select
              value={filter}
              onChange={(event) => setFilter(event.target.value)}
              aria-label="Filter by risk level"
            >
              <option value="ALL">All Risk Levels</option>
              <option value="CRITICAL">Critical Risk</option>
              <option value="HIGH">High Risk</option>
              <option value="MEDIUM">Medium Risk</option>
              <option value="LOW">Low Risk</option>
            </select>

            <button type="button" onClick={clearHistory} disabled={records.length === 0}>
              <Trash2 size={16} />
              Clear History
            </button>
          </div>
        </div>

        {error && (
          <div className="history-error" style={{ marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        {loading && records.length === 0 && (
          <p className="history-message">Loading risk history...</p>
        )}

        {!loading && records.length === 0 && !error && (
          <p className="history-message">
            No history recorded yet. Records will appear when sensor-risk data is received.
          </p>
        )}

        {records.length > 0 && filteredRecords.length === 0 && (
          <p className="history-message">No records found for this risk level.</p>
        )}

        {filteredRecords.length > 0 && (
          <div className="history-table-wrapper">
            <table className="history-table">
              <thead>
                <tr>
                  <th>Recorded At</th>
                  <th>Sensor ID</th>
                  <th>Risk Score</th>
                  <th>Risk Tier</th>
                  <th>Soil %</th>
                  <th>Tilt Change</th>
                  <th>Motion</th>
                  <th>Rain</th>
                </tr>
              </thead>

              <tbody>
                {filteredRecords.map((record) => {
                  const readings = record.readings || {};
                  const soilPct = readings.soil_moisture != null ? `${readings.soil_moisture}%` : "—";
                  const tiltChange =
                    readings.tilt_change != null
                      ? `${readings.tilt_change}°`
                      : readings.tilt != null
                      ? `${readings.tilt}°`
                      : "—";
                  const motionStr =
                    readings.motion_gyro != null
                      ? `${readings.motion_gyro}°/s`
                      : readings.motion_accel != null
                      ? `${readings.motion_accel} m/s²`
                      : "—";
                  const rainStr =
                    readings.rain_detected !== undefined
                      ? readings.rain_detected
                        ? "Detected"
                        : "None"
                      : readings.rainfall != null
                      ? `${readings.rainfall} mm`
                      : "—";

                  return (
                    <tr key={record.id}>
                      <td>{formatDate(record.timestamp)}</td>
                      <td>{record.sensor_id || "NODE-01"}</td>
                      <td>
                        <strong>{record.risk_score ?? "N/A"}</strong>
                      </td>
                      <td>
                        <span className={`history-risk ${riskClass(record.risk_level)}`}>
                          {record.risk_level || "UNKNOWN"}
                        </span>
                      </td>
                      <td>{soilPct}</td>
                      <td>{tiltChange}</td>
                      <td>{motionStr}</td>
                      <td>
                        <span
                          style={{
                            fontWeight: rainStr === "Detected" ? "bold" : "normal",
                            color: rainStr === "Detected" ? "#c0392b" : "inherit",
                          }}
                        >
                          {rainStr}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default History;
````

---

## `frontend/src/pages/GIS.jsx`

````jsx
import { useEffect, useState } from "react";

import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Circle,
  CircleMarker,
  Tooltip,
  useMap
} from "react-leaflet";

import {
  Map as MapIcon,
  Layers,
  Navigation,
} from "lucide-react";

import L from "leaflet";
import parseGeoraster from "georaster";
import GeoRasterLayer from "georaster-layer-for-leaflet";

import "leaflet/dist/leaflet.css";


function SusceptibilityLayer({ onLoaded }) {

  const map = useMap();

  const [_loading, setLoading] = useState(true);


  useEffect(() => {

    let rasterLayer = null;


    const loadRaster = async () => {

      try {

        const response = await fetch(
          "/rasters/Landslide_Susceptibility_Probability.tif"
        );


        if (!response.ok) {

          throw new Error(
            "Could not load susceptibility raster"
          );

        }


        const arrayBuffer =
          await response.arrayBuffer();


        const georaster =
          await parseGeoraster(arrayBuffer);


        console.log(
          "Susceptibility GeoRaster:",
          georaster
        );


        rasterLayer = new GeoRasterLayer({

          georaster: georaster,

          opacity: 0.65,

          resolution: 64,


          pixelValuesToColorFn: (values) => {

            const value = values[0];


            if (
              value === null ||
              value === undefined ||
              value === -9999
            ) {

              return null;

            }


            if (value < 0.2) {

              return "#2e8b57";

            }


            if (value < 0.4) {

              return "#9acd32";

            }


            if (value < 0.6) {

              return "#f1c40f";

            }


            if (value < 0.8) {

              return "#e67e22";

            }


            return "#c0392b";

          },

        });


        rasterLayer.addTo(map);


        map.fitBounds(
          rasterLayer.getBounds()
        );


        setLoading(false);


        if (onLoaded) {

          onLoaded(true);

        }

      } catch (error) {

        console.error(
          "Raster loading error:",
          error
        );


        setLoading(false);


        if (onLoaded) {

          onLoaded(false);

        }

      }

    };


    loadRaster();


    return () => {

      if (rasterLayer) {

        map.removeLayer(rasterLayer);

      }

    };

  }, [map, onLoaded]);


  return null;

}


/*
  Choose marker color based on
  current real-time risk.
*/

function getRiskColor(riskLevel) {

  switch (riskLevel) {

    case "LOW":
      return "#2e8b57";

    case "MEDIUM":
      return "#f1c40f";

    case "HIGH":
      return "#e67e22";

    case "CRITICAL":
      return "#c0392b";

    default:
      return "#2e7773";

  }

}


/*
  GIS Page
*/

function GIS() {

  const nilgirisCenter = [
    11.4102,
    76.6950,
  ];


  const [rasterLoaded, setRasterLoaded] =
    useState(false);


  const [sensors, setSensors] =
    useState([]);
  const [weatherLocations, setWeatherLocations] = useState([]);

  /*
    Load sensor risk data
    immediately and every 5 seconds.
  */

  useEffect(() => {


    const fetchRiskData = () => {

      fetch(
        "http://127.0.0.1:8000/api/risk"
      )

        .then((response) => {

          if (!response.ok) {

            throw new Error(
              "Could not load risk data"
            );

          }

          return response.json();

        })

        .then((data) => {

          setSensors(data.sensors);

        })

        .catch((error) => {

          console.error(
            "Risk data loading error:",
            error
          );

        });

    };


    // First request
    fetchRiskData();

    // Refresh every 3 seconds
    const interval = setInterval(
      fetchRiskData,
      3000
    );

    return () => {
      clearInterval(interval);
    };
  }, []);


  /*
    Load weather data for locations without physical sensors.
    Refresh every 60 seconds.
  */

  useEffect(() => {
    const fetchWeatherLocations = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/weather");

        if (!response.ok) {
          throw new Error("Could not load weather locations");
        }

        const data = await response.json();
        setWeatherLocations(data.locations || []);
      } catch (error) {
        console.error("Weather locations loading error:", error);
      }
    };

    fetchWeatherLocations();

    const interval = setInterval(fetchWeatherLocations, 60000);
    return () => clearInterval(interval);
  }, []);


  /*
    Fix Leaflet marker icons.
  */

  useEffect(() => {

    delete L.Icon.Default.prototype._getIconUrl;


    L.Icon.Default.mergeOptions({

      iconRetinaUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",

      iconUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",

      shadowUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",

    });

  }, []);


  return (

    <div className="page">


      {/* Page heading */}

      <div className="page-heading">

        <h1>Live GIS</h1>

        <p>
          Real-time landslide susceptibility
          and sensor risk monitoring
        </p>

      </div>


      {/* Toolbar */}

      <div className="gis-toolbar">

        <div className="gis-info">

          <div className="stat-icon">

            <MapIcon size={19} />

          </div>


          <div>

            <strong>
              Nilgiris District
            </strong>

            <span>
              Susceptibility & Sensor Risk Map
            </span>

          </div>

        </div>


        <div className="gis-tools">

          <div className="gis-tool">

            <Layers size={16} />

            <span>
              Susceptibility
            </span>

          </div>


          <div className="gis-tool" style={{
            background: sensors.some(s => s.gps_valid && s.location?.latitude != null) ? "#e4f4eb" : "#fef3c7",
          }}>
            <Navigation size={16} color={sensors.some(s => s.gps_valid && s.location?.latitude != null) ? "#23845a" : "#b45309"} />
            <span style={{
              color: sensors.some(s => s.gps_valid && s.location?.latitude != null) ? "#23845a" : "#b45309",
              fontWeight: 600,
            }}>
              {sensors.some(s => s.gps_valid && s.location?.latitude != null) ? "Node GPS Active" : "No GPS fix"}
            </span>
          </div>

          <div className="gis-tool">
            <span
              style={{
                display: "inline-block",
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                background: "#60a5fa",
                marginRight: "6px",
              }}
            />
            <span>Weather API</span>
          </div>

        </div>

      </div>


      {/* Map */}

      <div className="gis-map-card">

        <MapContainer

          center={nilgirisCenter}

          zoom={10}

          scrollWheelZoom={true}

          className="gis-map"

        >


          {/* OpenStreetMap */}

          <TileLayer

            attribution="&copy; OpenStreetMap contributors"

            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"

          />


          {/* ML susceptibility raster */}

          <SusceptibilityLayer
            onLoaded={setRasterLoaded}
          />


          {/* Nilgiris marker */}

          <Marker
            position={nilgirisCenter}
          >

            <Popup>

              <strong>
                Nilgiris District
              </strong>

              <br />

              Landslide monitoring area

            </Popup>

          </Marker>


          {/* Monitoring area */}

          <Circle

            center={nilgirisCenter}

            radius={15000}

            pathOptions={{

              color: "#2e7773",

              fillOpacity: 0,

            }}

          />


          {/* Live sensor risk markers */}
          {sensors.map((sensor) => {
            const hasGps = sensor.gps_valid && sensor.location?.latitude != null && sensor.location?.longitude != null;
            if (!hasGps) {
              // Only plot marker if gps_valid is true. Otherwise do not draw fake marker!
              return null;
            }

            const riskColor = getRiskColor(sensor.risk_level);
            const readings = sensor.readings || {};

            return (
              <CircleMarker
                key={sensor.sensor_id}
                center={[
                  sensor.location.latitude,
                  sensor.location.longitude,
                ]}
                radius={12}
                pathOptions={{
                  color: "#ffffff",
                  weight: 2,
                  fillColor: riskColor,
                  fillOpacity: 0.95,
                }}
              >
                <Popup>
                  <div style={{ minWidth: "190px" }}>
                    <strong style={{ fontSize: "14px" }}>{sensor.sensor_id}</strong>
                    <br />
                    <strong style={{ color: riskColor, fontSize: "13px" }}>
                      Risk Level: {sensor.risk_level || "LOW"}
                    </strong>
                    <br />
                    Risk Score: <strong>{sensor.risk_score ?? 0} / 100</strong>
                    <br />
                    <span style={{ fontSize: "11px", color: "#666" }}>
                      GPS: {sensor.location.latitude.toFixed(4)}, {sensor.location.longitude.toFixed(4)}
                    </span>
                    <hr style={{ margin: "6px 0", borderColor: "#eee" }} />
                    {readings.rain_detected !== undefined ? (
                      <div style={{ fontSize: "12px", lineHeight: "1.4" }}>
                        <div>Rain Sensor: <strong style={{ color: readings.rain_detected ? "#c0392b" : "#23845a" }}>{readings.rain_detected ? "Detected" : "Not detected"}</strong></div>
                        <div>Soil Moisture: <strong>{readings.soil_moisture != null ? `${readings.soil_moisture}%` : "—"}</strong></div>
                        <div>Tilt Angle: <strong>{readings.tilt != null ? `${readings.tilt}° (Δ ${readings.tilt_change ?? 0}°)` : "—"}</strong></div>
                        <div>Motion Gyro: <strong>{readings.motion_gyro != null ? `${readings.motion_gyro}°/s` : "—"}</strong></div>
                      </div>
                    ) : (
                      <div style={{ fontSize: "12px", lineHeight: "1.4" }}>
                        <div>Rainfall: <strong>{readings.rainfall ?? "—"} mm</strong></div>
                        <div>Soil Moisture: <strong>{readings.soil_moisture ?? "—"}%</strong></div>
                        <div>Tilt: <strong>{readings.tilt ?? "—"}°</strong></div>
                      </div>
                    )}
                    {sensor.contributing_factors && sensor.contributing_factors.length > 0 && (
                      <div style={{ marginTop: "6px", fontSize: "10px", color: "#444" }}>
                        <strong>Risk Factors:</strong>
                        <ul style={{ margin: "2px 0 0 12px", padding: 0 }}>
                          {sensor.contributing_factors.map((factor, idx) => (
                            <li key={idx}>{factor}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </Popup>
              </CircleMarker>
            );
          })}


          {/* Weather API locations without physical sensors */}
          {weatherLocations.map((location) => (
            <CircleMarker
              key={location.location_id}
              center={[location.latitude, location.longitude]}
              radius={8}
              pathOptions={{
                color: "#2563eb",
                fillColor: "#60a5fa",
                fillOpacity: 0.9,
                weight: 2,
              }}
            >
              <Tooltip direction="top">
                Weather-monitored area
              </Tooltip>

              <Popup>
                <div>
                  <strong>{location.name}</strong>
                  <br />
                  <span>Monitoring type: Weather API</span>
                  <br />
                  <span>Location ID: {location.location_id}</span>

                  {location.weather?.available ? (
                    <>
                      <hr />
                      <div>
                        <strong>Current weather</strong>
                      </div>
                      <div>
                        Temperature: {location.weather.readings?.temperature_c ?? "N/A"} °C
                      </div>
                      <div>
                        Humidity: {location.weather.readings?.humidity_percent ?? "N/A"}%
                      </div>
                      <div>
                        Rain: {location.weather.readings?.rain_mm ?? "N/A"} mm
                      </div>
                      <div>
                        Precipitation: {location.weather.readings?.precipitation_mm ?? "N/A"} mm
                      </div>
                      <div>
                        Pressure: {location.weather.readings?.pressure_hpa ?? "N/A"} hPa
                      </div>
                      <div>
                        <small>
                          Source: {location.weather.source || "Weather API"}
                        </small>
                      </div>
                      {location.weather.observed_at && (
                        <div>
                          <small>
                            Updated: {location.weather.observed_at}
                          </small>
                        </div>
                      )}
                    </>
                  ) : (
                    <p>Weather data currently unavailable.</p>
                  )}
                </div>
              </Popup>
            </CircleMarker>
          ))}


        </MapContainer>

      </div>


      {/* Susceptibility legend */}

      <div className="gis-legend">


        <div className="legend-title">

          Susceptibility Level

        </div>


        <div className="legend-items">


          <div>

            <span
              className="legend-color very-low"
            ></span>

            Very Low

          </div>


          <div>

            <span
              className="legend-color low"
            ></span>

            Low

          </div>


          <div>

            <span
              className="legend-color medium"
            ></span>

            Medium

          </div>


          <div>

            <span
              className="legend-color high"
            ></span>

            High

          </div>


          <div>

            <span
              className="legend-color very-high"
            ></span>

            Very High

          </div>

        </div>


        {/* Raster status */}

        <div className="raster-status">

          <span
            className={
              rasterLoaded
                ? "status-success"
                : "status-loading"
            }
          >

            {rasterLoaded

              ? "Susceptibility raster loaded"

              : "Loading raster..."}

          </span>

        </div>


        {/* Sensor status */}

        <div className="raster-status">

          <span className="status-success">

            {sensors.length} live sensors connected

          </span>

        </div>


        {/* Weather API location status */}
        <div className="raster-status">
          <span className="status-success">
            {weatherLocations.length} weather-monitored locations
          </span>
        </div>

        {/* Map marker legend */}
        <div className="raster-status">
          <span
            style={{
              display: "inline-block",
              width: "10px",
              height: "10px",
              borderRadius: "50%",
              background: "#60a5fa",
              border: "2px solid #2563eb",
              marginRight: "8px",
            }}
          />
          Weather API location
        </div>


        {/* Risk marker legend */}

        <div className="sensor-risk-legend">

          <div className="legend-title">

            Live Sensor Risk

          </div>


          <div className="legend-items">


            <div>

              <span
                className="risk-dot risk-low"
              ></span>

              Low

            </div>


            <div>

              <span
                className="risk-dot risk-medium"
              ></span>

              Medium

            </div>


            <div>

              <span
                className="risk-dot risk-high"
              ></span>

              High

            </div>


            <div>

              <span
                className="risk-dot risk-critical"
              ></span>

              Critical

            </div>

          </div>

        </div>

      </div>


    </div>

  );

}


export default GIS;
````

---

## `frontend/src/pages/MLPrediction.jsx`

````jsx
import { useState } from "react";

import {
  BrainCircuit,
  Mountain,
  Waves,
  Compass,
  CloudRain,
  Layers,
  Map,
  Route,
  AlertTriangle,
  CheckCircle2,
} from "lucide-react";

function MLPrediction() {
  const [formData, setFormData] = useState({
    DEM_Final: "",
    Slope: "",
    Aspect: "",
    Rainfall: "",
    Clay: "",
    LULC: "",
    Road_Dist: "",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const fields = [
    {
      name: "DEM_Final",
      label: "Elevation / DEM",
      placeholder: "e.g. 1800",
      icon: Mountain,
    },
    {
      name: "Slope",
      label: "Slope",
      placeholder: "e.g. 25",
      icon: Waves,
    },
    {
      name: "Aspect",
      label: "Aspect",
      placeholder: "e.g. 180",
      icon: Compass,
    },
    {
      name: "Rainfall",
      label: "Rainfall",
      placeholder: "e.g. 150",
      icon: CloudRain,
    },
    {
      name: "Clay",
      label: "Clay Content",
      placeholder: "e.g. 30",
      icon: Layers,
    },
    {
      name: "LULC",
      label: "Land Use / Land Cover",
      placeholder: "e.g. 40",
      icon: Map,
    },
    {
      name: "Road_Dist",
      label: "Distance to Road",
      placeholder: "e.g. 100",
      icon: Route,
    },
  ];

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/predict",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            DEM_Final: Number(formData.DEM_Final),
            Slope: Number(formData.Slope),
            Aspect: Number(formData.Aspect),
            Rainfall: Number(formData.Rainfall),
            Clay: Number(formData.Clay),
            LULC: Number(formData.LULC),
            Road_Dist: Number(formData.Road_Dist),
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Prediction request failed");
      }

      const data = await response.json();

      setResult(data);
    } catch (error) {
      console.error(error);
      alert("Could not connect to the ML backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">

      <div className="page-heading">
        <h1>ML Prediction</h1>

        <p>
          Analyze landslide susceptibility using the trained
          Random Forest model.
        </p>
      </div>

      <div className="prediction-container">

        <div className="prediction-card">

          <div className="section-header">
            <div>
              <h2>Environmental Factors</h2>

              <p
                style={{
                  margin: "6px 0 0",
                  color: "#7a8d8b",
                  fontSize: "12px",
                }}
              >
                Enter the seven GIS factors used by the ML model.
              </p>
            </div>

            <div className="stat-icon">
              <BrainCircuit size={20} />
            </div>
          </div>

          <form
            onSubmit={handleSubmit}
            className="prediction-form"
          >

            {fields.map((field) => {
              const Icon = field.icon;

              return (
                <div className="form-group" key={field.name}>

                  <label>
                    <span
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                      }}
                    >
                      <Icon size={15} />
                      {field.label}
                    </span>
                  </label>

                  <input
                    type="number"
                    step="any"
                    name={field.name}
                    value={formData[field.name]}
                    onChange={handleChange}
                    placeholder={field.placeholder}
                    required
                  />

                </div>
              );
            })}

            <button
              type="submit"
              className="predict-btn"
              disabled={loading}
            >
              <BrainCircuit size={18} />

              {loading
                ? "Analyzing..."
                : "Predict Landslide Risk"}
            </button>

          </form>

        </div>

        {result && (
          <div className="prediction-result">

            <div className="section-header">

              <h2>Prediction Result</h2>

              {result.prediction === 1 ? (
                <AlertTriangle size={22} />
              ) : (
                <CheckCircle2 size={22} />
              )}

            </div>

            <div className="result-grid">

              <div className="result-item">
                <span>Prediction</span>

                <strong>
                  {result.prediction === 1
                    ? "Landslide"
                    : "Non-Landslide"}
                </strong>
              </div>

              <div className="result-item">
                <span>Probability</span>

                <strong>
                  {result.probability}%
                </strong>
              </div>

              <div className="result-item">
                <span>Risk Level</span>

                <strong>
                  {result.risk_level}
                </strong>
              </div>

            </div>

          </div>
        )}

      </div>

    </div>
  );
}

export default MLPrediction;
````

---

## Files Not Included

The following data, binary, documentation, and lock files were excluded from the source code bundle in accordance with specifications:

| File Path | Size (Bytes) | Category / Reason |
|-----------|--------------|-------------------|
| `backend/.env` | 1,075 | Local Environment File (Excluded for security) |
| `backend/ml/landslide_random_forest_model.pkl` | 4,723,049 | Trained ML Model Binary |
| `documentation/LANDSLIDE_DOCUMENTATION.md` | 57,453 | Project Documentation |
| `documentation/LANDSLIDE_DOCUMENTATION_PART2.md` | 60,066 | Project Documentation |
| `documentation/LANDSLIDE_DOCUMENTATION_PART3.md` | 47,934 | Project Documentation |
| `documentation/LANDSLIDE_DOCUMENTATION_PART4.md` | 37,995 | Project Documentation |
| `documentation/Landslide_Early_Warning_System_Full_Source_Code.pdf` | 4,321,571 | PDF Documentation |
| `frontend/.gitignore` | 253 | Git Ignore File |
| `frontend/README.md` | 1,009 | Markdown Documentation |
| `frontend/package-lock.json` | 310,040 | Package Lock File |
| `frontend/public/favicon.svg` | 9,522 | Image Asset |
| `frontend/public/icons.svg` | 5,031 | Image Asset |
| `frontend/public/rasters/Landslide_Susceptibility_Probability.tif` | 4,898,928 | GIS Raster Data |
| `frontend/src/assets/hero.png` | 13,057 | Image Asset |
| `frontend/src/assets/react.svg` | 4,126 | Image Asset |
| `frontend/src/assets/vite.svg` | 8,709 | Image Asset |
| `sensor_data.csv` | 1,537 | Sensor Data CSV |

