# Landslide Early Warning & Susceptibility Mapping System (GEORISK)
## Technical Source Code Documentation — Part 2: Frontend Application & UI Pages

> **Project Target**: Nilgiris District, Tamil Nadu, India  
> **Master Documentation**: See **[LANDSLIDE_DOCUMENTATION.md](file:///d:/Landslide-Early-Warning-System/LANDSLIDE_DOCUMENTATION.md)** for Architectural Overview, Datasets, ML Models, and Backend Source Code.  
> **Source Code Fidelity**: 100% Exact Copy (Indentation, imports, variables, and structure preserved verbatim).

---

## Complete Source Code: Frontend Core, Components, and Application Views

---

### File 17: `frontend/src/main.jsx`
* **Relative Path**: `frontend/src/main.jsx`
* **What the file does**:
  Entrypoint bootstrapping script for the React 19 single-page application. Mounts the root component inside `React.StrictMode`, wraps the component tree with `BrowserRouter` for client-side routing, and imports global stylesheets.

```jsx
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
```

#### Detailed Code Explanation
* **Lines 1–7**: Imports the React core library, modern `ReactDOM.createRoot` API from `react-dom/client`, `BrowserRouter` from `react-router-dom`, the root `App` container component, and global CSS stylesheets (`index.css` and `App.css`).
* **Lines 9–15**: Selects the root DOM container element `<div id="root">` from `index.html` and renders the application enclosed in `<React.StrictMode>` for runtime development warnings and `<BrowserRouter>` for HTML5 history API navigation.

---

### File 18: `frontend/src/App.jsx`
* **Relative Path**: `frontend/src/App.jsx`
* **What the file does**:
  Root application layout component orchestrating the master user interface structure. Combines the persistent sidebar navigation, top executive status header, and primary content viewport managed via client-side route transitions.

```jsx
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
```

#### Detailed Code Explanation
* **Lines 1–11**: Imports router components (`Routes`, `Route`), common UI chrome (`Sidebar`, `Header`), and the 6 primary page views (`Dashboard`, `GIS`, `Sensors`, `MLPrediction`, `Alerts`, `History`).
* **Lines 15–44**: Constructs the top-level application flexbox grid (`.app-layout`):
  * Places `<Sidebar />` fixed on the left margin.
  * Places `<div className="main-area">` on the right containing `<Header />` and `<main className="content-area">`.
  * Configures URL path routing:
    * `/` $\to$ `<Dashboard />`
    * `/gis` $\to$ `<GIS />`
    * `/sensors` $\to$ `<Sensors />`
    * `/ml` $\to$ `<MLPrediction />`
    * `/alerts` $\to$ `<Alerts />`
    * `/history` $\to$ `<History />`

---

### File 19: `frontend/src/components/Header.jsx`
* **Relative Path**: `frontend/src/components/Header.jsx`
* **What the file does**:
  Executive navigation header displayed across all views. Features the study district title, a pulsing green system online badge, and an alert notification badge displaying active hazard counts.

```jsx
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
```

#### Detailed Code Explanation
* **Lines 1–3**: Imports Lucide vector icons (`Bell` for notification alerts, `Circle` for status light indicators).
* **Lines 5–11**: Defines the left title container branding the system for "Nilgiris District, Tamil Nadu".
* **Lines 12–25**: Right-hand action bar housing the `.live-status` indicator with a solid green circle and a `.notification-btn` button displaying a red badge counter.

---

### File 20: `frontend/src/components/Sidebar.jsx`
* **Relative Path**: `frontend/src/components/Sidebar.jsx`
* **What the file does**:
  Left-hand navigational drawer providing persistent navigation across all functional views. Uses React Router's `NavLink` to dynamically highlight the active route and displays the overall system online status.

```jsx
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
```

#### Detailed Code Explanation
* **Lines 15–46**: Declares `menuItems` configuration mapping page titles, target URL routes, and Lucide vector icons (`Dashboard`, `Live GIS`, `Sensors`, `ML Prediction`, `Alerts`, `History`).
* **Lines 51–60**: Sidebar branding displaying the `ShieldAlert` crest and title "Landslide Early Warning".
* **Lines 62–85**: Dynamic navigation list iterating over `menuItems` using `NavLink`. Passes a function to `className` to append the `.active` class when current browser URL matches the route.
* **Lines 87–99**: Bottom footer badge highlighting operational status ("System Online - Monitoring active") with pulsing `.online-dot`.

---

### File 21: `frontend/src/pages/Dashboard.jsx`
* **Relative Path**: `frontend/src/pages/Dashboard.jsx`
* **What the file does**:
  Executive central command view consolidating real-time risk statistics, a preview shortcut to the live GIS map, a summary card for the highest-risk simulated physical sensor, live meteorological widgets across 5 Nilgiris taluks, and a sensor status overview list.

```jsx

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
} from "lucide-react";

function Dashboard() {
  const [sensors, setSensors] = useState([]);
  const [weatherLocations, setWeatherLocations] = useState([]);
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [weatherLoading, setWeatherLoading] = useState(true);
  const [weatherError, setWeatherError] = useState("");

  // Load simulated sensor-risk data.
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
          setLoading(false);
        }
      } catch (error) {
        console.error("Dashboard risk loading error:", error);

        if (active) setLoading(false);
      }
    };

    fetchRiskData();
    const interval = setInterval(fetchRiskData, 5000);

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
        const response = await fetch(
          "http://127.0.0.1:8000/api/locations"
        );

        if (!response.ok) {
          throw new Error("Could not load monitoring locations");
        }

        const data = await response.json();

        if (active) {
          setLocations(data.locations || []);
        }
      } catch (error) {
        console.error("Location loading error:", error);
      }
    };

    fetchLocations();

    return () => {
      active = false;
    };
  }, []);

  // Load weather API readings for the weather-monitored areas.
  useEffect(() => {
    let active = true;

    const fetchWeather = async () => {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/api/weather-risk"
        );

        if (!response.ok) {
          throw new Error("Could not load weather data");
        }

        const data = await response.json();

        if (active) {
          setWeatherLocations(data.locations || []);
          setWeatherError("");
          setWeatherLoading(false);
        }
      } catch (error) {
        console.error("Weather loading error:", error);

        if (active) {
          setWeatherError(
            "Weather data could not be loaded. Check the backend and internet connection."
          );
          setWeatherLoading(false);
        }
      }
    };

    fetchWeather();

    // Refresh weather every minute.
    const interval = setInterval(fetchWeather, 60000);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  // Calculate sensor dashboard values.
  const highestScore =
    sensors.length > 0
      ? Math.max(...sensors.map((sensor) => sensor.risk_score))
      : 0;

  const highestRiskSensor =
    sensors.length > 0
      ? sensors.reduce((highest, sensor) =>
          sensor.risk_score > highest.risk_score ? sensor : highest
        )
      : null;

  const averageScore =
    sensors.length > 0
      ? Math.round(
          sensors.reduce(
            (total, sensor) => total + sensor.risk_score,
            0
          ) / sensors.length
        )
      : 0;

  const highRiskSensors = sensors.filter(
    (sensor) =>
      sensor.risk_level === "HIGH" ||
      sensor.risk_level === "CRITICAL"
  ).length;

  let overallRisk = "LOW";

  if (highestScore >= 75) {
    overallRisk = "CRITICAL";
  } else if (highestScore >= 50) {
    overallRisk = "HIGH";
  } else if (highestScore >= 25) {
    overallRisk = "MEDIUM";
  }

  // Match sensor IDs to their configured names.
  const getSensorLocationName = (sensor) => {
    const location = locations.find(
      (item) => item.sensor_id === sensor.sensor_id
    );

    return location?.name || `Simulated demo location (${sensor.sensor_id})`;
  };

  const formatValue = (value, unit = "") => {
    return value === null || value === undefined
      ? "N/A"
      : `${value}${unit}`;
  };

  const formatObservedTime = (time) => {
    if (!time) return "Time unavailable";

    // Open-Meteo usually returns a local timestamp without a timezone.
    return time.replace("T", " ");
  };

  return (
    <div className="page">
      <div className="page-heading">
        <h1>Dashboard</h1>
        <p>
          Landslide monitoring and weather conditions across Nilgiris District
        </p>
      </div>

      {/* Main statistics */}
      <div className="dashboard-cards">
        <div className="stat-card">
          <div className="stat-icon">
            <ShieldAlert size={20} />
          </div>
          <div>
            <span className="stat-label">Overall Sensor Risk</span>
            <div className="stat-value">
              {loading ? "..." : overallRisk}
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <RadioTower size={20} />
          </div>
          <div>
            <span className="stat-label">Simulated Sensors</span>
            <div className="stat-value">
              {loading ? "..." : sensors.length}
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <Activity size={20} />
          </div>
          <div>
            <span className="stat-label">Average Sensor Risk Score</span>
            <div className="stat-value">
              {loading ? "..." : `${averageScore}/100`}
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <AlertTriangle size={20} />
          </div>
          <div>
            <span className="stat-label">High/Critical Sensors</span>
            <div className="stat-value">
              {loading ? "..." : highRiskSensors}
            </div>
          </div>
        </div>
      </div>

      {/* Main dashboard sections */}
      <div className="dashboard-grid">
        <div className="dashboard-section">
          <div className="section-header">
            <div>
              <h2>Live GIS Monitoring</h2>
              <p>Susceptibility raster and monitoring locations</p>
            </div>
            <Map size={20} />
          </div>

          <div className="map-placeholder">
            <Map size={40} />
            <strong>Live GIS Map</strong>
            <span>
              View named weather locations and sensor risk markers on the GIS
              page.
            </span>
            <a href="/gis">Open Live GIS</a>
          </div>
        </div>

        <div className="dashboard-section">
          <div className="section-header">
            <div>
              <h2>Risk Summary</h2>
              <p>Highest-risk simulated sensor</p>
            </div>
            <BrainCircuit size={20} />
          </div>

          {highestRiskSensor ? (
            <div className="risk-summary">
              <div className="risk-summary-row">
                <span>Location</span>
                <strong>
                  {getSensorLocationName(highestRiskSensor)}
                </strong>
              </div>

              <div className="risk-summary-row">
                <span>Sensor ID</span>
                <strong>{highestRiskSensor.sensor_id}</strong>
              </div>

              <div className="risk-summary-row">
                <span>Risk Level</span>
                <strong>{highestRiskSensor.risk_level}</strong>
              </div>

              <div className="risk-summary-row">
                <span>Risk Score</span>
                <strong>{highestRiskSensor.risk_score}/100</strong>
              </div>

              <div className="risk-summary-row">
                <span>Rainfall</span>
                <strong>
                  {formatValue(highestRiskSensor.readings?.rainfall, " mm")}
                </strong>
              </div>

              <div className="risk-summary-row">
                <span>Soil Moisture</span>
                <strong>
                  {formatValue(
                    highestRiskSensor.readings?.soil_moisture,
                    "%"
                  )}
                </strong>
              </div>

              <div className="risk-summary-row">
                <span>Ground Tilt</span>
                <strong>
                  {formatValue(highestRiskSensor.readings?.tilt, "°")}
                </strong>
              </div>
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
      <div className="dashboard-section weather-section">
        <div className="section-header">
          <div>
            <h2>Weather Monitoring by Location</h2>
            <p>
              Current weather values supplied by the weather API
            </p>
          </div>
          <CloudRain size={20} />
        </div>

        {weatherLoading ? (
          <div className="alert-empty">Loading weather data...</div>
        ) : weatherError ? (
          <div className="alert-empty">{weatherError}</div>
        ) : weatherLocations.length === 0 ? (
          <div className="alert-empty">
            No weather locations were returned by the backend.
          </div>
        ) : (
          <div className="weather-location-grid">
            {weatherLocations.map((location) => {
              const weather = location.weather;
              const readings = weather?.readings;
              const weatherRisk = location.weather_risk;

              return (
                <div
                  className="weather-location-card"
                  key={location.location_id}
                >
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
                      <span className="weather-location-id">
                        {location.location_id} · Weather API
                      </span>
                    </div>
                    <CloudRain size={21} />
                  </div>

                  {weather?.available && readings ? (
                    <>
                      <div className="weather-primary-value">
                        <Thermometer size={20} />
                        <strong>
                          {formatValue(readings.temperature_c, " °C")}
                        </strong>
                        <span>Temperature</span>
                      </div>

                      <div className="weather-readings">
                        <div>
                          <Droplets size={16} />
                          <span>Humidity</span>
                          <strong>
                            {formatValue(readings.humidity_percent, "%")}
                          </strong>
                        </div>

                        <div>
                          <CloudRain size={16} />
                          <span>Rain</span>
                          <strong>
                            {formatValue(readings.rain_mm, " mm")}
                          </strong>
                        </div>

                        <div>
                          <CloudRain size={16} />
                          <span>Precipitation</span>
                          <strong>
                            {formatValue(readings.precipitation_mm, " mm")}
                          </strong>
                        </div>

                        <div>
                          <Gauge size={16} />
                          <span>Surface Pressure</span>
                          <strong>
                            {formatValue(readings.pressure_hpa, " hPa")}
                          </strong>
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
                    <div className="weather-unavailable">
                      Weather data is currently unavailable for this location.
                    </div>
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
                        <strong>
                          {formatValue(readings?.precipitation_mm, " mm")}
                        </strong>
                      </div>
                    </div>

                    <span className="weather-risk-observed">
                      Observation time:{" "}
                      {formatObservedTime(
                        weatherRisk?.observed_at || weather?.observed_at
                      )}
                    </span>

                    <details className="weather-risk-explanation">
                      <summary>Why is the risk unassessed?</summary>
                      <div>
                        <p>
                          {weatherRisk?.reason ||
                            "A weather-based assessment could not be returned."}
                        </p>
                        <p>
                          Historical landslide event data and validated,
                          time-window-specific thresholds are unavailable.
                          Current weather readings alone cannot establish a
                          landslide risk category.
                        </p>
                        {weatherRisk?.method_description && (
                          <p>{weatherRisk.method_description}</p>
                        )}
                      </div>
                    </details>

                    <p className="weather-risk-disclaimer">
                      This is a preliminary screening prototype, not a trained
                      ML prediction or official warning.
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Simulated sensor overview */}
      <div className="dashboard-section">
        <div className="section-header">
          <div>
            <h2>Sensor Overview</h2>
            <p>
              Simulated sensor readings for the current software demo
            </p>
          </div>
          <RadioTower size={20} />
        </div>

        <div className="sensor-overview">
          {sensors.map((sensor) => (
            <div
              className="sensor-overview-item"
              key={sensor.sensor_id}
            >
              <div>
                <strong>{getSensorLocationName(sensor)}</strong>
                <span>
                  {sensor.sensor_id} · Risk score: {sensor.risk_score}
                </span>
              </div>

              <span
                className={`overview-risk ${(
                  sensor.risk_level || "LOW"
                ).toLowerCase()}`}
              >
                {sensor.risk_level}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
```

#### Detailed Code Explanation
* **Lines 28–60**: Polling effect invoking `/api/risk` every 5,000 milliseconds to refresh live sensor hazard metrics.
* **Lines 62–91**: Fetches metadata for monitoring locations from `/api/locations`.
* **Lines 93–135**: Queries Open-Meteo meteorological conditions and unvalidated screening heuristics from `/api/weather-risk` on a 60-second cycle.
* **Lines 137–175**: Derives aggregated state metrics: highest sensor risk score, identification of the highest-risk sensor node, mean hazard score, count of high/critical sensors, and composite system risk tier.
* **Lines 208–256**: Top four stat KPI cards presenting Overall Sensor Risk, Connected Sensors count, Average Risk Score, and Critical Sensors count.
* **Lines 259–344**: Two-column layout pairing a quick GIS launch preview card with a detailed breakdown of the highest-risk sensor (location name, rainfall, soil moisture, and ground tilt).
* **Lines 347–524**: Grid of weather location cards detailing ambient temperature, humidity %, current rainfall, precipitation accumulation, atmospheric pressure, and the weather screening status note.
* **Lines 527–562**: Sensor overview list color-coding each individual sensor node by its current operational risk classification.

---

### File 22: `frontend/src/pages/MLPrediction.jsx`
* **Relative Path**: `frontend/src/pages/MLPrediction.jsx`
* **What the file does**:
  Interactive geotechnical simulation tool allowing researchers and engineers to input 7 terrain and environmental parameters, submit them to the FastAPI ML backend, and receive instant Random Forest susceptibility predictions with probability scores and risk tiers.

```jsx
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
```

#### Detailed Code Explanation
* **Lines 17–28**: Form state capturing the 7 geotechnical inputs initialized to empty strings; manages `result` payload and `loading` boolean spinner state.
* **Lines 30–73**: Field descriptor array binding input keys to human-readable labels, placeholders, and Lucide icons.
* **Lines 82–121**: `handleSubmit` function: cancels native submit event, casts form inputs to numeric floats, and issues a POST request to `http://127.0.0.1:8000/api/predict`. On response, populates `result`.
* **Lines 159–209**: Form layout presenting 7 distinct numeric inputs arranged in a responsive 2-column grid.
* **Lines 213–259**: Output card rendering binary prediction result (Landslide vs Non-Landslide), calculated percentage probability (e.g., $84.25\%$), and mapped risk level (`HIGH`, `MEDIUM`, or `LOW`).

---

### File 23: `frontend/src/pages/Sensors.jsx`
* **Relative Path**: `frontend/src/pages/Sensors.jsx`
* **What the file does**:
  Dedicated geotechnical IoT telemetry monitoring console displaying status cards for each active physical sensor station (Ooty S001, S002, S003), highlighting live readings for precipitation, soil moisture, temperature, humidity, barometric pressure, and ground tilt angle.

```jsx
import { useEffect, useState } from "react";

import {
  RadioTower,
  CloudRain,
  Droplets,
  Thermometer,
  Wind,
  Gauge,
  Activity,
  ShieldAlert,
} from "lucide-react";


function Sensors() {

  const [sensors, setSensors] = useState([]);

  const [loading, setLoading] = useState(true);


  useEffect(() => {

  const fetchRiskData = () => {

    fetch("http://127.0.0.1:8000/api/risk")

      .then((response) => response.json())

      .then((data) => {

        setSensors(data.sensors);

        setLoading(false);

      })

      .catch((error) => {

        console.error(
          "Risk data loading error:",
          error
        );

        setLoading(false);

      });

  };


  // Get data immediately
  fetchRiskData();


  // Refresh every 5 seconds
  const interval = setInterval(
    fetchRiskData,
    5000
  );


  // Stop the timer when leaving the page
  return () => {
    clearInterval(interval);
  };

}, []);


  return (

    <div className="page">

      <div className="page-heading">

        <h1>Sensors</h1>

        <p>
          Real-time environmental monitoring
          and landslide risk
        </p>

      </div>


      {/* Sensor summary */}

      <div className="dashboard-cards">

        <div className="stat-card">

          <div className="stat-icon">

            <RadioTower size={20} />

          </div>

          <div>

            <span className="stat-label">
              Connected Sensors
            </span>

            <div className="stat-value">
              {sensors.length}
            </div>

          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon">

            <ShieldAlert size={20} />

          </div>

          <div>

            <span className="stat-label">
              Monitoring
            </span>

            <div className="stat-value">
              Active
            </div>

          </div>

        </div>

      </div>


      {/* Sensor cards */}

      {loading ? (

        <div className="dashboard-section">

          <p>Loading sensor data...</p>

        </div>

      ) : (

        <div className="sensor-grid">

          {sensors.map((sensor) => (

            <div
              className="sensor-card"
              key={sensor.sensor_id}
            >

              {/* Header */}

              <div className="sensor-card-header">

                <div>

                  <h3>
                    {sensor.sensor_id}
                  </h3>

                  <span>
                    Sensor Active
                  </span>

                </div>

                <div className="sensor-status-dot"></div>

              </div>


              {/* Risk */}

              <div className="sensor-risk">

                <div>

                  <span>
                    Current Risk
                  </span>

                  <strong>
                    {sensor.risk_level}
                  </strong>

                </div>

                <div className="risk-score">

                  {sensor.risk_score}

                </div>

              </div>


              {/* Location */}

              <div className="sensor-location">

                Location:

                {" "}

                {sensor.location.latitude.toFixed(4)}

                ,

                {" "}

                {sensor.location.longitude.toFixed(4)}

              </div>


              {/* Readings */}

              <div className="sensor-readings">


                <div className="sensor-reading">

                  <CloudRain size={18} />

                  <div>

                    <span>
                      Rainfall
                    </span>

                    <strong>
                      {sensor.readings.rainfall} mm
                    </strong>

                  </div>

                </div>


                <div className="sensor-reading">

                  <Droplets size={18} />

                  <div>

                    <span>
                      Soil Moisture
                    </span>

                    <strong>
                      {sensor.readings.soil_moisture}%
                    </strong>

                  </div>

                </div>


                <div className="sensor-reading">

                  <Thermometer size={18} />

                  <div>

                    <span>
                      Temperature
                    </span>

                    <strong>
                      {sensor.readings.temperature} °C
                    </strong>

                  </div>

                </div>


                <div className="sensor-reading">

                  <Wind size={18} />

                  <div>

                    <span>
                      Humidity
                    </span>

                    <strong>
                      {sensor.readings.humidity}%
                    </strong>

                  </div>

                </div>


                <div className="sensor-reading">

                  <Gauge size={18} />

                  <div>

                    <span>
                      Pressure
                    </span>

                    <strong>
                      {sensor.readings.pressure} hPa
                    </strong>

                  </div>

                </div>


                <div className="sensor-reading">

                  <Activity size={18} />

                  <div>

                    <span>
                      Tilt
                    </span>

                    <strong>
                      {sensor.readings.tilt}°
                    </strong>

                  </div>

                </div>


              </div>

            </div>

          ))}

        </div>

      )}

    </div>

  );

}


export default Sensors;
```

#### Detailed Code Explanation
* **Lines 17–68**: Manages local state `sensors` and `loading`. Initiates an immediate fetch to `/api/risk` and sets up a 5-second `setInterval` timer, cleaning up on component unmount.
* **Lines 89–136**: KPI statistics cards displaying active sensor counts and real-time operational readiness.
* **Lines 151–350**: Sensor grid rendering an individual card for each station (`S001`, `S002`, `S003`):
  * Header with active pulse dot indicator.
  * Risk level badge and composite score (0–100).
  * 4-decimal geographic coordinates (Latitude, Longitude).
  * 6 physical parameter tiles with distinct icons: Rainfall (mm), Soil Moisture (%), Temperature (°C), Humidity (%), Surface Pressure (hPa), and Ground Inclinometer Tilt (°).

---

### File 24: `frontend/src/pages/Alerts.jsx`
* **Relative Path**: `frontend/src/pages/Alerts.jsx`
* **What the file does**:
  Emergency management alert feed that evaluates simulated sensor telemetry against high-risk and critical hazard thresholds, presents live notifications with location names, and details the contributing physical factors.

```jsx

import { useEffect, useState } from "react";

import {
  BellRing,
  ShieldAlert,
  TriangleAlert,
  CheckCircle2,
  RadioTower,
  MapPin,
} from "lucide-react";

function Alerts() {
  const [sensors, setSensors] = useState([]);
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
          setLocations(locationData.locations || []);
          setError("");
          setLoading(false);
        }
      } catch (err) {
        console.error("Alert loading error:", err);

        if (active) {
          setError("Unable to load alerts. Check that the backend is running.");
          setLoading(false);
        }
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  // Find the location name for each sensor.
  const getLocationName = (sensor) => {
    const matchingLocation = locations.find(
      (location) => location.sensor_id === sensor.sensor_id
    );

    if (matchingLocation) {
      return matchingLocation.name;
    }

    // These are demo sensors, not confirmed physical installations.
    if (sensor.sensor_id === "S002") {
      return "Ooty region - Simulated Sensor 2";
    }

    if (sensor.sensor_id === "S003") {
      return "Ooty region - Simulated Sensor 3";
    }

    return "Location not configured";
  };

  const highRiskSensors = sensors.filter(
    (sensor) => sensor.risk_level === "HIGH"
  );

  const criticalSensors = sensors.filter(
    (sensor) => sensor.risk_level === "CRITICAL"
  );

  const totalAlerts =
    highRiskSensors.length + criticalSensors.length;

  const alertSensors = [...criticalSensors, ...highRiskSensors];

  return (
    <div className="page">
      <div className="page-heading">
        <h1>Alerts</h1>
        <p>
          Landslide risk alerts with named monitoring locations
        </p>
      </div>

      <div className="dashboard-cards">
        <div className="stat-card">
          <div className="stat-icon">
            <BellRing size={20} />
          </div>
          <div>
            <span className="stat-label">Active Alerts</span>
            <div className="stat-value">
              {loading ? "..." : totalAlerts}
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <ShieldAlert size={20} />
          </div>
          <div>
            <span className="stat-label">Critical</span>
            <div className="stat-value">
              {loading ? "..." : criticalSensors.length}
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <TriangleAlert size={20} />
          </div>
          <div>
            <span className="stat-label">High Risk</span>
            <div className="stat-value">
              {loading ? "..." : highRiskSensors.length}
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <RadioTower size={20} />
          </div>
          <div>
            <span className="stat-label">Sensors Monitored</span>
            <div className="stat-value">
              {loading ? "..." : sensors.length}
            </div>
          </div>
        </div>
      </div>

      <div className="dashboard-section">
        <div className="section-header">
          <div>
            <h2>Current Alerts</h2>
            <p>
              Alerts generated from the current sensor risk calculations
            </p>
          </div>
          <BellRing size={20} />
        </div>

        {loading ? (
          <div className="alert-empty">
            Loading alert data...
          </div>
        ) : error ? (
          <div className="alert-empty">
            {error}
          </div>
        ) : totalAlerts === 0 ? (
          <div className="alert-empty">
            <CheckCircle2 size={28} />
            <strong>No Active Alerts</strong>
            <span>
              No simulated sensor currently meets the high-risk
              alert threshold.
            </span>
          </div>
        ) : (
          <div className="alert-list">
            {alertSensors.map((sensor) => {
              const isCritical = sensor.risk_level === "CRITICAL";
              const placeName = getLocationName(sensor);

              return (
                <div
                  className={`alert-item ${sensor.risk_level.toLowerCase()}`}
                  key={sensor.sensor_id}
                >
                  <div className="alert-icon">
                    {isCritical ? (
                      <ShieldAlert size={22} />
                    ) : (
                      <TriangleAlert size={22} />
                    )}
                  </div>

                  <div className="alert-content">
                    <div className="alert-title-row">
                      <strong>
                        {isCritical
                          ? "Critical Landslide Risk"
                          : "High Landslide Risk"}
                      </strong>
                      <span className="alert-time">Live demo</span>
                    </div>

                    <p>
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
                      Sensor ID: <strong>{sensor.sensor_id}</strong>
                      {" "}is reporting a{" "}
                      {sensor.risk_level.toLowerCase()} risk condition.
                    </p>

                    <div className="alert-details">
                      <span>
                        Risk Score:{" "}
                        <strong>{sensor.risk_score}/100</strong>
                      </span>

                      <span>
                        Rainfall:{" "}
                        <strong>{sensor.readings.rainfall} mm</strong>
                      </span>

                      <span>
                        Soil Moisture:{" "}
                        <strong>
                          {sensor.readings.soil_moisture}%
                        </strong>
                      </span>

                      <span>
                        Tilt:{" "}
                        <strong>{sensor.readings.tilt}°</strong>
                      </span>
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
```

#### Detailed Code Explanation
* **Lines 19–59**: Concurrently issues requests to `/api/risk` and `/api/locations` using `Promise.all` with a 5-second recurring polling cycle.
* **Lines 62–81**: Maps sensor identifiers to named geographical entities (e.g., `S001` to Ooty).
* **Lines 83–94**: Segregates sensor array into `highRiskSensors` and `criticalSensors`, sorting critical alerts to the top of the feed.
* **Lines 105–153**: Metrics summary bar highlighting Active Alerts, Critical Alerts count, High Risk count, and Monitored Nodes count.
* **Lines 175–183**: Green empty state ("No Active Alerts") displayed when no sensor exceeds threshold values.
* **Lines 184–257**: Formatted alert cards color-coded with red (critical) or orange (high risk) borders displaying location names, sensor identifiers, hazard scores, rainfall, soil moisture, and tilt readings.

---

### File 25: `frontend/src/pages/History.jsx`
* **Relative Path**: `frontend/src/pages/History.jsx`
* **What the file does**:
  Newly implemented historical sensor telemetry and risk archival interface. Captures periodic 5-second sensor hazard events, maintains an in-browser sliding buffer of up to 500 records via `localStorage`, provides multi-tier risk filtering, and displays a comprehensive chronological data table.

```jsx

import { useEffect, useMemo, useState } from "react";
import {
  History as HistoryIcon,
  RefreshCw,
  Trash2,
  AlertTriangle,
} from "lucide-react";

const API_URL = "http://127.0.0.1:8000/api/risk";
const STORAGE_KEY = "landslide-risk-history";

function History() {
  const [records, setRecords] = useState(() => {
    try {
      return JSON.parse(
        localStorage.getItem(STORAGE_KEY) || "[]"
      );
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
        }));

        setRecords((previous) => {
          const updated = [...newRecords, ...previous].slice(
            0,
            500
          );

          try {
            localStorage.setItem(
              STORAGE_KEY,
              JSON.stringify(updated)
            );
          } catch (storageError) {
            console.error(
              "Could not save history:",
              storageError
            );
          }

          return updated;
        });

        setError("");
      } catch (err) {
        if (active) {
          setError(
            "Could not load history. Check that your backend is running."
          );
          console.error("History loading error:", err);
        }
      } finally {
        if (active) setLoading(false);
      }
    };

    fetchHistory();

    const interval = setInterval(fetchHistory, 5000);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  const filteredRecords = useMemo(() => {
    if (filter === "ALL") return records;

    return records.filter(
      (record) =>
        record.risk_level.toUpperCase() === filter
    );
  }, [records, filter]);

  const formatDate = (value) => {
    return new Date(value).toLocaleString();
  };

  const clearHistory = () => {
    const confirmed = window.confirm(
      "Are you sure you want to clear all saved history?"
    );

    if (!confirmed) return;

    localStorage.removeItem(STORAGE_KEY);
    setRecords([]);
  };

  const riskClass = (level) => {
    const value = (level || "UNKNOWN").toLowerCase();

    if (value.includes("high")) return "high";
    if (value.includes("medium")) return "medium";
    if (value.includes("low")) return "low";

    return "unknown";
  };

  return (
    <div className="page">
      <div className="page-heading">
        <h1>Risk History</h1>
        <p>
          Historical sensor readings and landslide risk records
        </p>
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
                  record.risk_level
                    .toUpperCase()
                    .includes("HIGH")
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
            <span className="stat-label">Refresh Interval</span>
            <h2>5 seconds</h2>
          </div>
        </div>
      </div>

      <div className="history-panel">
        <div className="history-toolbar">
          <div>
            <h2>Recorded Events</h2>
            <p>Newest records appear first.</p>
          </div>

          <div className="history-actions">
            <select
              value={filter}
              onChange={(event) => setFilter(event.target.value)}
              aria-label="Filter by risk level"
            >
              <option value="ALL">All Risk Levels</option>
              <option value="HIGH">High Risk</option>
              <option value="MEDIUM">Medium Risk</option>
              <option value="LOW">Low Risk</option>
            </select>

            <button
              type="button"
              onClick={clearHistory}
              disabled={records.length === 0}
            >
              <Trash2 size={16} />
              Clear History
            </button>
          </div>
        </div>

        {loading && records.length === 0 && (
          <p className="history-message">
            Loading risk history...
          </p>
        )}

        {error && (
          <p className="history-error">{error}</p>
        )}

        {!loading && records.length === 0 && !error && (
          <p className="history-message">
            No history recorded yet. Records will appear when
            sensor-risk data is received.
          </p>
        )}

        {records.length > 0 && filteredRecords.length === 0 && (
          <p className="history-message">
            No records found for this risk level.
          </p>
        )}

        {filteredRecords.length > 0 && (
          <div className="history-table-wrapper">
            <table className="history-table">
              <thead>
                <tr>
                  <th>Recorded At</th>
                  <th>Sensor ID</th>
                  <th>Location</th>
                  <th>Risk Level</th>
                  <th>Risk Score</th>
                  <th>Rainfall (mm)</th>
                  <th>Soil Moisture (%)</th>
                  <th>Tilt (°)</th>
                </tr>
              </thead>

              <tbody>
                {filteredRecords.map((record) => (
                  <tr key={record.id}>
                    <td>{formatDate(record.timestamp)}</td>
                    <td>{record.sensor_id}</td>
                    <td>
                      {typeof record.location === "object" && record.location !== null
                        ? `${record.location.latitude}, ${record.location.longitude}`
                        : record.location ?? "Unknown"}
                    </td>
                    <td>
                      <span
                        className={`history-risk ${riskClass(
                          record.risk_level
                        )}`}
                      >
                        {record.risk_level}
                      </span>
                    </td>
                    <td>
                      {record.risk_score ?? "N/A"}
                    </td>
                    <td>
                      {record.readings.rainfall ?? "N/A"}
                    </td>
                    <td>
                      {record.readings.soil_moisture ?? "N/A"}
                    </td>
                    <td>
                      {record.readings.tilt ?? "N/A"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default History;
```

#### Detailed Code Explanation
* **Lines 14–22**: Lazy state initializer reading previous event logs from `window.localStorage` under key `"landslide-risk-history"`.
* **Lines 28–98**: Polling cycle: every 5 seconds, queries `http://127.0.0.1:8000/api/risk`, creates unique records prefixed with ISO timestamps, and prepends them to state while slicing to a maximum buffer of 500 entries. Writes back to `localStorage`.
* **Lines 100–107**: `useMemo` computation dynamically filtering stored records based on selected dropdown value (`ALL`, `HIGH`, `MEDIUM`, `LOW`).
* **Lines 113–122**: `clearHistory()` function resetting both React state and browser `localStorage` upon explicit user confirmation.
* **Lines 143–181**: KPI metrics bar displaying Total Saved Records, High-Risk Events count, and Polling Frequency (5s).
* **Lines 237–287**: Chronological historical table detailing ISO Timestamp, Station ID, Geo Coordinates, Risk Badge, Score (0–100), Rainfall (mm), Soil Moisture (%), and Inclinometer Tilt (°).

---

> **Proceed to Part 3**:  
> For the complete source code and line explanations of the GIS Leaflet Engine (`GIS.jsx`), complete design system stylesheets (`App.css`, `index.css`), and SVG assets, see **[LANDSLIDE_DOCUMENTATION_PART3.md](file:///d:/Landslide-Early-Warning-System/LANDSLIDE_DOCUMENTATION_PART3.md)**.
