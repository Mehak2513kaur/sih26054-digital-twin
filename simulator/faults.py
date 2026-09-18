import time
from typing import Dict, Any, List

class FaultManager:
    '''
    Manages 7 aerospace fault models with continuous progression.
    '''
    FAULT_TYPES = [
        "OVERHEATING",
        "MISFIRE",
        "OIL_PRESSURE_FAILURE",
        "VIBRATION_ANOMALY",
        "FUEL_SYSTEM_ANOMALY",
        "SENSOR_DRIFT",
        "BEARING_DEGRADATION"
    ]

    SEVERITY_LEVELS = {
        "LOW": 0.40,
        "MEDIUM": 0.75,
        "HIGH": 1.00
    }

    def __init__(self):
        self.active_fault: str = "NORMAL"
        self.severity_name: str = "NONE"
        self.target_severity: float = 0.0
        self.current_severity: float = 0.0
        self.ramp_duration: float = 20.0
        self.elapsed_sim_time: float = 0.0
        self.start_wall_time: float = 0.0
        self.fault_history: List[Dict[str, Any]] = []

    def inject(self, fault_type: str, severity: str = "MEDIUM", ramp_duration: float = 20.0):
        fault_type = fault_type.upper()
        severity = severity.upper()
        if fault_type not in self.FAULT_TYPES:
            raise ValueError(f"Invalid fault type: {fault_type}")
        
        self.active_fault = fault_type
        self.severity_name = severity
        self.target_severity = self.SEVERITY_LEVELS.get(severity, 0.75)
        self.ramp_duration = max(1.0, float(ramp_duration))
        self.start_wall_time = time.time()
        self.elapsed_sim_time = 0.0
        self.current_severity = 0.0
        
        event = {
            "timestamp": self.start_wall_time,
            "fault_type": fault_type,
            "severity": severity,
            "target_severity": self.target_severity,
            "action": "INJECTED"
        }
        self.fault_history.append(event)
        return event

    def clear(self):
        old_fault = self.active_fault
        self.active_fault = "NORMAL"
        self.severity_name = "NONE"
        self.target_severity = 0.0
        self.current_severity = 0.0
        self.elapsed_sim_time = 0.0
        event = {
            "timestamp": time.time(),
            "fault_type": old_fault,
            "action": "CLEARED"
        }
        self.fault_history.append(event)
        return event

    def update(self, dt: float, engine) -> Dict[str, float]:
        if self.active_fault != "NORMAL" and self.target_severity > 0:
            self.elapsed_sim_time += dt
            fraction = min(1.0, self.elapsed_sim_time / self.ramp_duration)
            self.current_severity = self.target_severity * fraction
        else:
            self.current_severity = max(0.0, self.current_severity - dt * 0.5)

        for k in engine.fault_modifiers:
            engine.fault_modifiers[k] = 0.0

        s = self.current_severity
        if self.active_fault == "OVERHEATING":
            engine.fault_modifiers["cooling_degradation"] = s
        elif self.active_fault == "MISFIRE":
            engine.fault_modifiers["misfire_intensity"] = s
        elif self.active_fault == "OIL_PRESSURE_FAILURE":
            engine.fault_modifiers["oil_leak_severity"] = s
        elif self.active_fault == "VIBRATION_ANOMALY":
            engine.fault_modifiers["mechanical_imbalance"] = s
        elif self.active_fault == "FUEL_SYSTEM_ANOMALY":
            engine.fault_modifiers["fuel_restriction"] = s
        elif self.active_fault == "SENSOR_DRIFT":
            engine.fault_modifiers["sensor_cht_drift"] = s * 34.0
        elif self.active_fault == "BEARING_DEGRADATION":
            engine.fault_modifiers["bearing_wear"] = s

        return {
            "active_fault": self.active_fault,
            "severity_name": self.severity_name,
            "current_severity": round(self.current_severity, 3),
            "target_severity": round(self.target_severity, 3),
            "ramp_progress": round(self.current_severity / max(0.01, self.target_severity) * 100, 1) if self.target_severity > 0 else 0.0
        }
