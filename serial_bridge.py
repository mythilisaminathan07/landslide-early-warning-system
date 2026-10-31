
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
