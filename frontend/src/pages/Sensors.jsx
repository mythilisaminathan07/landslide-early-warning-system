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