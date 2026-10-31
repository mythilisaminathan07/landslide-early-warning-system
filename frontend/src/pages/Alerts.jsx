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