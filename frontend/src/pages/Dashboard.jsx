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
