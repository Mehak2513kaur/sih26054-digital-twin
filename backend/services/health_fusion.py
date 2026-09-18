import math
from typing import Dict, Any

class HealthFusionEngine:
    '''
    Combines:
    1. Physics Residual Norm
    2. ML Anomaly Score
    3. Fault Classifier Confidence
    4. Rate-of-Change thermal & vibration stress
    to compute a single responsive 0 - 100 Digital Twin Health Score.
    '''
    def __init__(self):
        self.current_health: float = 96.0

    def calculate(
        self,
        physics_residuals: Dict[str, Any],
        ml_prediction: Dict[str, Any],
        derived_features: Dict[str, Any],
        fault_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        norm = physics_residuals.get("composite_residual_norm", 0.0)
        phys_penalty = min(35.0, max(0.0, (norm - 0.8) * 12.0))
        
        anomaly_intensity = ml_prediction.get("anomaly_intensity", 0.0)
        ml_penalty = (anomaly_intensity / 100.0) * 35.0
        
        predicted_fault = ml_prediction.get("predicted_fault", "NORMAL")
        confidence = ml_prediction.get("confidence", 0.0) / 100.0
        fault_penalty = 0.0
        if predicted_fault != "NORMAL":
            fault_penalty = confidence * 20.0
            
        temp_rate = abs(derived_features.get("temperature_rate", 0.0))
        vib_rate = abs(derived_features.get("vibration_rate", 0.0))
        rate_penalty = min(10.0, (temp_rate * 0.4) + (vib_rate * 1.5))
        
        raw_score = 100.0 - (phys_penalty + ml_penalty + fault_penalty + rate_penalty)
        raw_score = max(8.0, min(100.0, raw_score))
        
        self.current_health += (raw_score - self.current_health) * 0.25
        final_health = round(self.current_health, 1)

        if final_health >= 80.0:
            status = "HEALTHY"
            color = "#10b981"
        elif final_health >= 50.0:
            status = "DEGRADING"
            color = "#f59e0b"
        else:
            status = "CRITICAL"
            color = "#ef4444"

        return {
            "health_score": final_health,
            "status": status,
            "status_color": color,
            "penalties": {
                "physics_penalty": round(phys_penalty, 1),
                "ml_penalty": round(ml_penalty, 1),
                "fault_penalty": round(fault_penalty, 1),
                "rate_stress_penalty": round(rate_penalty, 1)
            }
        }
