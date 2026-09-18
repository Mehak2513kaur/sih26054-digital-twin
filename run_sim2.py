"""
DRDO Problem Statement 26054: Sim 2 Master Launcher
Executes the full continuous flow:
Engine Simulator -> Fault Injection -> Modified Telemetry -> MQTT Publisher -> Digital Twin -> AI Diagnostics -> Component Health -> RUL
"""

import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from simulator.run_sim2 import run_sim2
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DRDO PS 26054: UAV Digital Twin - Sim 2 Runner")
    parser.add_argument("--fault", type=str, default="none", help="Fault type (e.g. overheating, 'low oil pressure', misfire, 'bearing degradation')")
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
