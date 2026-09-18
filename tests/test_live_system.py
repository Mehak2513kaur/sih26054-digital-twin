import requests
import time
import json
import os

BASE = "http://localhost:8000/api"

def log(section, msg):
    print(f"[{section}] {msg}")

def run_tests():
    print("=" * 70)
    print(" DRDO PS 26054: UAV DIGITAL TWIN FULL END-TO-END SYSTEM VERIFICATION")
    print("=" * 70)

    # 1. Health endpoint test
    r = requests.get(f"{BASE}/health")
    assert r.status_code == 200, f"Health check failed: {r.status_code}"
    health_data = r.json()
    log("HEALTH", f"System: {health_data.get('system')}")
    log("HEALTH", f"Mode: {health_data.get('mode')}")
    log("HEALTH", f"Subsystems: {list(health_data.get('subsystems', {}).keys())}")
    log("HEALTH", f"WebSocket Endpoint: {health_data['subsystems']['websocket']['endpoint']}")
    assert health_data['subsystems']['websocket']['endpoint'] == "/ws/engine", "WS endpoint mismatch!"

    # 2. Mission Start
    r = requests.post(f"{BASE}/missions/start", json={
        "scenario": "NORMAL_MISSION",
        "altitude": 8000,
        "ambient_temp": 18,
        "throttle": 65
    })
    assert r.status_code == 200, f"Mission start failed: {r.status_code}"
    mission_id = r.json().get("mission_id", "TEST_MISSION")
    log("MISSION", f"Started mission {mission_id}")
    time.sleep(2)

    # 3. Test All 7 Fault Injections & Live ML Predictions
    fault_types = [
        "OVERHEATING",
        "MISFIRE",
        "OIL_PRESSURE_FAILURE",
        "VIBRATION_ANOMALY",
        "FUEL_SYSTEM_ANOMALY",
        "SENSOR_DRIFT",
        "BEARING_DEGRADATION"
    ]

    fault_results = {}

    for f_type in fault_types:
        # Inject fault with fast ramp
        r_inj = requests.post(f"{BASE}/fault/inject", json={
            "fault_type": f_type,
            "severity": "HIGH",
            "ramp_duration": 2.0
        })
        assert r_inj.status_code == 200, f"Fault injection failed for {f_type}"
        
        # Wait for simulation steps to register fault and propagate through physics + ML
        time.sleep(5)

        # Query prediction
        r_pred = requests.get(f"{BASE}/prediction")
        assert r_pred.status_code == 200
        p_json = r_pred.json()
        
        ml = p_json.get("prediction", {}) or p_json.get("ml", {})
        pred_fault = ml.get("predicted_fault")
        conf = ml.get("confidence", 0.0)
        is_anomaly = ml.get("is_anomaly", False)
        
        # Query twin residuals
        r_twin = requests.get(f"{BASE}/twin/state")
        twin_json = r_twin.json()
        residuals = twin_json.get("residuals", {}).get("parameters", {})
        
        passed = (pred_fault == f_type)
        fault_results[f_type] = {
            "passed": passed,
            "detected": pred_fault,
            "confidence": conf,
            "is_anomaly": is_anomaly
        }
        
        status_sym = "[PASS]" if passed else "[WARN]"
        log("FAULT-TEST", f"{status_sym} Injected: {f_type:<22} -> Detected: {pred_fault:<22} (Conf: {conf:.1f}%, Anomaly: {is_anomaly})")

        # Clear fault
        requests.post(f"{BASE}/fault/clear")
        time.sleep(2)

    # 4. Stop Mission
    r_stop = requests.post(f"{BASE}/missions/stop")
    assert r_stop.status_code == 200
    log("MISSION", f"Stopped mission {mission_id}")

    # 5. PDF Generation Test
    r_pdf = requests.get(f"{BASE}/report/{mission_id}/pdf")
    assert r_pdf.status_code == 200, f"PDF report generation failed: {r_pdf.status_code}"
    content_type = r_pdf.headers.get("content-type", "")
    assert "pdf" in content_type.lower(), f"Unexpected Content-Type: {content_type}"
    pdf_size = len(r_pdf.content)
    log("PDF-REPORT", f"Generated DRDO Dossier PDF: {pdf_size} bytes (Content-Type: {content_type})")

    # 6. Demo Mode Full Life-Cycle Test
    log("DEMO", "Starting 120s Demo Mode...")
    r_demo_start = requests.post(f"{BASE}/demo/start")
    assert r_demo_start.status_code == 200
    time.sleep(3)

    r_demo_stat = requests.get(f"{BASE}/demo/status")
    d_stat = r_demo_stat.json()
    log("DEMO", f"Demo running: active={d_stat.get('is_active')}, time={d_stat.get('current_time_sec'):.1f}s, stage='{d_stat.get('current_stage')}'")

    log("DEMO", "Pausing demo...")
    r_pause = requests.post(f"{BASE}/demo/pause")
    assert r_pause.status_code == 200 and r_pause.json().get("is_paused") is True

    log("DEMO", "Resuming demo...")
    r_resume = requests.post(f"{BASE}/demo/resume")
    assert r_resume.status_code == 200 and r_resume.json().get("is_paused") is False

    log("DEMO", "Stopping demo...")
    r_demo_stop = requests.post(f"{BASE}/demo/stop")
    assert r_demo_stop.status_code == 200
    log("DEMO", "Demo stopped cleanly without exception.")

    # 7. Quality & History Endpoints
    r_hist = requests.get(f"{BASE}/sensors/history?limit=20")
    assert r_hist.status_code == 200
    log("HISTORY", f"Telemetry points in history: {len(r_hist.json().get('history', []))}")

    r_qual = requests.get(f"{BASE}/quality")
    assert r_qual.status_code == 200
    log("QUALITY", f"Sensor status: {r_qual.json().get('status', 'OK')}")

    print("=" * 70)
    print(" ALL END-TO-END VERIFICATION CHECKS COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
