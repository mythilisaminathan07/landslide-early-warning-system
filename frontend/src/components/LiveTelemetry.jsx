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