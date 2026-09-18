"""
MALE UAV Piston Engine Digital Twin - Sim 2 Runner
DRDO Problem Statement 26054

Demonstrates the continuous end-to-end pipeline:
Engine Simulator
      ↓
Fault Injection (10 logical failure modes)
      ↓
Modified Telemetry (18 parameters)
      ↓
MQTT Publisher (uav/engine/telemetry, faults, health, alerts)
      ↓
Digital Twin / Residuals Engine
      ↓
AI Diagnostics & Anomaly Detection
      ↓
Component Health Monitoring
      ↓
Prognostic RUL Estimation
"""

import sys
import os
import time
import argparse
import json
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


def run_sim2(
    fault: str = "none",
    severity: str = "MEDIUM",
    duration: float = 30.0,
    rate_hz: float = 5.0,
    broker: str = "localhost",
    port: int = 1883,
    mock_mqtt: bool = False,
):
    print("=" * 78)
    print("  DRDO PS 26054: MALE UAV PISTON ENGINE DIGITAL TWIN - SIM 2 PIPELINE")
    print("=" * 78)
    print(f"  Simulation Rate : {rate_hz} Hz (dt = {1.0/rate_hz:.2f}s)")
    print(f"  Target Fault    : {fault.upper()} (Severity: {severity})")
    print(f"  Run Duration    : {duration} seconds")
    print(f"  MQTT Broker     : {broker}:{port} (Mock fallback enabled)")
    print("-" * 78)

    # 1. Initialize Pipeline Components
    engine = UAVPistonEngine(engine_id="UAV-PX-SIM2", initial_hours=1250.0)
    fault_injector = FaultInjectionEngine()
    publisher = MQTTSimulatorPublisher(broker=broker, port=port, mock_mode=mock_mqtt)
    physics_twin = PhysicsEngineModel()
    residual_calc = ResidualCalculator()
    ai_inference = EngineAIInference()

    # 2. Start fault if requested
    if fault.lower() not in ("none", "normal"):
        print(f"[*] Arming fault injection: '{fault}' at {severity} severity...")
        fault_injector.start_fault(fault_name=fault, severity=severity, ramp_duration=8.0)
        # Publish fault injection event to MQTT
        publisher.publish_fault({
            "timestamp": time.time(),
            "fault_type": fault,
            "severity": severity,
            "action": "INJECTED",
            "ramp_duration": 8.0
        })

    dt = 1.0 / rate_hz
    start_time = time.time()
    step_count = 0

    print(f"[*] Starting continuous simulation loop...")
    print(f"{'Time':<7} | {'RPM':<5} | {'CHT':<6} | {'OilP':<5} | {'OilT':<5} | {'EGT':<5} | {'Vib':<5} | {'Fault Active':<15} | {'Health':<6} | {'RUL':<6}")
    print("-" * 78)

    try:
        while time.time() - start_time < duration:
            t0 = time.time()
            step_count += 1

            # A. Update Fault Progression
            fault_status = fault_injector.update(dt=dt)

            # B. Step Engine Simulator Physics
            raw_telemetry = engine.step(dt=dt)

            # C. Apply Fault Injection -> Modified Telemetry
            modified_telemetry = fault_injector.apply_fault(raw_telemetry)

            # D. MQTT Publish Telemetry -> uav/engine/telemetry
            publisher.publish_telemetry(modified_telemetry)

            # E. Digital Twin Virtual State & Residuals
            expected = physics_twin.calculate_expected(
                rpm=modified_telemetry["rpm"],
                throttle=modified_telemetry["throttle"],
                altitude=modified_telemetry["altitude"],
                ambient_temp=modified_telemetry["ambient_temperature"],
                engine_load=modified_telemetry["engine_load"],
            )
            residuals = residual_calc.calculate(modified_telemetry, expected)

            # F. AI Diagnostics (Anomaly Detection + Fault Classification + RUL)
            derived = {
                "temperature_rate": 0.0,
                "vibration_rate": 0.0,
                "oil_pressure_rate": 0.0,
                "rpm_change": 0.0,
            }
            ml_pred = ai_inference.predict(modified_telemetry, residuals, derived, expected)
            rul_data = ml_pred.get("rul", {})
            rul_hours = rul_data.get("rul_hours", 450.0)

            # G. Component Health Fusion
            comp_health = fault_injector.component_health
            overall_health = comp_health.get("overall_engine_health", 95.0)

            # H. MQTT Publish Health -> uav/engine/health
            publisher.publish_health({
                "health_score": overall_health,
                "status": "HEALTHY" if overall_health > 80 else ("DEGRADING" if overall_health > 50 else "CRITICAL"),
                "component_health": comp_health,
                "rul_hours": rul_hours,
                "degradation_velocity": rul_data.get("degradation_velocity", 0.0),
            })

            # I. MQTT Publish Alerts -> uav/engine/alerts if anomaly detected
            if ml_pred.get("is_anomaly") or ml_pred.get("predicted_fault") != "NORMAL":
                publisher.publish_alert({
                    "timestamp": time.time(),
                    "anomaly_detected": ml_pred.get("is_anomaly", True),
                    "anomaly_score": ml_pred.get("anomaly_intensity", 85.0),
                    "predicted_fault": ml_pred.get("predicted_fault", "ANOMALY"),
                    "confidence": ml_pred.get("confidence", 95.0),
                    "severity": fault_status.get("severity", "WARNING"),
                    "directive": "Immediate throttle derate recommended to prevent mechanical seizure",
                })

            # J. Console display every 5 steps
            if step_count % 5 == 0:
                elapsed = time.time() - start_time
                f_name = fault_status["active_fault"] if fault_status["is_active"] else "NORMAL"
                print(
                    f"{elapsed:5.1f}s  | "
                    f"{modified_telemetry['rpm']:5.0f} | "
                    f"{modified_telemetry['cht']:5.1f}° | "
                    f"{modified_telemetry['oil_pressure']:4.2f}b | "
                    f"{modified_telemetry['oil_temperature']:4.1f}° | "
                    f"{modified_telemetry['egt']:5.0f}° | "
                    f"{modified_telemetry['vibration']:4.2f} | "
                    f"{f_name:<15} | "
                    f"{overall_health:5.1f}% | "
                    f"{rul_hours:5.1f}h"
                )

            sleep_time = max(0.001, dt - (time.time() - t0))
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n[*] Sim 2 stopped by user.")

    # Stop publisher and display statistics
    publisher.stop()
    stats = publisher.get_stats()

    print("=" * 78)
    print("  SIM 2 EXECUTION COMPLETE")
    print("=" * 78)
    print(f"  Total Steps Simulated : {step_count}")
    print(f"  Total MQTT Published  : {stats['total_published']} messages")
    print(f"  Topic Breakdown       :")
    for top, count in stats["topic_counts"].items():
        print(f"    - {top:<25}: {count} messages")
    print(f"  MQTT Broker Status    : {'CONNECTED' if stats['is_connected'] else 'MOCK SIMULATION MODE'}")
    print(f"  Final Engine Health   : {comp_health.get('overall_engine_health', 95.0)}%")
    print(f"  Final Projected RUL   : {rul_hours:.1f} hours")
    print("=" * 78)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DRDO PS 26054: UAV Digital Twin - Sim 2 Runner")
    parser.add_argument("--fault", type=str, default="none", help="Fault type (overheating, low oil pressure, misfire, etc.)")
    parser.add_argument("--severity", type=str, default="MEDIUM", choices=["LOW", "MEDIUM", "HIGH", "CRITICAL"])
    parser.add_argument("--duration", type=float, default=15.0, help="Run duration in seconds")
    parser.add_argument("--rate", type=float, default=10.0, help="Simulation loop rate in Hz")
    parser.add_argument("--broker", type=str, default="localhost", help="MQTT Broker host")
    parser.add_argument("--port", type=int, default=1883, help="MQTT Broker port")
    parser.add_argument("--mock", action="store_true", help="Force mock MQTT mode")
    args = parser.parse_args()

    run_sim2(
        fault=args.fault,
        severity=args.severity,
        duration=args.duration,
        rate_hz=args.rate,
        broker=args.broker,
        port=args.port,
        mock_mqtt=args.mock,
    )
