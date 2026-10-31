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
