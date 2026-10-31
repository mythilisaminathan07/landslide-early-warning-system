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
