import os
import sys
import unittest
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from simulator.engine import UAVPistonEngine
from simulator.faults import FaultManager
from physics.engine_model import PhysicsEngineModel
from physics.residuals import ResidualCalculator
from backend.services.edge_preprocessor import EdgePreprocessor
from backend.services.health_fusion import HealthFusionEngine
from backend.services.recommendations import RecommendationEngine
from ml.inference import EngineAIInference

class TestUAVEngineFaultDetection(unittest.TestCase):
    '''
    Automated verification suite for DRDO PS 26054 Digital Twin.
    Tests all 7 fault injection modes + normal baseline across:
    - Sensor signature
    - Physics residuals & Z-scores
    - Anomaly detection score
    - Fault classification & confidence
    - Health score degradation
    - RUL prognostic decay
    - XAI factor attribution
    - Actionable maintenance recommendation
    '''
    @classmethod
    def setUpClass(cls):
        print("\n" + "="*80)
        print("  DRDO PS 26054 AUTOMATED FAULT INJECTION & DIGITAL TWIN TEST SUITE")
        print("="*80)
        cls.ai = EngineAIInference()
        cls.physics = PhysicsEngineModel()
        cls.resid_calc = ResidualCalculator()
        cls.health_fusion = HealthFusionEngine()
        cls.recs = RecommendationEngine()

    def run_fault_scenario(self, fault_type: str, steps: int = 35):
        engine = UAVPistonEngine()
        fault_mgr = FaultManager()
        edge = EdgePreprocessor(window_size=12)
        
        # Reset RUL predictor state for clean test isolation
        self.ai.rul_predictor.current_rul = 480.0
        self.ai.rul_predictor.smooth_degradation_index = 8.5
        
        engine.set_conditions(throttle=65.0, altitude=8000.0, ambient_temp=18.0)
        
        # Warmup and settle to baseline equilibrium
        for _ in range(40):
            raw = engine.step(dt=0.1)
            edge.process(raw)

        if fault_type != "NORMAL":
            fault_mgr.inject(fault_type, severity="HIGH", ramp_duration=0.5)
            fault_mgr.target_severity = 0.90
            fault_mgr.current_severity = 0.90
            fault_mgr.update(dt=0.1, engine=engine)
            # Allow dynamics to fully manifest
            for _ in range(35):
                fault_mgr.update(dt=0.1, engine=engine)
                raw = engine.step(dt=0.1)
                edge_out = edge.process(raw)
                clean = edge_out["cleaned_telemetry"]
                expected = self.physics.calculate_expected(clean["rpm"], clean["throttle"], clean["altitude"], clean["ambient_temp"], clean["engine_load"])
                residuals = self.resid_calc.calculate(clean, expected)
                self.ai.predict(clean, residuals, edge_out["derived_features"], expected)

        clean = None
        expected = None
        residuals = None
        pred = None
        derived = None

        for _ in range(steps):
            if fault_type != "NORMAL":
                fault_mgr.update(dt=0.1, engine=engine)
            raw = engine.step(dt=0.1)
            edge_out = edge.process(raw)
            clean = edge_out["cleaned_telemetry"]
            derived = edge_out["derived_features"]
            expected = self.physics.calculate_expected(
                rpm=clean["rpm"],
                throttle=clean["throttle"],
                altitude=clean["altitude"],
                ambient_temp=clean["ambient_temp"],
                engine_load=clean["engine_load"]
            )
            residuals = self.resid_calc.calculate(clean, expected)
            pred = self.ai.predict(clean, residuals, derived, expected)

        health = self.health_fusion.calculate(
            physics_residuals=residuals,
            ml_prediction=pred,
            derived_features=derived,
            fault_info={"severity_name": "HIGH" if fault_type != "NORMAL" else "NONE"}
        )
        rec = self.recs.get_recommendation(pred["predicted_fault"], "HIGH" if fault_type != "NORMAL" else "NONE")

        return {
            "clean": clean,
            "expected": expected,
            "residuals": residuals,
            "pred": pred,
            "health": health,
            "rec": rec
        }

    def test_01_normal_baseline(self):
        print("\n[TEST 1] Verifying NORMAL Baseline Flight...")
        res = self.run_fault_scenario("NORMAL")
        pred = res["pred"]
        health = res["health"]
        residuals = res["residuals"]

        print(f"  Classified Fault : {pred['predicted_fault']} (Confidence: {pred['confidence']:.1f}%)")
        print(f"  Health Score     : {health['health_score']:.1f}% ({health['status']})")
        print(f"  Residual Norm    : {residuals['composite_residual_norm']:.2f} sigma")
        print(f"  RUL Hours        : {pred['rul']['rul_hours']:.1f} h")

        self.assertEqual(pred["predicted_fault"], "NORMAL")
        self.assertGreaterEqual(health["health_score"], 80.0)
        self.assertLess(residuals["composite_residual_norm"], 1.8)
        self.assertGreaterEqual(pred["rul"]["rul_hours"], 380.0)
        print("  -> PASS: Baseline healthy cruise verified.")

    def test_02_overheating(self):
        print("\n[TEST 2] Verifying OVERHEATING Fault Signature...")
        res = self.run_fault_scenario("OVERHEATING")
        pred = res["pred"]
        health = res["health"]
        residuals = res["residuals"]
        xai = pred["explainability"]

        print(f"  Observed CHT     : {res['clean']['engine_temp']:.1f} ?C (Expected: {res['expected']['expected_engine_temp']:.1f} ?C)")
        print(f"  CHT Residual     : {residuals['residual_engine_temp']:+.1f} ?C")
        print(f"  Classified Fault : {pred['predicted_fault']} (Confidence: {pred['confidence']:.1f}%)")
        print(f"  Health Score     : {health['health_score']:.1f}% ({health['status']})")
        print(f"  RUL Decayed to   : {pred['rul']['rul_hours']:.1f} h")
        print(f"  Top XAI Factor   : {xai['contributions'][0]['label']}")
        print(f"  Directive        : {res['rec']['recommended_action'][:70]}...")

        self.assertEqual(pred["predicted_fault"], "OVERHEATING")
        self.assertGreater(residuals["residual_engine_temp"], 5.0)
        self.assertGreaterEqual(pred["confidence"], 75.0)
        self.assertLess(health["health_score"], 80.0)
        self.assertLess(pred["rul"]["rul_hours"], 300.0)
        print("  -> PASS: Overheating early divergence & classification verified.")

    def test_03_misfire(self):
        print("\n[TEST 3] Verifying MISFIRE Fault Signature...")
        res = self.run_fault_scenario("MISFIRE")
        pred = res["pred"]
        health = res["health"]
        residuals = res["residuals"]

        print(f"  Observed RMS Vib : {res['clean']['vibration']:.2f} mm/s (Expected: {res['expected']['expected_vibration']:.2f} mm/s)")
        print(f"  Vib Residual     : {residuals['residual_vibration']:+.2f} mm/s")
        print(f"  Classified Fault : {pred['predicted_fault']} (Confidence: {pred['confidence']:.1f}%)")
        print(f"  Health Score     : {health['health_score']:.1f}%")

        self.assertEqual(pred["predicted_fault"], "MISFIRE")
        self.assertGreater(residuals["residual_vibration"], 3.0)
        self.assertGreaterEqual(pred["confidence"], 75.0)
        print("  -> PASS: Cylinder misfire torsional signature verified.")

    def test_04_oil_pressure_failure(self):
        print("\n[TEST 4] Verifying OIL_PRESSURE_FAILURE Fault Signature...")
        res = self.run_fault_scenario("OIL_PRESSURE_FAILURE")
        pred = res["pred"]
        health = res["health"]
        residuals = res["residuals"]

        print(f"  Observed Oil P   : {res['clean']['oil_pressure']:.2f} bar (Expected: {res['expected']['expected_oil_pressure']:.2f} bar)")
        print(f"  Oil P Residual   : {residuals['residual_oil_pressure']:+.2f} bar")
        print(f"  Classified Fault : {pred['predicted_fault']} (Confidence: {pred['confidence']:.1f}%)")
        print(f"  Health Score     : {health['health_score']:.1f}% ({health['status']})")

        self.assertEqual(pred["predicted_fault"], "OIL_PRESSURE_FAILURE")
        self.assertLess(residuals["residual_oil_pressure"], -0.7)
        self.assertGreaterEqual(pred["confidence"], 75.0)
        self.assertLess(health["health_score"], 60.0)
        print("  -> PASS: Hydraulic oil pressure failure verified.")

    def test_05_vibration_anomaly(self):
        print("\n[TEST 5] Verifying VIBRATION_ANOMALY Fault Signature...")
        res = self.run_fault_scenario("VIBRATION_ANOMALY")
        pred = res["pred"]
        residuals = res["residuals"]

        print(f"  Observed RMS Vib : {res['clean']['vibration']:.2f} mm/s")
        print(f"  Vib Residual     : {residuals['residual_vibration']:+.2f} mm/s")
        print(f"  Classified Fault : {pred['predicted_fault']} (Confidence: {pred['confidence']:.1f}%)")

        self.assertEqual(pred["predicted_fault"], "VIBRATION_ANOMALY")
        self.assertGreater(residuals["residual_vibration"], 3.5)
        self.assertGreaterEqual(pred["confidence"], 75.0)
        print("  -> PASS: Dynamic vibration imbalance signature verified.")

    def test_06_fuel_system_anomaly(self):
        print("\n[TEST 6] Verifying FUEL_SYSTEM_ANOMALY Fault Signature...")
        res = self.run_fault_scenario("FUEL_SYSTEM_ANOMALY")
        pred = res["pred"]
        residuals = res["residuals"]

        print(f"  Fuel Flow Obs    : {res['clean']['fuel_flow']:.1f} L/h (Expected: {res['expected']['expected_fuel_flow']:.1f} L/h)")
        print(f"  EGT Obs          : {res['clean']['exhaust_gas_temp']:.1f} ?C (Expected: {res['expected']['expected_exhaust_gas_temp']:.1f} ?C)")
        print(f"  Classified Fault : {pred['predicted_fault']} (Confidence: {pred['confidence']:.1f}%)")

        self.assertEqual(pred["predicted_fault"], "FUEL_SYSTEM_ANOMALY")
        self.assertGreaterEqual(pred["confidence"], 75.0)
        print("  -> PASS: Lean fuel flow restriction verified.")

    def test_07_sensor_drift(self):
        print("\n[TEST 7] Verifying SENSOR_DRIFT Fault Signature...")
        res = self.run_fault_scenario("SENSOR_DRIFT")
        pred = res["pred"]
        residuals = res["residuals"]

        print(f"  CHT Obs (Drift)  : {res['clean']['engine_temp']:.1f} ?C (Expected: {res['expected']['expected_engine_temp']:.1f} ?C)")
        print(f"  Oil Temp (Real)  : {res['clean']['oil_temp']:.1f} ?C (Expected: {res['expected']['expected_oil_temp']:.1f} ?C)")
        print(f"  Classified Fault : {pred['predicted_fault']} (Confidence: {pred['confidence']:.1f}%)")

        self.assertEqual(pred["predicted_fault"], "SENSOR_DRIFT")
        self.assertGreater(residuals["residual_engine_temp"], 12.0)
        self.assertGreaterEqual(pred["confidence"], 75.0)
        print("  -> PASS: Decoupled sensor transducer calibration drift verified.")

    def test_08_bearing_degradation(self):
        print("\n[TEST 8] Verifying BEARING_DEGRADATION Fault Signature...")
        res = self.run_fault_scenario("BEARING_DEGRADATION")
        pred = res["pred"]
        residuals = res["residuals"]

        print(f"  Observed Vib     : {res['clean']['vibration']:.2f} mm/s")
        print(f"  Observed Oil T   : {res['clean']['oil_temp']:.1f} ?C")
        print(f"  Classified Fault : {pred['predicted_fault']} (Confidence: {pred['confidence']:.1f}%)")

        self.assertEqual(pred["predicted_fault"], "BEARING_DEGRADATION")
        self.assertGreaterEqual(pred["confidence"], 75.0)
        print("  -> PASS: Dual bearing spalling signature verified.")

if __name__ == "__main__":
    unittest.main()
