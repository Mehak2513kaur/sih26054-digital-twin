import os
import sys
import joblib
import json
import numpy as np
from pathlib import Path
from typing import Dict, Any

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from ml.rul import RULPredictor
from ml.explainability import ExplainabilityEngine

class EngineAIInference:
    '''
    Real-time inference pipeline:
    - Isolation Forest for anomaly detection
    - Random Forest for multi-class fault classification
    - Prognostic RUL calculation with measurable stress indicators
    - Explainable AI (XAI) feature attribution
    '''
    FEATURE_NAMES = [
        "rpm", "engine_temp", "oil_temp", "oil_pressure", "fuel_flow",
        "manifold_pressure", "exhaust_gas_temp", "vibration", "engine_load",
        "temperature_rate", "vibration_rate", "oil_pressure_rate",
        "residual_engine_temp", "residual_oil_pressure", "residual_vibration",
        "residual_exhaust_gas_temp", "composite_residual_norm"
    ]

    def __init__(self, models_dir: Path = None):
        if models_dir is None:
            models_dir = root_dir / "ml" / "models"
        self.models_dir = models_dir
        
        self.scaler = None
        self.isolation_forest = None
        self.fault_classifier = None
        self.metadata = None
        
        self.rul_predictor = RULPredictor(initial_rul=480.0)
        self.xai_engine = ExplainabilityEngine()
        
        self.load_models()

    def load_models(self):
        scaler_p = self.models_dir / "scaler.joblib"
        iso_p = self.models_dir / "isolation_forest.joblib"
        rf_p = self.models_dir / "fault_classifier.joblib"
        meta_p = self.models_dir / "metadata.json"
        
        if scaler_p.exists() and iso_p.exists() and rf_p.exists():
            try:
                self.scaler = joblib.load(scaler_p)
                self.isolation_forest = joblib.load(iso_p)
                self.fault_classifier = joblib.load(rf_p)
                if meta_p.exists():
                    self.metadata = json.loads(meta_p.read_text(encoding="utf-8"))
                print("ML models loaded successfully from disk.")
            except Exception as e:
                print(f"Error loading trained models: {e}.")
        else:
            print("Model weights not yet found. Training recommended.")

    def predict(
        self,
        telemetry: Dict[str, Any],
        residuals: Dict[str, Any],
        derived: Dict[str, Any],
        expected_physics: Dict[str, float]
    ) -> Dict[str, Any]:
        norm = residuals.get("composite_residual_norm", 0.8)
        res_temp = residuals.get("residual_engine_temp", 0.0)
        res_oil = residuals.get("residual_oil_pressure", 0.0)
        res_vib = residuals.get("residual_vibration", 0.0)
        res_egt = residuals.get("residual_exhaust_gas_temp", 0.0)
        res_fuel = residuals.get("residual_fuel_flow", 0.0)
        res_oil_t = residuals.get("residual_oil_temp", 0.0)

        raw_features = [
            telemetry.get("rpm", 4600.0),
            telemetry.get("engine_temp", 96.5),
            telemetry.get("oil_temp", 88.0),
            telemetry.get("oil_pressure", 4.10),
            telemetry.get("fuel_flow", 22.4),
            telemetry.get("manifold_pressure", 29.2),
            telemetry.get("exhaust_gas_temp", 760.0),
            telemetry.get("vibration", 1.65),
            telemetry.get("engine_load", 65.0),
            derived.get("temperature_rate", 0.0),
            derived.get("vibration_rate", 0.0),
            derived.get("oil_pressure_rate", 0.0),
            res_temp,
            res_oil,
            res_vib,
            res_egt,
            norm
        ]
        
        X = np.array([raw_features])
        predicted_fault = "NORMAL"
        confidence = 95.0
        anomaly_intensity = 0.0
        is_anomaly = False

        if self.scaler is not None and self.isolation_forest is not None and self.fault_classifier is not None:
            try:
                X_scaled = self.scaler.transform(X)
                # Decision function: lower is more anomalous
                iso_score = self.isolation_forest.decision_function(X_scaled)[0]
                raw_intensity = float(np.clip((0.10 - iso_score) * 220.0, 0.0, 100.0))
                
                # Fuse residual norm into anomaly intensity
                residual_boost = max(0.0, (norm - 1.2) * 25.0)
                anomaly_intensity = min(100.0, max(raw_intensity, residual_boost))

                # Supervised classifier
                probs = self.fault_classifier.predict_proba(X_scaled)[0]
                classes = self.fault_classifier.classes_
                top_idx = int(np.argmax(probs))
                predicted_fault = str(classes[top_idx])
                confidence = float(probs[top_idx] * 100.0)

                # Physical consistency check: If residuals are nominal, enforce NORMAL
                if norm < 1.35 and abs(res_temp) < 5.0 and abs(res_oil) < 0.35 and abs(res_vib) < 0.6:
                    predicted_fault = "NORMAL"
                    confidence = max(92.0, confidence)
                    anomaly_intensity = min(22.0, anomaly_intensity)
                    is_anomaly = False
                else:
                    # When fault is identified or residuals exceed 2.0 sigma, set anomaly true
                    is_anomaly = anomaly_intensity > 32.0 or predicted_fault != "NORMAL" or norm > 2.0
                    if predicted_fault != "NORMAL":
                        anomaly_intensity = max(55.0, anomaly_intensity)

            except Exception:
                pass

        # Robust rule-based fallback if models not loaded or in case of ambiguity
        if self.fault_classifier is None or confidence < 45.0:
            if res_temp > 7.0 and res_oil_t > 4.0:
                predicted_fault = "OVERHEATING"
                confidence = 92.0
                anomaly_intensity = 82.0
                is_anomaly = True
            elif res_vib > 3.0 and telemetry.get("rpm", 4600) < 4450:
                predicted_fault = "MISFIRE"
                confidence = 88.0
                anomaly_intensity = 80.0
                is_anomaly = True
            elif res_oil < -0.7:
                predicted_fault = "OIL_PRESSURE_FAILURE"
                confidence = 94.0
                anomaly_intensity = 90.0
                is_anomaly = True
            elif res_vib > 3.5 and abs(res_temp) < 4.0:
                predicted_fault = "VIBRATION_ANOMALY"
                confidence = 91.0
                anomaly_intensity = 85.0
                is_anomaly = True
            elif res_fuel < -4.0 and res_egt > 45.0:
                predicted_fault = "FUEL_SYSTEM_ANOMALY"
                confidence = 89.0
                anomaly_intensity = 78.0
                is_anomaly = True
            elif res_temp > 12.0 and abs(res_oil_t) < 3.0 and abs(res_egt) < 15.0:
                predicted_fault = "SENSOR_DRIFT"
                confidence = 87.0
                anomaly_intensity = 72.0
                is_anomaly = True
            elif res_vib > 1.8 and res_oil_t > 8.0:
                predicted_fault = "BEARING_DEGRADATION"
                confidence = 86.0
                anomaly_intensity = 75.0
                is_anomaly = True
            else:
                predicted_fault = "NORMAL"
                confidence = 95.0
                anomaly_intensity = max(0.0, (norm - 0.7) * 15.0)
                is_anomaly = False

        # RUL estimation with measurable physical stress indicators
        rul_data = self.rul_predictor.estimate(
            engine_hours=telemetry.get("engine_hours", 1247.4),
            anomaly_intensity=anomaly_intensity,
            physics_residuals=residuals,
            derived_features=derived,
            telemetry=telemetry,
            predicted_fault=predicted_fault
        )

        # Explainable AI (XAI) Attribution
        xai_data = self.xai_engine.explain(
            predicted_fault=predicted_fault,
            confidence=confidence,
            physics_residuals=residuals,
            derived_features=derived,
            cleaned_telemetry=telemetry,
            expected_physics=expected_physics
        )

        return {
            "is_anomaly": is_anomaly,
            "anomaly_intensity": round(anomaly_intensity, 1),
            "predicted_fault": predicted_fault,
            "confidence": round(confidence, 1),
            "rul": rul_data,
            "explainability": xai_data
        }
