# app/routes/sensor_routes.py

from flask import Blueprint, request, jsonify
from app.utils.calculator import energy_to_carbon_direct
from app.utils.anomaly import run_anomaly_check
from app.database.db_operations import (
    save_reading,
    get_last_n_readings,
    save_anomaly
)
from datetime import datetime

sensor_bp = Blueprint("sensor", __name__)


@sensor_bp.route("/api/sensor/data", methods=["POST"])
def receive_data():

    data = request.get_json()

    # Validate fields
    power_kw     = data.get("power_kw")
    time_seconds = data.get("time_seconds")
    co2_ppm      = data.get("co2_ppm")
    temperature  = data.get("temperature")
    device_id    = data.get("device_id")

    if power_kw is None or time_seconds is None:
        return jsonify({
            "error": "Missing power_kw or time_seconds"
        }), 400

    # Calculate carbon
    result = energy_to_carbon_direct(power_kw, time_seconds)

    # Build full reading
    reading = {
        "device_id":   device_id or "ESP32_001",
        "power_kw":    power_kw,
        "energy_kwh":  result["energy_kwh"],
        "carbon_kg":   result["carbon_kg"],
        "co2_ppm":     co2_ppm or 0,
        "temperature": temperature or 0,
        "timestamp":   datetime.now()
    }

    # Save to database
    reading_id = save_reading(reading)

    # Check for anomaly
    history = get_last_n_readings(device_id or "ESP32_001", 20)
    history_power = [r["power_kw"] for r in history]

    anomaly_result = run_anomaly_check(reading, history_power)

    # Save anomaly if detected
    if anomaly_result["is_anomaly"]:
        zscore = anomaly_result["zscore_result"]
        save_anomaly(
            device_id    = device_id or "ESP32_001",
            reading_id   = reading_id,
            anomaly_type = "spike",
            severity     = zscore.get("severity", "medium"),
            message      = zscore.get("message", "Anomaly detected")
        )

    return jsonify({
        "status":       "success",
        "reading_id":   reading_id,
        "carbon_kg":    result["carbon_kg"],
        "energy_kwh":   result["energy_kwh"],
        "anomaly":      anomaly_result["is_anomaly"]
    }), 200