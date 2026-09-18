import os
import sys
import random
import pandas as pd
import numpy as np
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from simulator.engine import UAVPistonEngine
from simulator.faults import FaultManager
from physics.engine_model import PhysicsEngineModel
from physics.residuals import ResidualCalculator
from backend.services.edge_preprocessor import EdgePreprocessor

def generate_dataset(n_samples: int = 12000, output_path: str = None):
    print(f"Synthesizing {n_samples} physics-coupled UAV engine telemetry records...")
    if output_path is None:
        output_path = root_dir / "data" / "engine_synthetic_dataset.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    engine = UAVPistonEngine()
    fault_mgr = FaultManager()
    physics = PhysicsEngineModel()
    resid_calc = ResidualCalculator()
    edge = EdgePreprocessor(window_size=12)

    records = []
    fault_types = ["NORMAL"] + FaultManager.FAULT_TYPES
    samples_per_class = n_samples // len(fault_types)

    batch_count = samples_per_class // 15

    for fault_class in fault_types:
        print(f"  Generating signature records for: {fault_class}...")
        fault_mgr.clear()

        for b in range(batch_count):
            throttle = random.uniform(45.0, 80.0)
            alt = random.uniform(3000.0, 16000.0)
            amb_temp = random.uniform(5.0, 32.0)
            engine.set_conditions(throttle=throttle, altitude=alt, ambient_temp=amb_temp)

            # Settle engine to clean flight regime
            fault_mgr.clear()
            for _ in range(40):
                raw = engine.step(dt=0.1)
                edge.process(raw)

            # If fault class, inject with randomized realistic severity and let it manifest
            if fault_class != "NORMAL":
                sev = random.uniform(0.70, 0.95)
                fault_mgr.inject(fault_class, severity="HIGH", ramp_duration=0.5)
                fault_mgr.target_severity = sev
                fault_mgr.current_severity = sev
                fault_mgr.update(dt=0.1, engine=engine)
                # Allow fault dynamics (thermal, fluid, vibration) to fully express
                for _ in range(35):
                    fault_mgr.update(dt=0.1, engine=engine)
                    raw = engine.step(dt=0.1)
                    edge.process(raw)

            # Record 15 calibrated samples per batch
            for _ in range(15):
                if fault_class != "NORMAL":
                    fault_mgr.update(dt=0.1, engine=engine)
                else:
                    fault_mgr.clear()

                raw = engine.step(dt=0.1)
                edge_res = edge.process(raw)
                clean = edge_res["cleaned_telemetry"]
                derived = edge_res["derived_features"]
                
                expected = physics.calculate_expected(
                    rpm=clean["rpm"],
                    throttle=clean["throttle"],
                    altitude=clean["altitude"],
                    ambient_temp=clean["ambient_temp"],
                    engine_load=clean["engine_load"]
                )
                residuals = resid_calc.calculate(clean, expected)

                rec = {
                    "rpm": clean["rpm"],
                    "engine_temp": clean["engine_temp"],
                    "oil_temp": clean["oil_temp"],
                    "oil_pressure": clean["oil_pressure"],
                    "fuel_flow": clean["fuel_flow"],
                    "manifold_pressure": clean["manifold_pressure"],
                    "exhaust_gas_temp": clean["exhaust_gas_temp"],
                    "vibration": clean["vibration"],
                    "engine_load": clean["engine_load"],
                    "altitude": clean["altitude"],
                    "ambient_temp": clean["ambient_temp"],
                    "throttle": clean["throttle"],
                    "temperature_rate": derived["temperature_rate"],
                    "vibration_rate": derived["vibration_rate"],
                    "oil_pressure_rate": derived["oil_pressure_rate"],
                    "residual_engine_temp": residuals["residual_engine_temp"],
                    "residual_oil_pressure": residuals["residual_oil_pressure"],
                    "residual_vibration": residuals["residual_vibration"],
                    "residual_exhaust_gas_temp": residuals["residual_exhaust_gas_temp"],
                    "composite_residual_norm": residuals["composite_residual_norm"],
                    "fault_class": fault_class
                }
                records.append(rec)

    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} samples saved to {output_path}.")
    return df

if __name__ == "__main__":
    generate_dataset()
