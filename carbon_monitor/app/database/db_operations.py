# app/database/db_operations.py

from app.database.db_config import (
    sensor_readings,
    carbon_predictions,
    anomalies,
    recommendations,
    users
)
from datetime import datetime


# ─────────────────────────────────
# SENSOR READINGS
# ─────────────────────────────────

def save_reading(data):
    result = sensor_readings.insert_one(data)
    return str(result.inserted_id)


def get_latest_reading(device_id):
    return sensor_readings.find_one(
        {"device_id": device_id},
        sort=[("timestamp", -1)]
    )


def get_readings_by_range(device_id, start_date, end_date):
    return list(sensor_readings.find({
        "device_id": device_id,
        "timestamp": {
            "$gte": start_date,
            "$lte": end_date
        }
    }).sort("timestamp", 1))


def get_last_n_readings(device_id, n=24):
    # Used by LSTM — needs last n readings
    return list(sensor_readings.find(
        {"device_id": device_id}
    ).sort("timestamp", -1).limit(n))


def get_all_latest_readings():
    # For admin/analyst — latest per device
    pipeline = [
        {"$sort": {"timestamp": -1}},
        {"$group": {
            "_id": "$device_id",
            "latest": {"$first": "$$ROOT"}
        }}
    ]
    return list(sensor_readings.aggregate(pipeline))


# ─────────────────────────────────
# CARBON PREDICTIONS
# ─────────────────────────────────

def save_carbon_prediction(device_id, reading_id,
                           predicted_kg, model_used):
    carbon_predictions.insert_one({
        "device_id":    device_id,
        "reading_id":   reading_id,
        "predicted_kg": predicted_kg,
        "model_used":   model_used,
        "timestamp":    datetime.utcnow()
    })


def get_latest_prediction(device_id):
    return carbon_predictions.find_one(
        {"device_id": device_id},
        sort=[("timestamp", -1)]
    )


# ─────────────────────────────────
# ANOMALIES
# ─────────────────────────────────

def save_anomaly(device_id, reading_id,
                 anomaly_type, severity, message):
    anomalies.insert_one({
        "device_id":    device_id,
        "reading_id":   reading_id,
        "anomaly_type": anomaly_type,
        "severity":     severity,
        "message":      message,
        "is_resolved":  False,
        "detected_at":  datetime.utcnow()
    })


def get_anomalies(device_id=None, limit=20):
    query = {}
    if device_id:
        query["device_id"] = device_id
    return list(anomalies.find(
        query
    ).sort("detected_at", -1).limit(limit))


def resolve_anomaly(anomaly_id):
    from bson import ObjectId
    anomalies.update_one(
        {"_id": ObjectId(anomaly_id)},
        {"$set": {"is_resolved": True}}
    )


# ─────────────────────────────────
# RECOMMENDATIONS
# ─────────────────────────────────

def save_recommendation(device_id, suggestion,
                        saving_kg, priority, top_cause):
    recommendations.insert_one({
        "device_id":  device_id,
        "suggestion": suggestion,
        "saving_kg":  saving_kg,
        "priority":   priority,
        "top_cause":  top_cause,
        "created_at": datetime.utcnow()
    })


def get_latest_recommendation(device_id):
    return recommendations.find_one(
        {"device_id": device_id},
        sort=[("created_at", -1)]
    )


# ─────────────────────────────────
# USERS
# ─────────────────────────────────

def save_user(name, email, password_hash, role="user"):
    users.insert_one({
        "name":          name,
        "email":         email,
        "password_hash": password_hash,
        "role":          role,
        "created_at":    datetime.utcnow()
    })


def get_user_by_email(email):
    return users.find_one({"email": email})


def get_all_users():
    # Never return password hash
    return list(users.find(
        {},
        {"password_hash": 0}
    ))


def update_user_role(user_id, new_role):
    from bson import ObjectId
    users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"role": new_role}}
    )


def delete_user(user_id):
    from bson import ObjectId
    users.delete_one({"_id": ObjectId(user_id)})


# ─────────────────────────────────
# TEST
# ─────────────────────────────────

if __name__ == "__main__":

    print("=" * 40)
    print("TESTING DB OPERATIONS")
    print("=" * 40)

    # Test 1: Save a sensor reading
    print("\n--- SENSOR READINGS ---")
    fake_reading = {
        "device_id":   "ESP32_001",
        "voltage":      220.5,
        "current":      2.3,
        "power_kw":     0.506,
        "energy_kwh":   0.042,
        "co2_ppm":      820,
        "temperature":  28.5,
        "carbon_kg":    0.034,
        "timestamp":    datetime.utcnow()
    }
    saved_id = save_reading(fake_reading)
    print(f"Reading saved ✅  ID: {saved_id}")

    # Test 2: Get latest reading
    latest = get_latest_reading("ESP32_001")
    print(f"Latest reading ✅  "
          f"power={latest['power_kw']} kW, "
          f"co2={latest['co2_ppm']} ppm")

    # Test 3: Save anomaly
    print("\n--- ANOMALIES ---")
    save_anomaly(
        device_id    = "ESP32_001",
        reading_id   = saved_id,
        anomaly_type = "spike",
        severity     = "high",
        message      = "Power usage 3x above normal"
    )
    print("Anomaly saved ✅")

    # Test 4: Get anomalies
    anomaly_list = get_anomalies("ESP32_001")
    print(f"Anomalies found ✅  count={len(anomaly_list)}")

    # Test 5: Save recommendation
    print("\n--- RECOMMENDATIONS ---")
    save_recommendation(
        device_id  = "ESP32_001",
        suggestion = "Reduce AC usage by 2 hours",
        saving_kg  = 1.2,
        priority   = "high",
        top_cause  = "power_kw"
    )
    print("Recommendation saved ✅")

    # Test 6: Get recommendation
    rec = get_latest_recommendation("ESP32_001")
    print(f"Recommendation found ✅  "
          f"suggestion='{rec['suggestion']}'")

    # Test 7: Save user
    print("\n--- USERS ---")
    save_user(
        name          = "Ankur",
        email         = "ankur@bmsit.in",
        password_hash = "hashed_password_here",
        role          = "admin"
    )
    print("User saved ✅")

    # Test 8: Get user by email
    user = get_user_by_email("ankur@bmsit.in")
    print(f"User found ✅  "
          f"name={user['name']}, role={user['role']}")

    # Test 9: Get all users
    all_users = get_all_users()
    print(f"All users ✅  count={len(all_users)}")

    print("\n" + "=" * 40)
    print("ALL TESTS PASSED ✅")
    print("=" * 40)