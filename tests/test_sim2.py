"""
DRDO Problem Statement 26054: Sim 2 Verification Suite
Tests:
1. All 10 fault injections and their logical physics coupling
2. All 4 severity levels (LOW, MEDIUM, HIGH, CRITICAL)
3. MQTT Publisher with all 4 topics and 18 mandatory telemetry fields
4. Verification of JSON payloads and mock mode
5. Component health wear integration and RUL prediction
"""

import sys
import os
import json
import time
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from simulator.engine import UAVPistonEngine
from simulator.fault_injection import FaultInjectionEngine, FaultType, FaultSeverity
from simulator.publisher import MQTTSimulatorPublisher
from physics.engine_model import PhysicsEngineModel
from physics.residuals import ResidualCalculator
from ml.inference import EngineAIInference


def test_sim2_all():
    print("=" * 75)
    print("  DRDO PS 26054: SIM 2 MODULE COMPREHENSIVE VERIFICATION SUITE")
    print("=" * 75)

    engine = UAVPistonEngine(engine_id="UAV-PX-TEST")
    fault_engine = FaultInjectionEngine()
    publisher = MQTTSimulatorPublisher(mock_mode=True)
    physics_twin = PhysicsEngineModel()
    residual_calc = ResidualCalculator()
    ai_inference = EngineAIInference()

    # -------------------------------------------------------------
    # TEST 1: Verify Baseline Telemetry & 18 Mandatory Fields
    # -------------------------------------------------------------
    print("\n[TEST 1] Verifying Baseline Telemetry & 18 Mandatory Fields...")
    raw = engine.step(dt=0.1)
    mod = fault_engine.apply_fault(raw)

    expected_18 = [
        "timestamp", "rpm", "cht", "egt", "oil_pressure", "oil_temperature",
        "fuel_pressure", "fuel_flow", "map", "boost_pressure", "vibration",
        "engine_load", "throttle", "altitude", "ambient_temperature",
        "coolant_temperature", "battery_voltage", "engine_hours"
    ]

    for field in expected_18:
        assert field in mod, f"Missing mandatory field '{field}' in telemetry!"
        assert isinstance(mod[field], (int, float)), f"Field '{field}' must be numeric, got {type(mod[field])}"

    print(f"  -> PASS: All 18 mandatory telemetry fields verified with valid numeric types.")

    # -------------------------------------------------------------
    # TEST 2: Verify All 10 Fault Types & Physical Coupling
    # -------------------------------------------------------------
    print("\n[TEST 2] Verifying All 10 Fault Injections & Physical Coupling...")

    fault_test_cases = [
        ("overheating", "cht", 125.0, ">", "CHT increased logically"),
        ("low oil pressure", "oil_pressure", 2.5, "<", "Oil pressure decreased logically"),
        ("high oil temperature", "oil_temperature", 110.0, ">", "Oil temperature increased logically"),
        ("misfire", "vibration", 4.0, ">", "Torsional vibration spiked logically"),
        ("vibration anomaly", "vibration", 5.0, ">", "Imbalance vibration increased logically"),
        ("fuel-system anomaly", "egt", 830.0, ">", "Lean burn EGT spiked logically"),
        ("injector degradation", "egt", 780.0, ">", "Delayed burn EGT increased logically"),
        ("turbocharger degradation", "map", 26.0, "<", "Manifold boost decreased logically"),
        ("bearing degradation", "oil_temperature", 98.0, ">", "Bearing friction increased oil temp"),
        ("sensor drift", "cht", 115.0, ">", "Transducer reported drift verified"),
    ]

    for f_name, check_param, threshold, op, description in fault_test_cases:
        fault_engine.start_fault(fault_name=f_name, severity="HIGH", ramp_duration=1.0)
        # Advance 2 seconds to reach full intensity
        for _ in range(20):
            fault_engine.update(dt=0.1)

        b_tele = engine.step(dt=0.1)
        m_tele = fault_engine.apply_fault(b_tele)
        val = m_tele[check_param]

        if op == ">":
            passed = val > threshold
        else:
            passed = val < threshold

        assert passed, f"Fault '{f_name}' failed physical check: {check_param}={val} (expected {op} {threshold})"
        print(f"  [{f_name.upper():<25}] {check_param} = {val} ({description}) -> PASS")

        fault_engine.stop_fault()
        fault_engine.update(dt=0.5)

    # -------------------------------------------------------------
    # TEST 3: Verify Severity Levels (LOW, MEDIUM, HIGH, CRITICAL)
    # -------------------------------------------------------------
    print("\n[TEST 3] Verifying Severity Levels Scaling (LOW, MEDIUM, HIGH, CRITICAL)...")
    severities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    cht_values = []

    for sev in severities:
        fault_engine.start_fault(fault_name="overheating", severity=sev, ramp_duration=0.5)
        for _ in range(10):
            fault_engine.update(dt=0.1)
        m_tele = fault_engine.apply_fault(engine.step(dt=0.1))
        cht_values.append(m_tele["cht"])
        fault_engine.stop_fault()

    print(f"  CHT scaling across severities: {dict(zip(severities, cht_values))}")
    assert cht_values[0] < cht_values[1] < cht_values[2] < cht_values[3], "Severity scaling is not strictly monotonic!"
    print(f"  -> PASS: Monotonic severity scaling confirmed across all 4 levels.")

    # -------------------------------------------------------------
    # TEST 4: Verify MQTT Publisher & JSON Payloads on 4 Topics
    # -------------------------------------------------------------
    print("\n[TEST 4] Verifying MQTT Publishing on All 4 Topics...")

    # Topic 1: Telemetry
    pub_tel = publisher.publish_telemetry(m_tele)
    assert pub_tel, "Failed to publish telemetry!"

    # Topic 2: Faults
    pub_flt = publisher.publish_fault({
        "timestamp": time.time(),
        "fault_type": "OVERHEATING",
        "severity": "CRITICAL",
        "action": "INJECTED",
        "stresses": {"thermal_stress": 3.5}
    })
    assert pub_flt, "Failed to publish fault event!"

    # Topic 3: Health
    pub_hlt = publisher.publish_health({
        "health_score": 78.4,
        "status": "DEGRADING",
        "component_health": fault_engine.component_health,
        "rul_hours": 120.5,
    })
    assert pub_hlt, "Failed to publish health event!"

    # Topic 4: Alerts
    pub_alt = publisher.publish_alert({
        "timestamp": time.time(),
        "anomaly_detected": True,
        "anomaly_score": 92.5,
        "predicted_fault": "OVERHEATING",
        "confidence": 98.0,
        "directive": "Immediate throttle derate to 40% recommended"
    })
    assert pub_alt, "Failed to publish alert event!"

    stats = publisher.get_stats()
    print(f"  Published messages: {stats['topic_counts']}")
    for topic in [MQTTSimulatorPublisher.TOPIC_TELEMETRY, MQTTSimulatorPublisher.TOPIC_FAULTS, MQTTSimulatorPublisher.TOPIC_HEALTH, MQTTSimulatorPublisher.TOPIC_ALERTS]:
        assert stats["topic_counts"][topic] >= 1, f"Topic {topic} was not published to!"

    # Verify JSON serializability of recent records
    recent = publisher.get_recent_messages(limit=4)
    for rec in recent:
        json_str = json.dumps(rec["payload"])
        deserialized = json.loads(json_str)
        assert isinstance(deserialized, dict), "Payload failed JSON roundtrip verification!"

    print("  -> PASS: All 4 MQTT topics verified with clean JSON payloads and mock buffer.")

    # -------------------------------------------------------------
    # TEST 5: Verify Full Flow to Digital Twin, ML & RUL
    # -------------------------------------------------------------
    print("\n[TEST 5] Verifying Full Flow: Sim -> Fault -> MQTT -> Twin -> ML -> RUL...")
    fault_engine.start_fault("low oil pressure", "CRITICAL", ramp_duration=1.0)
    # Step continuous simulation and AI inference loop for 20 steps
    for _ in range(20):
        fault_engine.update(dt=0.1)
        raw_tel = engine.step(dt=0.1)
        mod_tel = fault_engine.apply_fault(raw_tel)
        publisher.publish_telemetry(mod_tel)

        expected = physics_twin.calculate_expected(
            rpm=mod_tel["rpm"],
            throttle=mod_tel["throttle"],
            altitude=mod_tel["altitude"],
            ambient_temp=mod_tel["ambient_temperature"],
            engine_load=mod_tel["engine_load"]
        )
        residuals = residual_calc.calculate(mod_tel, expected)
        derived = {"temperature_rate": 0.0, "vibration_rate": 0.0, "oil_pressure_rate": 0.0, "rpm_change": 0.0}
        ml_pred = ai_inference.predict(mod_tel, residuals, derived, expected)

    oil_p_res = residuals["parameters"]["oil_pressure"]
    assert oil_p_res["status"] in ("WARNING", "DIVERGENT"), f"Expected oil pressure divergence, got {oil_p_res['status']}"
    assert ml_pred["is_anomaly"] is True, "AI failed to flag anomaly on critical oil pressure drop!"
    assert ml_pred["rul"]["rul_hours"] < 400.0, f"RUL failed to degrade under critical fault! Current: {ml_pred['rul']['rul_hours']}"

    print(f"  Physical Residual Z-Score : {oil_p_res['z_score']} sigma ({oil_p_res['status']})")
    print(f"  AI Classified Fault       : {ml_pred['predicted_fault']} (Confidence: {ml_pred['confidence']}%)")
    print(f"  AI Anomaly Flag           : {ml_pred['is_anomaly']}")
    print(f"  Degraded RUL              : {ml_pred['rul']['rul_hours']} hours")
    print(f"  Bearing Health            : {fault_engine.component_health['crank_bearings']}%")
    print("  -> PASS: Full continuous flow verified from simulation to AI/RUL output.")

    publisher.stop()
    print("\n" + "=" * 75)
    print("  ALL SIM 2 TESTS PASSED SUCCESSFULLY! (5/5 SUITES)")
    print("=" * 75)


if __name__ == "__main__":
    test_sim2_all()
