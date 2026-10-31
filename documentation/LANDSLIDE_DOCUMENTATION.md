# Landslide Early Warning & Susceptibility Mapping System (GEORISK)
## Technical Architecture, System Specification & Source Code Documentation

> **Target Study Region**: Nilgiris District, Western Ghats, Tamil Nadu, India  
> **Documentation Date**: October 27, 2026  
> **Source Code Fidelity**: 100% Exact Copy (Zero modifications, zero omissions)  
> **Multi-Part Structure**: Due to the comprehensive inclusion of all 32 source code files (over 5,800 lines of code), this documentation is structured into four connected parts:
> * **[LANDSLIDE_DOCUMENTATION.md](file:///d:/Landslide-Early-Warning-System/LANDSLIDE_DOCUMENTATION.md)** (Master Document: Architecture, Datasets, ML Models, Operations, and Part 1 Backend / Config Source Code)
> * **[LANDSLIDE_DOCUMENTATION_PART2.md](file:///d:/Landslide-Early-Warning-System/LANDSLIDE_DOCUMENTATION_PART2.md)** (Part 2: Frontend Application Core, Components, Dashboard, ML Prediction, Sensors, Alerts, and History Source Code)
> * **[LANDSLIDE_DOCUMENTATION_PART3.md](file:///d:/Landslide-Early-Warning-System/LANDSLIDE_DOCUMENTATION_PART3.md)** (Part 3: Interactive GIS Leaflet Engine, Base Styles, and SVG Vector Assets)
> * **[LANDSLIDE_DOCUMENTATION_PART4.md](file:///d:/Landslide-Early-Warning-System/LANDSLIDE_DOCUMENTATION_PART4.md)** (Part 4: Complete Design System & Master Stylesheet App.css)

---

## 1. Project Overview

### 1.1 Problem Statement
The Nilgiris District located in the Western Ghats of Tamil Nadu, India, is one of the most landslide-vulnerable mountainous terrains in South Asia. Characterized by steep topographic slopes, high annual rainfall during both South-West and North-East monsoon seasons, weathered clay-rich lateritic soils, and rapid anthropogenic land-use modification (deforestation, road cuttings, and slope settlements), the region faces recurring catastrophic slope instability. Conventional disaster response mechanisms rely on post-incident relief or coarse, regional meteorology bulletins that lack localized spatial resolution and real-time geotechnical telemetry.

### 1.2 Objective of GEORISK
The **GEORISK Landslide Early Warning and Susceptibility Mapping System** provides a multi-tiered decision support platform that combines:
1. **Pre-Disaster Spatial Zoning**: Machine-learning-derived spatial susceptibility modeling utilizing satellite digital elevation models, terrain morphology, lithology, and infrastructure proximity to classify terrain into discrete risk zones (Very Low to Very High).
2. **On-Demand Geotechnical Inference**: Real-time evaluation of site-specific parameters via an interactive Random Forest predictive model API.
3. **Real-Time IoT Field Telemetry**: Continuous simulation and monitoring of geotechnical parameters (volumetric soil moisture, pore water pressure, precipitation, ground tilt angle, and atmospheric pressure).
4. **Meteorological Screening**: Integration with high-resolution numerical weather forecasts (Open-Meteo REST API) across 6 key administrative taluks/stations (Ooty, Coonoor, Kotagiri, Kundah, Gudalur, Pandalur).
5. **Tiered Alert Notification & Archival Protocol**: Automatic categorization of risk into **LOW**, **MEDIUM**, **HIGH**, and **CRITICAL** levels, accompanied by actionable evacuation guidelines and persistent local telemetry history.

### 1.3 Link to UN Sustainable Development Goal 13 (Climate Action)
This project directly aligns with **United Nations Sustainable Development Goal 13: Climate Action**, specifically:
* **Target 13.1**: *Strengthen resilience and adaptive capacity to climate-related hazards and natural disasters in all countries.* The system establishes an automated early-warning framework that gives vulnerable highland communities and disaster managers actionable lead time prior to fatal slope failure.
* **Target 13.3**: *Improve education, awareness-raising, and human and institutional capacity on climate change mitigation, adaptation, impact reduction, and early warning.* The interactive GIS visualizer and historical incident logs empower local planning authorities with transparent spatial and geotechnical risk intelligence.

---

## 2. Tech Stack and Libraries

### 2.1 Backend Subsystem
* **Runtime**: Python 3.13 (CPython)
* **API Framework**: FastAPI `0.142.4`
* **ASGI Server**: Uvicorn `0.54.0`
* **Data Validation & Schemas**: Pydantic `2.13.5` & `pydantic_core 2.46.5`
* **Machine Learning & Numerics**:
  * Scikit-Learn `1.9.1` (`RandomForestClassifier`)
  * NumPy `2.5.3`
  * SciPy `1.18.1`
  * Pandas `3.0.6`
  * Joblib `1.6.0` (model serialization and deserialization)
* **HTTP & Meteorological Client**: HTTPX `0.28.1` (Asynchronous HTTP requests to Open-Meteo REST API)
* **Database & Persistence**: PyMongo (`MongoClient` connecting to local MongoDB `mongodb://localhost:27017`)
  * *Note: `pymongo` is actively utilized in `backend/main.py`; it requires entry in `requirements.txt` upon next freeze.*

### 2.2 Frontend Subsystem
* **Core Framework**: React `19.2.8` & React DOM `19.2.8`
* **Build Tool & Bundler**: Vite `8.3.0` (with `@vitejs/plugin-react 6.1.1`)
* **Routing**: React Router DOM `7.18.4` (`BrowserRouter`, `Routes`, `Route`, `NavLink`)
* **Geospatial Mapping**:
  * Leaflet `1.9.4` & React-Leaflet `5.0.0`
  * GeoRaster `1.6.0` (Client-side binary GeoTIFF parser)
  * GeoRasterLayer for Leaflet `4.1.2` (Dynamic client-side WebGL/Canvas raster rendering)
* **Data Visualization & Icons**:
  * Recharts `3.10.1`
  * Lucide React `1.53.0` (Geospatial and system icons)
* **Styling**: Vanilla CSS (modular design system with glassmorphism, responsive CSS Grid, and custom color variables)
* **Linter & Code Quality**: Oxlint `1.81.0`

---

## 3. Folder Structure and File Manifest

```
d:/Landslide-Early-Warning-System/
├── backend/
│   ├── ml/
│   │   ├── __pycache__/                                 # Compiled Python bytecode cache
│   │   ├── landslide_random_forest_model.pkl            # Serialized trained Random Forest Classifier binary
│   │   └── model.py                                     # Model persistence loader via Joblib
│   ├── locations.py                                     # Coordinates and identifiers for 6 Nilgiris monitoring stations
│   ├── main.py                                          # FastAPI application entrypoint, CORS, REST routes & MongoDB hooks
│   ├── requirements.txt                                 # Locked backend Python dependencies manifest
│   ├── risk_engine.py                                   # Multi-parameter geotechnical hazard scoring algorithm
│   ├── sensor_data.py                                   # Real-time IoT sensor telemetry simulator
│   ├── test_weather.py                                  # Quick diagnostic verification script for Open-Meteo API
│   ├── test_weather_risk.py                             # Unittest suite validating weather risk heuristics & endpoints
│   ├── weather_risk.py                                  # Meteorological early-warning screening logic
│   └── weather_service.py                               # Asynchronous Open-Meteo REST API client
├── documentation/
│   └── Landslide_Early_Warning_System_Full_Source_Code.pdf # Previous technical PDF documentation export
├── frontend/
│   ├── dist/                                            # Production-optimized Vite build bundle
│   ├── public/
│   │   ├── favicon.svg                                  # Application favicon asset
│   │   ├── icons.svg                                    # SVG vector sprite sheet
│   │   └── rasters/
│   │       └── Landslide_Susceptibility_Probability.tif # High-resolution GeoTIFF susceptibility probability raster
│   ├── src/
│   │   ├── assets/
│   │   │   ├── hero.png                                 # Visual brand graphic
│   │   │   ├── react.svg                                # React framework logo
│   │   │   └── vite.svg                                 # Vite tooling logo
│   │   ├── components/
│   │   │   ├── Header.jsx                               # Executive header component with active alert badges
│   │   │   └── Sidebar.jsx                              # Responsive navigation sidebar with active link routing
│   │   ├── pages/
│   │   │   ├── Alerts.jsx                               # Tiered early-warning alert notifications feed
│   │   │   ├── Dashboard.jsx                            # Live operational command center dashboard
│   │   │   ├── GIS.jsx                                  # Interactive Leaflet GIS susceptibility and telemetry map
│   │   │   ├── History.jsx                              # Sensor telemetry & risk archival page (New implementation)
│   │   │   ├── MLPrediction.jsx                         # 7-factor geotechnical parameter prediction form
│   │   │   └── Sensors.jsx                              # Live IoT physical sensor gauge cards
│   │   ├── App.css                                      # Primary application design system & page stylesheets
│   │   ├── App.jsx                                      # Main React router layout wrapper
│   │   ├── index.css                                    # Reset styles and typography definitions
│   │   └── main.jsx                                     # React DOM bootstrap file
│   ├── .gitignore                                       # Git ignore exclusions
│   ├── .oxlintrc.json                                   # Oxlint static analysis rules
│   ├── index.html                                       # HTML5 entrypoint shell
│   ├── package.json                                     # Node.js NPM project manifest and dependencies
│   ├── package-lock.json                                # Lockfile for npm package tree
│   ├── README.md                                        # Frontend template readme
│   └── vite.config.js                                   # Vite server and React plugin build configuration
├── LANDSLIDE_DOCUMENTATION.md                           # Master Documentation (Sections 1-4, 6-12, and Part 1 Backend Code)
├── LANDSLIDE_DOCUMENTATION_PART2.md                     # Part 2 Documentation (Frontend Application Core & Pages Code)
└── LANDSLIDE_DOCUMENTATION_PART3.md                     # Part 3 Documentation (GIS Leaflet Engine & CSS Styles Code)
```

---

## 4. Datasets Used

The landslide susceptibility model is conditioned on 7 primary geo-environmental and anthropogenic causal factors across the Nilgiris District:

| # | Conditioning Factor | Source / Origin | Format / Scale | Geotechnical & Hydrological Significance |
|---|---------------------|-----------------|----------------|------------------------------------------|
| 1 | **DEM (Elevation)** | SRTM 30m / Copernicus DEM | 32-bit Float GeoTIFF (m) | High elevations govern orographic precipitation, gravitational potential energy, and slope shearing stress. |
| 2 | **Slope Angle** | Derived from DEM via GDAL/QGIS | Degrees (0° to 90°) | Direct driver of shear stress. Slopes between 25°–45° represent critical failure thresholds in Nilgiris colluvium. |
| 3 | **Aspect** | Derived from DEM via GDAL/QGIS | Azimuth (0° to 360°) | Controls solar insolation, prevailing monsoon wind exposure, and soil desiccation/saturation cycles. |
| 4 | **Cumulative Rainfall** | CHIRPS / IMD Station Records | mm / continuous raster | Chief dynamic triggering factor inducing rapid pore water pressure buildup and reducing effective normal stress. |
| 5 | **Soil Clay Content** | Harmonized World Soil Database (HWSD) / ICAR | Percentage (%) | Clay minerals (kaolinite/illite) swell when saturated, decreasing internal friction angle and fostering slip surfaces. |
| 6 | **Land Use / Land Cover (LULC)** | ESA WorldCover 10m / Sentinel-2 | Categorical Code / Float | Dense shola forest stabilizes slopes via root cohesion; tea plantations and bare cut slopes exhibit higher vulnerability. |
| 7 | **Distance to Roads** | OpenStreetMap / PWD Road Network | Euclidean distance (meters) | Toe excavation, toe cutting, and road drainage runoff heavily destabilize adjacent cut slopes. |
| 8 | **Landslide Inventory** | Geological Survey of India (GSI) / Historical Records | Point Shapefile / Vector CSV | Historical landslide event centroids used as positive class (1) for supervised training. |
| 9 | **Non-Landslide Samples** | Generated randomly in low-slope stable terrain | Point Shapefile / Vector CSV | Sampled non-landslide points used as negative class (0) for balanced classification. |

---

## 5. Complete Source Code — Part 1: Backend & Configuration Subsystems

Below is the complete, unedited source code for each backend and configuration file, accompanied by file summaries and block explanations.

---

### File 1: `backend/main.py`
* **Relative Path**: `backend/main.py`
* **Purpose**: Core FastAPI application server entrypoint providing CORS middleware, MongoDB connectivity hooks, and REST endpoints for machine learning inference (`/api/predict`), IoT sensor telemetry (`/api/sensors`), geotechnical risk scoring (`/api/risk`), station coordinates (`/api/locations`), weather querying (`/api/weather`), and weather screening (`/api/weather-risk`).

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

from pymongo import MongoClient
from datetime import datetime, timezone

# Connect to MongoDB
MONGO_URL = "mongodb://localhost:27017"

client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)

# Select the database
db = client["slope_guard_ai"]

# Create collections (MongoDB creates them when first used)
sensor_history = db["sensor_history"]
risk_predictions = db["risk_predictions"]
alerts_collection = db["alerts"]


try:
    client.admin.command("ping")
    print("MongoDB connected successfully!")
except Exception as e:
    print("MongoDB connection failed:", e)




sys.path.append(os.path.dirname(__file__))

from ml.model import model
from sensor_data import generate_sensor_data
from risk_engine import calculate_risk
from locations import get_monitoring_locations
from weather_service import get_weather
from weather_risk import assess_weather_risk

app = FastAPI(
    title="Nilgiris Landslide Early Warning System",
    description="Backend API for GIS, ML, sensors and alerts",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        "message": "Nilgiris Landslide Early Warning System API is running"
    }


@app.get("/api/status")
def system_status():
    return {
        "status": "online",
        "system": "Landslide Early Warning System",
        "location": "Nilgiris District, Tamil Nadu"
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
        data.Road_Dist
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
        "risk_level": risk_level
    }

@app.get("/api/sensors")
def get_sensors():

    sensors = generate_sensor_data()

    return {
        "count": len(sensors),
        "sensors": sensors
    }
@app.get("/api/risk")
def get_risk():

    sensors = generate_sensor_data()

    results = []

    for sensor in sensors:

        risk = calculate_risk(
            sensor["readings"]
        )

        results.append({
            "sensor_id": sensor["sensor_id"],
            "location": sensor["location"],
            "readings": sensor["readings"],
            "risk_score": risk["risk_score"],
            "risk_level": risk["risk_level"]
        })

    return {
        "count": len(results),
        "sensors": results
    }

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
        "locations": locations
    }


@app.get("/api/weather")
def get_weather_for_locations():

    locations = get_monitoring_locations()

    weather_locations = [
        location
        for location in locations
        if location["monitoring_type"] == "weather_api"
    ]

    results = []

    for location in weather_locations:

        weather = get_weather(
            location["latitude"],
            location["longitude"]
        )

        results.append({
            "location_id": location["location_id"],
            "name": location["name"],
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "monitoring_type": "weather_api",
            "weather": weather
        })

    return {
        "count": len(results),
        "locations": results
    }


@app.get("/api/weather-risk")
def get_weather_risk_for_locations():

    locations = get_monitoring_locations()

    weather_locations = [
        location
        for location in locations
        if location["monitoring_type"] == "weather_api"
    ]

    results = []

    for location in weather_locations:

        weather = get_weather(
            location["latitude"],
            location["longitude"]
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
        "locations": results
    }
```

#### Detailed Code Explanation
* **Lines 1–9**: Imports essential framework utilities from FastAPI, Pydantic, system modules, and PyMongo client.
* **Lines 10–29**: Sets up a connection to a local MongoDB instance at `mongodb://localhost:27017` under the database name `slope_guard_ai`. Pre-defines references to three collections: `sensor_history`, `risk_predictions`, and `alerts`. A diagnostic `ping` command validates whether MongoDB is actively running without crashing the application on failure.
* **Lines 42–54**: Instantiates the FastAPI application with title and metadata. Attaches `CORSMiddleware` configured to allow cross-origin requests from the Vite frontend running on `http://localhost:5173`.
* **Lines 57–65**: `PredictionInput` Pydantic class defining strict float validation for the 7 geo-environmental features: `DEM_Final`, `Slope`, `Aspect`, `Rainfall`, `Clay`, `LULC`, and `Road_Dist`.
* **Lines 83–111**: `/api/predict` endpoint: extracts features into a 2D array, calls `model.predict()` for the binary class, computes the positive class probability via `model.predict_proba()`, maps the probability to a discrete risk category (`HIGH` for $\ge 70\%$, `MEDIUM` for $\ge 40\%$, else `LOW`), and returns JSON results.
* **Lines 113–121**: `/api/sensors` endpoint: calls `generate_sensor_data()` to return simulated telemetry from physical sensor stations.
* **Lines 122–146**: `/api/risk` endpoint: iterates over generated sensor data, feeds the physical readings into `calculate_risk()`, and returns aggregated hazard scores and risk classifications.
* **Lines 148–164**: `/api/locations` endpoint: fetches the 6 Nilgiris monitoring locations and summarizes counts by `sensor` vs. `weather_api` types.
* **Lines 167–200**: `/api/weather` endpoint: queries Open-Meteo for all weather-monitored stations and returns live atmospheric readings.
* **Lines 202–243**: `/api/weather-risk` endpoint: applies meteorological early warning screening heuristics to real-time precipitation and rainfall readings.

---

### File 2: `backend/locations.py`
* **Relative Path**: `backend/locations.py`
* **Purpose**: Geographic registry maintaining spatial coordinates, location identifiers, names, and monitoring mechanisms for key stations across the Nilgiris District.

```python

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
```

#### Detailed Code Explanation
* **Lines 2–51**: Defines `MONITORING_LOCATIONS`, a list of dictionaries capturing geographical metadata for 6 major settlements in the Nilgiris: Ooty (LOC001), Coonoor (LOC002), Kotagiri (LOC003), Kundah (LOC004), Gudalur (LOC005), and Pandalur (LOC006).
* Ooty is designated with `monitoring_type: "sensor"` associated with sensor ID `S001`, while the remaining 5 sites are configured as `monitoring_type: "weather_api"`.
* **Lines 54–55**: Helper function `get_monitoring_locations()` returning the registry to caller modules.

---

### File 3: `backend/risk_engine.py`
* **Relative Path**: `backend/risk_engine.py`
* **Purpose**: Multi-parameter geotechnical heuristic scoring algorithm that weights real-time environmental factors (rainfall intensity, soil moisture saturation, atmospheric humidity, ground tilt displacement, and barometric depression) into a composite 0–100 hazard index.

```python
def calculate_risk(readings):
    """
    Calculate real-time landslide risk
    using simulated sensor readings.
    """

    rainfall = readings.get("rainfall", 0)
    soil_moisture = readings.get("soil_moisture", 0)
    humidity = readings.get("humidity", 0)
    tilt = readings.get("tilt", 0)
    pressure = readings.get("pressure", 1013)

    score = 0

    # Rainfall contribution
    if rainfall >= 100:
        score += 30
    elif rainfall >= 70:
        score += 20
    elif rainfall >= 40:
        score += 10

    # Soil moisture contribution
    if soil_moisture >= 80:
        score += 25
    elif soil_moisture >= 65:
        score += 15
    elif soil_moisture >= 50:
        score += 8

    # Humidity contribution
    if humidity >= 90:
        score += 15
    elif humidity >= 80:
        score += 10
    elif humidity >= 70:
        score += 5

    # Ground tilt contribution
    if tilt >= 6:
        score += 25
    elif tilt >= 3:
        score += 15
    elif tilt >= 1:
        score += 5

    # Atmospheric pressure contribution
    if pressure < 1000:
        score += 5

    # Risk classification
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
        "risk_level": risk_level
    }
```

#### Detailed Code Explanation
* **Lines 1–12**: Extracts 5 physical variables from the incoming readings dictionary with safe fallbacks: `rainfall` (default 0 mm), `soil_moisture` (default 0%), `humidity` (default 0%), `tilt` (default 0°), and `pressure` (default 1013 hPa).
* **Lines 16–22**: **Rainfall weighting** (Max 30 points): $\ge 100\text{ mm} \to +30$, $\ge 70\text{ mm} \to +20$, $\ge 40\text{ mm} \to +10$.
* **Lines 24–30**: **Soil Moisture weighting** (Max 25 points): $\ge 80\% \to +25$, $\ge 65\% \to +15$, $\ge 50\% \to +8$.
* **Lines 32–38**: **Relative Humidity weighting** (Max 15 points): $\ge 90\% \to +15$, $\ge 80\% \to +10$, $\ge 70\% \to +5$.
* **Lines 40–46**: **Ground Tilt Angle weighting** (Max 25 points): $\ge 6^\circ \to +25$, $\ge 3^\circ \to +15$, $\ge 1^\circ \to +5$. Reflects physical slope displacement detected by inclinometers.
* **Lines 48–50**: **Atmospheric Pressure weighting** (Max 5 points): $< 1000\text{ hPa} \to +5$ (cyclonic depression indicator).
* **Lines 52–64**: Classifies composite score: $\ge 75 \to \textbf{CRITICAL}$, $\ge 50 \to \textbf{HIGH}$, $\ge 25 \to \textbf{MEDIUM}$, $< 25 \to \textbf{LOW}$. Returns structured dictionary.

---

### File 4: `backend/sensor_data.py`
* **Relative Path**: `backend/sensor_data.py`
* **Purpose**: Generates dynamic, simulated real-time IoT sensor telemetry across three monitoring nodes in the Nilgiris for demonstration and frontend live testing.

```python
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
```

#### Detailed Code Explanation
* **Lines 4–26**: Defines three virtual sensor nodes (`S001`, `S002`, `S003`) clustered around Ooty (latitudes 11.3850 to 11.4500, longitudes 76.6800 to 76.7200).
* **Lines 29–65**: `generate_sensor_data()` synthesizes realistic environmental values on each call:
  * Rainfall: 40.0 to 130.0 mm
  * Soil moisture: 50.0% to 90.0%
  * Temperature: 20.0°C to 28.0°C
  * Humidity: 70.0% to 98.0%
  * Surface pressure: 995.0 to 1010.0 hPa
  * Ground tilt: 1.0° to 8.0°

---

### File 5: `backend/weather_service.py`
* **Relative Path**: `backend/weather_service.py`
* **Purpose**: Communicates with the public Open-Meteo REST API to query real-time meteorological conditions for specific geographic coordinates in the Nilgiris with robust HTTP timeout and error handling.

```python

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
```

#### Detailed Code Explanation
* **Lines 10–21**: Formulates query parameters requesting `temperature_2m`, `relative_humidity_2m`, `precipitation`, `rain`, and `surface_pressure` set to the `Asia/Kolkata` time zone.
* **Lines 23–29**: Initiates synchronous HTTP GET request with a 15-second timeout via `httpx.get()`.
* **Lines 30–58**: Checks HTTP response status (`raise_for_status()`), parses JSON body, extracts `current` payload, and standardizes readings into standard scientific keys.
* **Lines 60–64**: Safely catches `httpx.HTTPError` and `ValueError`, returning an `{ "available": False, "error": ... }` response without breaking downstream API calls.

---

### File 6: `backend/weather_risk.py`
* **Relative Path**: `backend/weather_risk.py`
* **Purpose**: Meteorological early-warning screening logic that verifies meteorological data integrity and explicitly flags weather-only risk evaluations as unassessed prototypes in the absence of time-window-specific historical landslide rainfall thresholds.

```python
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
```

#### Detailed Code Explanation
* **Lines 4–9**: Defines `METHOD_DESCRIPTION`, a clear disclaimer stating that weather screening is an unvalidated prototype and not a trained ML prediction or official warning.
* **Lines 17–25**: Guard clause checking for invalid or unavailable weather dictionaries.
* **Lines 27–56**: Strict data validation loop verifying that `rain_mm` and `precipitation_mm` are non-negative, finite numeric floats. Rejects booleans, NaN, infinity, or overflow numbers.
* **Lines 63–76**: Returns status `"unassessed"` with full scientific justification and factor breakdown.

---

### File 7: `backend/test_weather.py`
* **Relative Path**: `backend/test_weather.py`
* **Purpose**: Minimal diagnostic verification script checking live connectivity and payload integrity from the Open-Meteo API for coordinates in Kotagiri/Ooty (`11.4200, 76.7400`).

```python
from weather_service import get_weather

result = get_weather(11.4200, 76.7400)

print(result)
```

#### Detailed Code Explanation
* **Lines 1–5**: Imports `get_weather`, executes an API call for test coordinates (`11.4200, 76.7400`), and outputs the dictionary result to standard output.

---

### File 8: `backend/test_weather_risk.py`
* **Relative Path**: `backend/test_weather_risk.py`
* **Purpose**: Automated unit and integration test suite executing via Python's `unittest` and FastAPI's `TestClient` to validate weather screening heuristics, invalid input edge cases, endpoint responses, and route consistency.

```python
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
```

#### Detailed Code Explanation
* **Lines 10–26**: Tests that standard meteorological inputs report status `"unassessed"` with category `"UNASSESSED"`.
* **Lines 28–55**: Parameterized subtests with `None`, string numbers, NaN, infinity, overflow, negative values, and boolean flags to ensure bad inputs degrade gracefully to status `"unavailable"`.
* **Lines 56–82**: Uses `unittest.mock.patch` to mock `get_weather` and validates that `/api/weather-risk` iterates across all 5 non-sensor weather stations (Coonoor, Kotagiri, Kundah, Gudalur, Pandalur).
* **Lines 83–152**: Integration test validating route persistence, HTTP status codes, count contracts, and schema structure for all 5 core endpoints.

---

### File 9: `backend/ml/model.py`
* **Relative Path**: `backend/ml/model.py`
* **Purpose**: Model persistence deserializer loading the trained Random Forest classifier (`landslide_random_forest_model.pkl`) into memory using Joblib upon module import.

```python
import joblib
import os

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "landslide_random_forest_model.pkl"
)

model = joblib.load(MODEL_PATH)

print("Landslide Random Forest model loaded successfully!")
```

#### Detailed Code Explanation
* **Lines 4–7**: Constructs an absolute filesystem path to `landslide_random_forest_model.pkl` located in the same directory.
* **Lines 9–11**: Calls `joblib.load(MODEL_PATH)` to deserialize the trained Scikit-Learn `RandomForestClassifier` into memory and prints a confirmation banner.

---

### File 10: `backend/requirements.txt`
* **Relative Path**: `backend/requirements.txt`
* **Purpose**: Pinned specification of Python backend dependencies.

```txt
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
```

#### Detailed Code Explanation
* Contains all backend libraries including `fastapi==0.142.4`, `scikit-learn==1.9.1`, `joblib==1.6.0`, `httpx==0.28.1`, `pandas==3.0.6`, `numpy==2.5.3`, and `uvicorn==0.54.0`.
* *Note on Architecture*: `pymongo` is imported in `backend/main.py`; ensure `pip install pymongo` is executed in environments where MongoDB persistence is active.

---

### File 11: `frontend/package.json`
* **Relative Path**: `frontend/package.json`
* **Purpose**: Node.js package manifest declaring dependencies, build scripts, and metadata for the React 19 frontend application.

```json
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
```

#### Detailed Code Explanation
* **Scripts**: `npm run dev` launches the Vite dev server, `npm run build` runs rollup compilation into `dist/`, and `npm run lint` invokes `oxlint`.
* **Dependencies**: React 19, Leaflet 1.9.4, React-Leaflet 5.0.0, Georaster 1.6.0, Georaster-layer-for-leaflet 4.1.2, Lucide React icons, and React Router DOM 7.18.4.

---

### File 12: `frontend/vite.config.js`
* **Relative Path**: `frontend/vite.config.js`
* **Purpose**: Vite build configuration integrating the `@vitejs/plugin-react` Fast Refresh plugin.

```javascript
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
})
```

---

### File 13: `frontend/.oxlintrc.json`
* **Relative Path**: `frontend/.oxlintrc.json`
* **Purpose**: Configuration file for Oxlint static analysis enforcing React hooks validation and component export conventions.

```json
{
  "$schema": "./node_modules/oxlint/configuration_schema.json",
  "plugins": ["react", "oxc"],
  "rules": {
    "react/rules-of-hooks": "error",
    "react/only-export-components": ["warn", { "allowConstantExport": true }]
  }
}
```

---

### File 14: `frontend/.gitignore`
* **Relative Path**: `frontend/.gitignore`
* **Purpose**: Version control exclusion list preventing log files, node modules, build artifacts, and IDE metadata from repository commits.

```txt
# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

node_modules
dist
dist-ssr
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?
```

---

### File 15: `frontend/index.html`
* **Relative Path**: `frontend/index.html`
* **Purpose**: Main HTML5 entry document providing the viewport configuration, favicon link, and root DOM container for React mounting.

```html
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
```

---

### File 16: `frontend/README.md`
* **Relative Path**: `frontend/README.md`
* **Purpose**: Default frontend project documentation outlining Vite plugins, React compiler guidance, and Oxlint usage.

```markdown
# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some Oxlint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the Oxlint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and Oxlint's TypeScript related rules in your project.
```

---

## 6. Machine Learning Model Details

### 6.1 Algorithm & Architecture
The landslide susceptibility model is an ensemble **Random Forest Classifier** (`RandomForestClassifier`) serialized in `backend/ml/landslide_random_forest_model.pkl` (4.72 MB). Random Forest operates by constructing an ensemble of orthogonal decision trees during training and outputting the mode of the individual trees' classes (or the mean predicted class probabilities).

### 6.2 Feature Vector Definition
The model expects exactly 7 features in the following strict order:
1. `DEM_Final` (Digital Elevation Model in meters)
2. `Slope` (Slope gradient in degrees)
3. `Aspect` (Slope orientation in azimuth degrees 0–360)
4. `Rainfall` (Precipitation accumulation in mm)
5. `Clay` (Soil clay fraction percentage)
6. `LULC` (Land Use / Land Cover code)
7. `Road_Dist` (Euclidean distance to closest transportation artery in meters)

### 6.3 Hyperparameters and Training Metrics
* **Algorithm**: Random Forest Classifier (`sklearn.ensemble.RandomForestClassifier`)
* **Number of Estimators**: *Needs confirmation from offline training logs* (~100–300 trees based on 4.72 MB model footprint)
* **Train / Test Split Ratio**: *Needs confirmation from offline training logs* (Typical standard is 70/30 or 80/20 train/test split with stratified sampling)
* **Model Accuracy / AUC-ROC**: *Needs confirmation from offline training logs* (Operational threshold maps probabilities into High $\ge 70\%$, Medium $40\%-70\%$, Low $< 40\%$)

---

## 7. Spatial Validation

### 7.1 Method
Spatial validation of landslide susceptibility maps requires evaluating the concordance between the predicted susceptibility index raster and known historical landslide event locations:
1. **Receiver Operating Characteristic (ROC) & Area Under the Curve (AUC)**: Evaluates the true positive rate versus false positive rate across continuous classification thresholds.
2. **Frequency Ratio (FR) & Relative Landslide Density (R-Index)**: Calculates the percentage of historical landslide occurrences falling inside the Very High and High susceptibility zones relative to their spatial aerial extent.

### 7.2 Results
* **Spatial Alignment**: The output GeoTIFF raster [`Landslide_Susceptibility_Probability.tif`](file:///d:/Landslide-Early-Warning-System/frontend/public/rasters/Landslide_Susceptibility_Probability.tif) spans the Nilgiris bounding envelope (centered at 11.4102° N, 76.6950° E).
* **Validation Scores**: *Needs confirmation from offline GIS validation logs* (Spatial raster exhibits high concentration of high-probability cells along steep escarpments and road cuttings near Coonoor, Ooty, and Kotagiri).

---

## 8. Geotechnical Risk Engine, Dashboard, Sensors and Alerts

The software architecture connects three tiers of risk assessment:
```
+-----------------------------------------------------------------------------------------+
|                                    GEORISK PLATFORM                                     |
+-----------------------------------------------------------------------------------------+
|                                                                                         |
|  [Tier 1: Pre-Failure Spatial Zoning]  --> GeoTIFF Raster parsed via GeoRaster in GIS   |
|  [Tier 2: On-Demand ML Prediction]     --> 7-factor geotechnical inference (/api/predict)|
|  [Tier 3: Dynamic Multi-Sensor Engine] --> calculate_risk(readings) scoring (0-100)     |
|                                                                                         |
|  SCORING MATRIX:                                                                        |
|  * Rainfall (max 30 pts)     : >=100mm (+30), >=70mm (+20), >=40mm (+10)                |
|  * Soil Moisture (max 25 pts): >=80% (+25), >=65% (+15), >=50% (+8)                     |
|  * Humidity (max 15 pts)     : >=90% (+15), >=80% (+10), >=70% (+5)                     |
|  * Ground Tilt (max 25 pts)  : >=6 deg (+25), >=3 deg (+15), >=1 deg (+5)               |
|  * Barometric Pressure       : <1000 hPa (+5)                                           |
|                                                                                         |
|  COMPOSITE RISK TIERS:                                                                  |
|  * CRITICAL (>= 75) : Immediate slope evacuation warning                                |
|  * HIGH     (>= 50) : High landslide risk alert triggered                               |
|  * MEDIUM   (>= 25) : Heightened monitoring status                                      |
|  * LOW      (< 25)  : Normal baseline conditions                                        |
+-----------------------------------------------------------------------------------------+
```

---

## 9. How to Run the System

### 9.1 Prerequisites
1. **Python 3.10+** (Python 3.13 recommended)
2. **Node.js 18+** & npm
3. **MongoDB** (optional, for persistent historical sensor logging on `localhost:27017`)

### 9.2 Step-by-Step Execution Order

#### Step 1: Start the FastAPI Backend
```powershell
cd d:\Landslide-Early-Warning-System\backend
# Create virtual environment if not already existing:
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install requirements:
pip install -r requirements.txt
pip install pymongo

# Start Uvicorn server:
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
*Backend will be accessible at `http://127.0.0.1:8000` with interactive Swagger docs at `http://127.0.0.1:8000/docs`.*

#### Step 2: Start the React + Vite Frontend
```powershell
cd d:\Landslide-Early-Warning-System\frontend
# Install npm dependencies:
npm install

# Start Vite local development server:
npm run dev
```
*Frontend will launch at `http://localhost:5173`.*

#### Step 3: Run Automated Test Suites
```powershell
cd d:\Landslide-Early-Warning-System\backend
python -m unittest test_weather_risk.py
```

---

## 10. Output Files and Representations

1. **`frontend/public/rasters/Landslide_Susceptibility_Probability.tif`**:
   * Binary 32-bit floating point GeoTIFF (4.90 MB) covering the Nilgiris District. Pixel values represent predicted landslide probability ranging from $0.00$ to $1.00$. Rendered client-side into 5 distinct color bands (Green, Yellow-Green, Yellow, Orange, Red).
2. **`backend/ml/landslide_random_forest_model.pkl`**:
   * Serialized Scikit-Learn Random Forest model (4.72 MB) containing the ensemble decision trees, feature thresholds, and leaf nodes.
3. **`frontend/dist/`**:
   * Production build assets containing bundled, minified JS (`index-CVW1zzj_.js`), CSS (`index-C6i3LRe-.css`), and optimized HTML for deployment to static web hosts.

---

## 11. Newly Added / Updated Parts (Summary of Step 3)

| Component | Previous Documentation Export | Current Project State | Nature of Modification |
|-----------|-------------------------------|-----------------------|------------------------|
| **`frontend/src/pages/History.jsx`** | 10 lines (placeholder text) | 295 lines (full implementation) | **Major Feature**: Interactive historical telemetry viewer, periodic 5s polling, 500-event local archival in `localStorage`, risk filtering, and KPI stat cards. |
| **`frontend/src/App.css`** | 2,017 lines (32,072 bytes) | 2,168 lines (34,285 bytes) | **Design System Extension**: Added lines 2019–2168 with complete styling for tables, toolbars, badges, and responsive viewports. |
| **`backend/main.py`** | 217 lines (pure in-memory) | 243 lines (with MongoDB) | **Persistence Integration**: Added PyMongo `MongoClient` connecting to `slope_guard_ai` database with collections `sensor_history`, `risk_predictions`, and `alerts`. |
| **`backend/requirements.txt`** | 28 dependencies | 28 dependencies | **Maintenance Note**: `pymongo` actively imported in `main.py` but pending addition to `requirements.txt`. |

---

## 12. Limitations and Future Work

### 12.1 Limitations Evident from the Code
1. **Simulated IoT Telemetry**: `backend/sensor_data.py` generates sensor readings using Python `random.uniform()`. Physical hardware transceivers (LoRaWAN, Zigbee, or cellular GSM telemetry from field inclinometers and piezometers) are not yet interfaced.
2. **Unvalidated Weather Screening**: As highlighted in `backend/weather_risk.py`, Open-Meteo rainfall queries operate as an unvalidated screening heuristic because time-window-specific historical rainfall-trigger thresholds (e.g., Caine's intensity-duration thresholds or GSI regional thresholds) are not currently parameterized in the code.
3. **Separate Training Pipeline**: Preprocessing scripts (DEM clipping, slope derivation, raster alignment to identical projection/resolution, and cross-validation) were executed offline, leaving only the inference artifact (`.pkl`) in the repository.

### 12.2 Future Work
1. **Hardware Ingestion Gateway**: Implement MQTT or Webhook listeners in FastAPI to ingest genuine telemetry from field sensor nodes installed across Nilgiris slopes.
2. **Empirical Rainfall Threshold Calibration**: Fit regional Intensity-Duration (I-D) power-law curves ($I = \alpha D^{-\beta}$) calibrated against Nilgiris monsoon landslide inventories.
3. **Persistent Cloud Database Replication**: Complete the transition from browser `localStorage` to the newly established MongoDB collections (`slope_guard_ai.sensor_history`) for centralized archival and analytics.

---

> **Continued in Part 2, Part 3, and Part 4**:
> * To view the complete source code and line explanations for all React frontend pages, components, and routers, proceed to **[LANDSLIDE_DOCUMENTATION_PART2.md](file:///d:/Landslide-Early-Warning-System/LANDSLIDE_DOCUMENTATION_PART2.md)**.
> * To view the complete source code and line explanations for the GIS Leaflet engine, base CSS, and SVG vector assets, proceed to **[LANDSLIDE_DOCUMENTATION_PART3.md](file:///d:/Landslide-Early-Warning-System/LANDSLIDE_DOCUMENTATION_PART3.md)**.
> * To view the complete 2,168-line source code and block-by-block design breakdown for the master stylesheet `App.css`, proceed to **[LANDSLIDE_DOCUMENTATION_PART4.md](file:///d:/Landslide-Early-Warning-System/LANDSLIDE_DOCUMENTATION_PART4.md)**.
