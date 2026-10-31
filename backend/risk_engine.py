"""
================================================================================
SLOPEGUARD AI - RISK SCORING WEIGHTS & THRESHOLDS (MAX 100 POINTS)
================================================================================
Factor                  Max Pts   Thresholds & Points Allocation
--------------------------------------------------------------------------------
Soil Moisture (%)       35 pts    >= 85%  -> 35 pts  (Extreme saturation)
                                  >= 70%  -> 25 pts  (High saturation)
                                  >= 50%  -> 15 pts  (Moderate moisture)
                                  >= 30%  ->  5 pts  (Low-medium moisture)
                                  < 30%   ->  0 pts  (Dry)

Tilt Change (deg)       25 pts    >= 15.0° -> 25 pts (Severe slope displacement)
(from baseline)                   >=  8.0° -> 18 pts (Significant slope tilt)
                                  >=  4.0° -> 10 pts (Moderate tilt shift)
                                  >=  1.5° ->  5 pts (Minor tilt detected)
                                  <   1.5° ->  0 pts (Normal resting orientation)

Motion                  25 pts    Split between Accel Deviation (12) & Gyro (13):
 - Accel Dev (|mag-9.81|) 12 pts  >= 2.5 m/s²  -> 12 pts (Vigorous acceleration)
                                  >= 1.5 m/s²  ->  8 pts (Moderate vibration)
                                  >= 0.5 m/s²  ->  4 pts (Minor vibration)
                                  <  0.5 m/s²  ->  0 pts (Static)
 - Gyro Mag (deg/s)       13 pts  >= 15.0 deg/s -> 13 pts (Fast angular rotation)
                                  >=  8.0 deg/s ->  8 pts (Moderate rotation)
                                  >=  2.0 deg/s ->  4 pts (Minor rotation)
                                  <   2.0 deg/s ->  0 pts (Stationary)

Rain Detected           15 pts    True  -> 15 pts (Digital precipitation trigger)
                                  False ->  0 pts
                                  *Note: Rain alone yields 15 pts, remaining in LOW tier (<25)
--------------------------------------------------------------------------------
TOTAL RISK TIERS:
  LOW      :   0 - 24 pts
  MEDIUM   :  25 - 49 pts
  HIGH     :  50 - 74 pts
  CRITICAL :  75 - 100 pts
================================================================================
PROTOTYPE DISCLAIMER:
These scoring thresholds and weights are preliminary prototype engineering values.
They are NOT calibrated or validated for official evacuation or life-safety warnings.
================================================================================
"""

from typing import Any, Dict, List, Optional


def calculate_risk(readings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate real-time landslide risk score (0-100) and risk tier
    from hardware telemetry (soil moisture %, tilt change, motion, rain detected).
    
    If legacy simulator readings (rainfall mm, humidity, pressure) are passed,
    it falls back gracefully to simulated evaluation.
    """
    # Detect if this is real hardware node reading
    is_real_node = "rain_detected" in readings or "soil_raw" in readings or "tilt_change" in readings

    if is_real_node:
        return _calculate_real_sensor_risk(readings)
    else:
        return _calculate_legacy_simulator_risk(readings)


def _calculate_real_sensor_risk(readings: Dict[str, Any]) -> Dict[str, Any]:
    score = 0
    contributing_factors: List[str] = []
    factor_points: Dict[str, int] = {
        "soil_moisture": 0,
        "tilt_change": 0,
        "motion": 0,
        "rain_detected": 0,
    }

    # 1. Soil Moisture % (up to 35 pts)
    soil_pct = readings.get("soil_moisture")
    if soil_pct is not None:
        soil_val = float(soil_pct)
        if soil_val >= 85.0:
            pts = 35
            reason = f"Extreme soil saturation ({soil_val}% >= 85%)"
        elif soil_val >= 70.0:
            pts = 25
            reason = f"High soil saturation ({soil_val}% >= 70%)"
        elif soil_val >= 50.0:
            pts = 15
            reason = f"Moderate soil moisture ({soil_val}% >= 50%)"
        elif soil_val >= 30.0:
            pts = 5
            reason = f"Low soil moisture ({soil_val}% >= 30%)"
        else:
            pts = 0
            reason = ""

        if pts > 0:
            score += pts
            factor_points["soil_moisture"] = pts
            contributing_factors.append(f"{reason} (+{pts} pts)")

    # 2. Tilt Change from Baseline (up to 25 pts)
    tilt_change = readings.get("tilt_change")
    if tilt_change is not None:
        tc_val = float(tilt_change)
        if tc_val >= 15.0:
            pts = 25
            reason = f"Severe slope displacement ({tc_val}° change >= 15°)"
        elif tc_val >= 8.0:
            pts = 18
            reason = f"Significant slope tilt ({tc_val}° change >= 8°)"
        elif tc_val >= 4.0:
            pts = 10
            reason = f"Moderate tilt shift ({tc_val}° change >= 4°)"
        elif tc_val >= 1.5:
            pts = 5
            reason = f"Minor slope tilt ({tc_val}° change >= 1.5°)"
        else:
            pts = 0
            reason = ""

        if pts > 0:
            score += pts
            factor_points["tilt_change"] = pts
            contributing_factors.append(f"{reason} (+{pts} pts)")
    elif readings.get("mpu_available") is False or readings.get("mpu_valid") is False:
        # Note MPU unavailability if relevant
        contributing_factors.append("Tilt data unavailable (MPU invalid / disabled)")

    # 3. Motion: Accel Deviation (up to 12 pts) + Gyro Magnitude (up to 13 pts) = max 25 pts
    mot_accel = readings.get("motion_accel")
    mot_gyro = readings.get("motion_gyro")
    motion_pts = 0
    motion_reasons = []

    if mot_accel is not None:
        acc_val = float(mot_accel)
        if acc_val >= 2.5:
            p_acc = 12
            motion_reasons.append(f"Vigorous acceleration ({acc_val} m/s²)")
        elif acc_val >= 1.5:
            p_acc = 8
            motion_reasons.append(f"Moderate acceleration ({acc_val} m/s²)")
        elif acc_val >= 0.5:
            p_acc = 4
            motion_reasons.append(f"Minor vibration ({acc_val} m/s²)")
        else:
            p_acc = 0
        motion_pts += p_acc

    if mot_gyro is not None:
        gyr_val = float(mot_gyro)
        if gyr_val >= 15.0:
            p_gyr = 13
            motion_reasons.append(f"Fast angular rotation ({gyr_val} deg/s)")
        elif gyr_val >= 8.0:
            p_gyr = 8
            motion_reasons.append(f"Moderate rotation ({gyr_val} deg/s)")
        elif gyr_val >= 2.0:
            p_gyr = 4
            motion_reasons.append(f"Minor rotation ({gyr_val} deg/s)")
        else:
            p_gyr = 0
        motion_pts += p_gyr

    if motion_pts > 0:
        score += motion_pts
        factor_points["motion"] = motion_pts
        contributing_factors.append(f"Motion detected: {', '.join(motion_reasons)} (+{motion_pts} pts)")

    # 4. Rain Detected (up to 15 pts)
    # Binary sensor: rain alone yields 15 pts, which keeps it within LOW tier (<25)
    rain = readings.get("rain_detected", False)
    if rain is True or str(rain).lower() in ("true", "1"):
        score += 15
        factor_points["rain_detected"] = 15
        contributing_factors.append("Active rain detected (+15 pts)")

    # Clamp total score to [0, 100]
    score = max(0, min(100, score))

    # Determine risk tier
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
        "risk_level": risk_level,
        "contributing_factors": contributing_factors,
        "factor_points": factor_points,
    }


def _calculate_legacy_simulator_risk(readings: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback scorer for simulated demo data when USE_SIMULATOR=True."""
    rainfall = readings.get("rainfall", 0)
    soil_moisture = readings.get("soil_moisture", 0)
    humidity = readings.get("humidity", 0)
    tilt = readings.get("tilt", 0)
    pressure = readings.get("pressure", 1013)

    score = 0
    factors = []

    if rainfall >= 100:
        score += 30
        factors.append(f"Extreme simulated rainfall ({rainfall} mm)")
    elif rainfall >= 70:
        score += 20
        factors.append(f"Heavy simulated rainfall ({rainfall} mm)")
    elif rainfall >= 40:
        score += 10
        factors.append(f"Moderate simulated rainfall ({rainfall} mm)")

    if soil_moisture >= 80:
        score += 25
        factors.append(f"High simulated soil moisture ({soil_moisture}%)")
    elif soil_moisture >= 65:
        score += 15
        factors.append(f"Moderate simulated soil moisture ({soil_moisture}%)")
    elif soil_moisture >= 50:
        score += 8

    if humidity >= 90:
        score += 15
    elif humidity >= 80:
        score += 10
    elif humidity >= 70:
        score += 5

    if tilt >= 6:
        score += 25
        factors.append(f"High tilt ({tilt}°)")
    elif tilt >= 3:
        score += 15
        factors.append(f"Moderate tilt ({tilt}°)")
    elif tilt >= 1:
        score += 5

    if pressure < 1000:
        score += 5

    score = min(100, score)

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
        "risk_level": risk_level,
        "contributing_factors": factors,
        "factor_points": {},
    }