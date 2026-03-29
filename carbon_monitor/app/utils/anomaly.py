# app/utils/anomaly_detection.py

import numpy as np

# ─────────────────────────────────
# THRESHOLDS
# Define what counts as warning/critical
# ─────────────────────────────────

THRESHOLDS = {
    "power_kw":    {"warning": 3.0,  "critical": 5.0},
    "co2_ppm":     {"warning": 1000, "critical": 1500},
    "temperature": {"warning": 35,   "critical": 40}
}


# ─────────────────────────────────
# METHOD 1: Z-SCORE
# Compares new reading vs history
# ─────────────────────────────────

def zscore_detection(new_value, historical_values):

    # Need at least 10 past readings
    if len(historical_values) < 10:
        return {
            "is_anomaly": False,
            "reason":     "Not enough history yet",
            "severity":   None,
            "message":    None
        }

    mean    = np.mean(historical_values)
    std     = np.std(historical_values)

    # Avoid division by zero
    if std == 0:
        return {
            "is_anomaly": False,
            "reason":     "No variation in readings",
            "severity":   None,
            "message":    None
        }

    z_score = (new_value - mean) / std

    if z_score > 3:
        return {
            "is_anomaly": True,
            "z_score":    round(z_score, 2),
            "severity":   "high",
            "message":    f"Power usage extremely high: "
                          f"{round(new_value, 2)} kW "
                          f"(normal: {round(mean, 2)} kW)"
        }

    elif z_score > 2:
        return {
            "is_anomaly": True,
            "z_score":    round(z_score, 2),
            "severity":   "medium",
            "message":    f"Power usage above normal: "
                          f"{round(new_value, 2)} kW "
                          f"(normal: {round(mean, 2)} kW)"
        }

    else:
        return {
            "is_anomaly": False,
            "z_score":    round(z_score, 2),
            "severity":   None,
            "message":    None
        }


# ─────────────────────────────────
# METHOD 2: THRESHOLD CHECK
# Simple check against fixed limits
# ─────────────────────────────────

def threshold_detection(reading):

    alerts = []

    for field, limits in THRESHOLDS.items():

        value = reading.get(field)
        if value is None:
            continue

        if value >= limits["critical"]:
            alerts.append({
                "field":    field,
                "value":    value,
                "severity": "high",
                "message":  f"{field} is critically high: {value}"
            })

        elif value >= limits["warning"]:
            alerts.append({
                "field":    field,
                "value":    value,
                "severity": "medium",
                "message":  f"{field} is above normal: {value}"
            })

    return alerts


# ─────────────────────────────────
# COMBINED CHECK
# This is what API layer will call
# ─────────────────────────────────

def run_anomaly_check(new_reading, historical_power_values):

    # Run both methods
    zscore_result     = zscore_detection(
                            new_reading["power_kw"],
                            historical_power_values
                        )

    threshold_results = threshold_detection(new_reading)

    # Is it an anomaly by either method?
    is_anomaly = (
        zscore_result["is_anomaly"] or
        len(threshold_results) > 0
    )

    return {
        "is_anomaly":       is_anomaly,
        "zscore_result":    zscore_result,
        "threshold_alerts": threshold_results
    }


# ─────────────────────────────────
# TEST
# ─────────────────────────────────

if __name__ == "__main__":

    print("=" * 40)
    print("TESTING ANOMALY DETECTION")
    print("=" * 40)

    # Fake history — normal usage around 1.2 kW
    history = [1.2, 1.3, 1.1, 1.4, 1.2,
               1.3, 1.1, 1.2, 1.3, 1.2,
               1.4, 1.1, 1.2, 1.3, 1.2]

    print("\n--- Z-SCORE TESTS ---")

    # Test 1: Normal reading
    result = zscore_detection(1.3, history)
    print(f"Normal reading (1.3 kW): "
          f"anomaly={result['is_anomaly']}")
    # Expected: False ✅

    # Test 2: Medium spike
    result = zscore_detection(2.8, history)
    print(f"Medium spike (2.8 kW):   "
          f"anomaly={result['is_anomaly']}, "
          f"severity={result['severity']}")
    # Expected: True, medium ✅

    # Test 3: High spike
    result = zscore_detection(8.5, history)
    print(f"High spike (8.5 kW):     "
          f"anomaly={result['is_anomaly']}, "
          f"severity={result['severity']}")
    # Expected: True, high ✅

    # Test 4: Not enough history
    result = zscore_detection(1.3, [1.2, 1.3])
    print(f"Short history:           "
          f"anomaly={result['is_anomaly']}, "
          f"reason={result['reason']}")
    # Expected: False, not enough history ✅

    print("\n--- THRESHOLD TESTS ---")

    # Test 5: All normal
    reading = {"power_kw": 1.5, "co2_ppm": 600,
               "temperature": 28}
    alerts = threshold_detection(reading)
    print(f"All normal:              alerts={len(alerts)}")
    # Expected: 0 alerts ✅

    # Test 6: CO2 warning
    reading = {"power_kw": 1.5, "co2_ppm": 1100,
               "temperature": 28}
    alerts = threshold_detection(reading)
    print(f"CO2 warning:             alerts={len(alerts)}, "
          f"severity={alerts[0]['severity']}")
    # Expected: 1 alert, medium ✅

    # Test 7: Multiple critical
    reading = {"power_kw": 6.0, "co2_ppm": 1600,
               "temperature": 42}
    alerts = threshold_detection(reading)
    print(f"Multiple critical:       alerts={len(alerts)}")
    # Expected: 3 alerts ✅

    print("\n--- COMBINED CHECK TEST ---")

    # Test 8: Combined
    new_reading = {"power_kw": 8.5, "co2_ppm": 1600,
                   "temperature": 28}
    result = run_anomaly_check(new_reading, history)
    print(f"Combined check:          "
          f"is_anomaly={result['is_anomaly']}")
    print(f"Z-score severity:        "
          f"{result['zscore_result']['severity']}")
    print(f"Threshold alerts:        "
          f"{len(result['threshold_alerts'])}")
    # Expected: True, high, 2 alerts ✅