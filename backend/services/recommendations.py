from typing import Dict, Any

class RecommendationEngine:
    '''
    Defense engineering maintenance recommendations engine.
    Produces actionable protocols based on predicted failure modes and severity.
    '''
    RECOMMENDATIONS = {
        "OVERHEATING": {
            "title": "Cooling System Thermal Runaway Alert",
            "action": "Immediately reduce engine load by 20-30%. Enrich fuel mixture and pitch down to increase dynamic ram-air cooling. Inspect radiator coolant level, thermostat valve bypass, and cylinder cooling fins upon recovery.",
            "urgency": "CRITICAL"
        },
        "MISFIRE": {
            "title": "Cylinder Misfire & Combustion Instability Alert",
            "action": "Cross-check dual electronic ignition channels (ECU A vs ECU B). Verify fuel injection manifold delivery pressure and check for spark plug electrode fouling. Avoid high-power loiter maneuvers.",
            "urgency": "WARNING"
        },
        "OIL_PRESSURE_FAILURE": {
            "title": "Lubrication Hydraulic Pressure Deficit Alert",
            "action": "Descend to minimum safe altitude and establish precautionary return-to-base (RTB) heading. Monitor oil temperature climb. Avoid high-G maneuvers to minimize bearing starvation risk.",
            "urgency": "CRITICAL"
        },
        "VIBRATION_ANOMALY": {
            "title": "Drivetrain & Propeller Mechanical Imbalance Alert",
            "action": "Throttle back to minimum steady cruise RPM to escape harmonic resonance. Post-flight: inspect propeller blade pitch alignment, spinner dynamic balance, and elastomeric engine mount bushings.",
            "urgency": "WARNING"
        },
        "FUEL_SYSTEM_ANOMALY": {
            "title": "Fuel Delivery Restriction / Lean Condition Alert",
            "action": "Activate secondary auxiliary fuel boost pump. Inspect fuel rail differential pressure sensor and filter mesh. Closely monitor EGT to prevent piston crown detonation from lean combustion.",
            "urgency": "WARNING"
        },
        "SENSOR_DRIFT": {
            "title": "Avionics Sensor Calibration Drift Alert",
            "action": "Cross-validate telemetry against redundant secondary CHT/MAP analog transducers. Invalidate drifted channel in autonomous flight control computer to prevent false throttle modulation.",
            "urgency": "INFO"
        },
        "BEARING_DEGRADATION": {
            "title": "Crankshaft / Turbocharger Bearing Spalling Alert",
            "action": "Limit peak turbocharger boost pressure. Upon landing, perform magnetic chip detector inspection and spectroscopic oil analysis for copper-lead particulate accumulation.",
            "urgency": "WARNING"
        },
        "NORMAL": {
            "title": "Nominal Engine Operating Envelope",
            "action": "All engine thermodynamic and mechanical parameters within manufacturer tolerance. Continue designated flight plan.",
            "urgency": "INFO"
        }
    }

    def get_recommendation(self, fault_class: str, severity: str = "MEDIUM") -> Dict[str, Any]:
        fault_class = fault_class.upper()
        rec = self.RECOMMENDATIONS.get(fault_class, self.RECOMMENDATIONS["NORMAL"])
        urgency = "CRITICAL" if severity == "HIGH" and fault_class != "NORMAL" else rec["urgency"]
        return {
            "fault_class": fault_class,
            "title": rec["title"],
            "recommended_action": rec["action"],
            "urgency": urgency,
            "disclaimer": "Simulated prototype guidance for DRDO PS 26054 demonstration."
        }
