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
