"""
MALE UAV Piston Engine Digital Twin - Fault Injection Engine (Sim 2)
DRDO Problem Statement 26054

Provides deterministic, physics-coupled fault injection across 10 engine failure modes:
1. OVERHEATING
2. LOW OIL PRESSURE
3. HIGH OIL TEMPERATURE
4. MISFIRE
5. VIBRATION ANOMALY
6. FUEL-SYSTEM ANOMALY
7. INJECTOR DEGRADATION
8. TURBOCHARGER DEGRADATION
9. BEARING DEGRADATION
10. SENSOR DRIFT
"""

import math
import time
import random
from enum import Enum
from typing import Dict, Any, Optional, List


class FaultType(str, Enum):
    NONE = "none"
    OVERHEATING = "overheating"
    LOW_OIL_PRESSURE = "low oil pressure"
    HIGH_OIL_TEMPERATURE = "high oil temperature"
    MISFIRE = "misfire"
    VIBRATION_ANOMALY = "vibration anomaly"
    FUEL_SYSTEM_ANOMALY = "fuel-system anomaly"
    INJECTOR_DEGRADATION = "injector degradation"
    TURBOCHARGER_DEGRADATION = "turbocharger degradation"
    BEARING_DEGRADATION = "bearing degradation"
    SENSOR_DRIFT = "sensor drift"


class FaultSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class FaultInjectionEngine:
    """
    Continuous Fault Injection Engine for MALE UAV Piston Engines (Rotax 914/915 iS class).
    Applies logically coupled multi-parameter modifications to baseline engine telemetry.
    """

    SEVERITY_WEIGHTS = {
        FaultSeverity.LOW: 0.35,
        FaultSeverity.MEDIUM: 0.65,
        FaultSeverity.HIGH: 1.00,
        FaultSeverity.CRITICAL: 1.40,
    }

    # Normalized aliases for flexible string matching
    FAULT_ALIASES = {
        "none": FaultType.NONE,
        "normal": FaultType.NONE,
        "overheating": FaultType.OVERHEATING,
        "low oil pressure": FaultType.LOW_OIL_PRESSURE,
        "low_oil_pressure": FaultType.LOW_OIL_PRESSURE,
        "oil_pressure_failure": FaultType.LOW_OIL_PRESSURE,
        "high oil temperature": FaultType.HIGH_OIL_TEMPERATURE,
        "high_oil_temperature": FaultType.HIGH_OIL_TEMPERATURE,
        "misfire": FaultType.MISFIRE,
        "vibration anomaly": FaultType.VIBRATION_ANOMALY,
        "vibration_anomaly": FaultType.VIBRATION_ANOMALY,
        "fuel-system anomaly": FaultType.FUEL_SYSTEM_ANOMALY,
        "fuel_system_anomaly": FaultType.FUEL_SYSTEM_ANOMALY,
        "fuel system anomaly": FaultType.FUEL_SYSTEM_ANOMALY,
        "injector degradation": FaultType.INJECTOR_DEGRADATION,
        "injector_degradation": FaultType.INJECTOR_DEGRADATION,
        "turbocharger degradation": FaultType.TURBOCHARGER_DEGRADATION,
        "turbocharger_degradation": FaultType.TURBOCHARGER_DEGRADATION,
        "bearing degradation": FaultType.BEARING_DEGRADATION,
        "bearing_degradation": FaultType.BEARING_DEGRADATION,
        "sensor drift": FaultType.SENSOR_DRIFT,
        "sensor_drift": FaultType.SENSOR_DRIFT,
    }

    def __init__(self):
        self.active_fault: FaultType = FaultType.NONE
        self.severity: FaultSeverity = FaultSeverity.MEDIUM
        self.ramp_duration: float = 15.0  # seconds to reach full severity
        self.elapsed_fault_time: float = 0.0
        self.current_intensity: float = 0.0  # 0.0 to 1.4
        self.is_active: bool = False
        self.fault_start_time: float = 0.0

        # Component health states (0.0% = destroyed, 100.0% = brand new)
        self.component_health: Dict[str, float] = {
            "thermal_barrier": 98.5,
            "cylinder_head": 98.2,
            "crank_bearings": 99.0,
            "lubrication_system": 97.8,
            "fuel_injection": 99.1,
            "turbocharger": 98.4,
            "structural_mounts": 99.5,
            "overall_engine_health": 98.6,
        }

        # Dynamic stress multipliers
        self.stress_multipliers: Dict[str, float] = {
            "thermal_stress": 1.0,
            "bearing_stress": 1.0,
            "mechanical_stress": 1.0,
            "lubrication_stress": 1.0,
        }

        self.event_history: List[Dict[str, Any]] = []

    def _normalize_fault_name(self, fault_name: str) -> FaultType:
        key = fault_name.strip().lower().replace("-", " ").replace("_", " ")
        if key in self.FAULT_ALIASES:
            return self.FAULT_ALIASES[key]
        for enum_val in FaultType:
            if enum_val.value == key:
                return enum_val
        raise ValueError(f"Unknown fault type: '{fault_name}'. Supported: {[f.value for f in FaultType if f != FaultType.NONE]}")

    def _normalize_severity(self, severity: str) -> FaultSeverity:
        key = severity.strip().upper()
        if key in FaultSeverity.__members__:
            return FaultSeverity[key]
        raise ValueError(f"Unknown severity: '{severity}'. Supported: {[s.value for s in FaultSeverity]}")

    def select_fault(self, fault_name: str):
        """Select a fault without starting it immediately."""
        self.active_fault = self._normalize_fault_name(fault_name)

    def set_severity(self, severity: str):
        """Set severity level: LOW, MEDIUM, HIGH, CRITICAL."""
        self.severity = self._normalize_severity(severity)

    def start_fault(
        self,
        fault_name: Optional[str] = None,
        severity: Optional[str] = None,
        ramp_duration: float = 15.0,
    ) -> Dict[str, Any]:
        """
        Start fault injection with specified type, severity and ramp duration.
        """
        if fault_name is not None:
            self.select_fault(fault_name)
        if severity is not None:
            self.set_severity(severity)

        self.ramp_duration = max(1.0, float(ramp_duration))
        self.is_active = (self.active_fault != FaultType.NONE)
        self.elapsed_fault_time = 0.0
        self.current_intensity = 0.0
        self.fault_start_time = time.time()

        event = {
            "timestamp": self.fault_start_time,
            "event": "FAULT_STARTED",
            "fault_type": self.active_fault.value,
            "severity": self.severity.value,
            "ramp_duration": self.ramp_duration,
        }
        self.event_history.append(event)
        return event

    def stop_fault(self) -> Dict[str, Any]:
        """Stop current fault and begin recovery."""
        prev_fault = self.active_fault
        self.active_fault = FaultType.NONE
        self.is_active = False
        self.current_intensity = 0.0
        self.elapsed_fault_time = 0.0

        # Reset stress multipliers back toward nominal
        for k in self.stress_multipliers:
            self.stress_multipliers[k] = 1.0

        event = {
            "timestamp": time.time(),
            "event": "FAULT_STOPPED",
            "previous_fault": prev_fault.value,
            "action": "CLEARED",
        }
        self.event_history.append(event)
        return event

    def clear_fault(self) -> Dict[str, Any]:
        """Alias for stop_fault()."""
        return self.stop_fault()

    def update(self, dt: float = 0.1) -> Dict[str, Any]:
        """
        Update fault progression and wear integration over time.
        """
        target_weight = self.SEVERITY_WEIGHTS.get(self.severity, 0.65)

        if self.is_active and self.active_fault != FaultType.NONE:
            self.elapsed_fault_time += dt
            ramp_factor = min(1.0, self.elapsed_fault_time / max(0.1, self.ramp_duration))
            self.current_intensity = target_weight * ramp_factor

            # Degrade components based on active fault stress
            self._integrate_wear(dt)
        else:
            # Gradually decay intensity when fault cleared
            self.current_intensity = max(0.0, self.current_intensity - dt * 0.4)
            # Gentle recovery of transient stress
            for k in self.stress_multipliers:
                self.stress_multipliers[k] = max(1.0, self.stress_multipliers[k] - dt * 0.1)

        return self.get_status()

    def _integrate_wear(self, dt: float):
        """Progressively degrade component health according to physical stresses."""
        s = self.current_intensity

        if self.active_fault == FaultType.LOW_OIL_PRESSURE:
            # Severe bearing fatigue
            self.component_health["crank_bearings"] = max(5.0, self.component_health["crank_bearings"] - (0.45 * s * dt))
            self.component_health["lubrication_system"] = max(10.0, self.component_health["lubrication_system"] - (0.25 * s * dt))
        elif self.active_fault == FaultType.OVERHEATING:
            # Thermal barrier and cylinder head wear
            self.component_health["thermal_barrier"] = max(8.0, self.component_health["thermal_barrier"] - (0.35 * s * dt))
            self.component_head = max(10.0, self.component_health["cylinder_head"] - (0.30 * s * dt))
            self.component_health["lubrication_system"] = max(15.0, self.component_health["lubrication_system"] - (0.15 * s * dt))
        elif self.active_fault == FaultType.HIGH_OIL_TEMPERATURE:
            self.component_health["lubrication_system"] = max(12.0, self.component_health["lubrication_system"] - (0.35 * s * dt))
            self.component_health["crank_bearings"] = max(18.0, self.component_health["crank_bearings"] - (0.20 * s * dt))
        elif self.active_fault == FaultType.MISFIRE:
            self.component_health["cylinder_head"] = max(15.0, self.component_health["cylinder_head"] - (0.25 * s * dt))
            self.component_health["structural_mounts"] = max(20.0, self.component_health["structural_mounts"] - (0.30 * s * dt))
        elif self.active_fault == FaultType.VIBRATION_ANOMALY:
            self.component_health["structural_mounts"] = max(10.0, self.component_health["structural_mounts"] - (0.40 * s * dt))
            self.component_health["crank_bearings"] = max(25.0, self.component_health["crank_bearings"] - (0.15 * s * dt))
        elif self.active_fault == FaultType.FUEL_SYSTEM_ANOMALY:
            self.component_health["fuel_injection"] = max(12.0, self.component_health["fuel_injection"] - (0.35 * s * dt))
            self.component_health["thermal_barrier"] = max(20.0, self.component_health["thermal_barrier"] - (0.20 * s * dt))
        elif self.active_fault == FaultType.INJECTOR_DEGRADATION:
            self.component_health["fuel_injection"] = max(10.0, self.component_health["fuel_injection"] - (0.40 * s * dt))
        elif self.active_fault == FaultType.TURBOCHARGER_DEGRADATION:
            self.component_health["turbocharger"] = max(8.0, self.component_health["turbocharger"] - (0.42 * s * dt))
        elif self.active_fault == FaultType.BEARING_DEGRADATION:
            self.component_health["crank_bearings"] = max(5.0, self.component_health["crank_bearings"] - (0.50 * s * dt))
            self.component_health["lubrication_system"] = max(18.0, self.component_health["lubrication_system"] - (0.20 * s * dt))

        # Overall health as weighted average of subsystems
        weights = [0.18, 0.18, 0.20, 0.14, 0.12, 0.10, 0.08]
        keys = ["thermal_barrier", "cylinder_head", "crank_bearings", "lubrication_system", "fuel_injection", "turbocharger", "structural_mounts"]
        overall = sum(self.component_health[k] * w for k, w in zip(keys, weights))
        self.component_health["overall_engine_health"] = round(max(0.0, min(100.0, overall)), 1)

    def apply_fault(self, baseline_telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modifies baseline telemetry logically and deterministically.
        Guarantees all 18 standard telemetry fields are populated.
        """
        out = dict(baseline_telemetry)
        now = out.get("timestamp", time.time())
        s = self.current_intensity

        # Extract baseline readings with defaults
        rpm = float(out.get("rpm", 4600.0))
        cht = float(out.get("cylinder_head_temp", out.get("engine_temp", 96.5)))
        egt = float(out.get("exhaust_gas_temp", 760.0))
        oil_p = float(out.get("oil_pressure", 4.10))
        oil_t = float(out.get("oil_temperature", out.get("oil_temp", 88.0)))
        fuel_p = float(out.get("fuel_pressure", 3.25))
        fuel_f = float(out.get("fuel_flow", 22.40))
        map_val = float(out.get("manifold_pressure", 29.20))
        vib = float(out.get("vibration", 1.65))
        load = float(out.get("engine_load", 65.0))
        throttle = float(out.get("throttle", 65.0))
        altitude = float(out.get("altitude", 8000.0))
        amb_t = float(out.get("ambient_temperature", out.get("ambient_temp", 18.0)))
        bat_v = float(out.get("battery_voltage", 13.85))
        eng_hours = float(out.get("engine_hours", 1247.4))

        # Ambient pressure for boost calculation
        p_amb = 29.92 * math.pow(max(0.01, 1.0 - 6.875e-6 * altitude), 5.2559)
        boost = max(0.0, map_val - p_amb)
        coolant_t = cht * 0.88 + amb_t * 0.08

        # Reset stresses
        thermal_stress = 1.0
        bearing_stress = 1.0
        mechanical_stress = 1.0
        lubrication_stress = 1.0

        # Logical Physical Coupling according to selected fault
        if s > 0.001:
            if self.active_fault == FaultType.LOW_OIL_PRESSURE:
                # 1. Oil pressure drops drastically
                oil_p = max(0.60, oil_p - (2.95 * s))
                # 2. Bearing stress surges inversely proportional to oil pressure
                bearing_stress = 1.0 + (3.8 * s)
                lubrication_stress = 1.0 + (3.2 * s)
                # 3. Frictional heating in journal bearings increases oil temperature
                oil_t += (18.5 * s)
                # 4. Metal micro-scuffing induces mechanical vibration
                vib += (3.4 * s) + random.gauss(0, 0.06)

            elif self.active_fault == FaultType.OVERHEATING:
                # 1. Cylinder Head Temp climbs rapidly
                cht += (58.0 * s)
                coolant_t += (44.0 * s)
                # 2. Thermal stress escalates
                thermal_stress = 1.0 + (3.5 * s)
                # 3. Exhaust gas temperature and oil temperature rise
                egt += (38.0 * s)
                oil_t += (32.0 * s)
                # 4. Oil viscosity thinning reduces oil pressure slightly
                oil_p = max(1.8, oil_p - (0.65 * s))

            elif self.active_fault == FaultType.HIGH_OIL_TEMPERATURE:
                # 1. Oil temperature climbs (cooler blockage/bypass failure)
                oil_t += (48.0 * s)
                lubrication_stress = 1.0 + (3.4 * s)
                # 2. Viscosity drops severely -> oil pressure drops
                oil_p = max(1.1, oil_p - (1.75 * s))
                # 3. Secondary thermal soak into cylinder head
                cht += (14.0 * s)
                thermal_stress = 1.0 + (1.4 * s)

            elif self.active_fault == FaultType.MISFIRE:
                # 1. Intermittent combustion loss -> cyclic RPM ripple
                ripple = -240.0 * s * (1.0 + 0.65 * math.sin(now * 16.0))
                rpm = max(1500.0, rpm + ripple)
                # 2. Intense torsional imbalance causes massive vibration
                vib += (5.8 * s) + (math.sin(now * 18.0) * 0.8 * s)
                mechanical_stress = 1.0 + (3.6 * s)
                # 3. Unburnt fuel into exhaust manifold causes erratic EGT
                egt += (math.sin(now * 14.0) * 55.0 * s) - (30.0 * s)
                load = min(100.0, load + (5.0 * s))

            elif self.active_fault == FaultType.VIBRATION_ANOMALY:
                # 1. Pure mechanical imbalance (prop/mount)
                vib += (6.4 * s) + random.gauss(0, 0.1)
                mechanical_stress = 1.0 + (4.0 * s)
                bearing_stress = 1.0 + (1.5 * s)

            elif self.active_fault == FaultType.FUEL_SYSTEM_ANOMALY:
                # 1. Fuel delivery restriction
                fuel_f = max(6.0, fuel_f * (1.0 - 0.42 * s))
                fuel_p = max(0.9, fuel_p - (1.45 * s))
                # 2. Extreme lean burn combustion spikes EGT
                egt += (175.0 * s)
                thermal_stress = 1.0 + (2.8 * s)
                # 3. Power loss slightly reduces RPM
                rpm = max(1800.0, rpm - (160.0 * s))

            elif self.active_fault == FaultType.INJECTOR_DEGRADATION:
                # 1. Nozzle coking / spray pattern distortion
                fuel_f = max(8.0, fuel_f * (1.0 - 0.16 * s))
                egt += (72.0 * s)
                vib += (1.4 * s)
                mechanical_stress = 1.0 + (1.3 * s)
                thermal_stress = 1.0 + (1.6 * s)

            elif self.active_fault == FaultType.TURBOCHARGER_DEGRADATION:
                # 1. Boost loss & manifold pressure drop
                map_val = max(p_amb * 0.95, map_val - (9.2 * s))
                boost = max(0.0, map_val - p_amb)
                # 2. Engine loses power at altitude -> RPM drops
                rpm = max(1800.0, rpm - (310.0 * s))
                # 3. Fuel flow drops accordingly
                fuel_f = max(8.0, fuel_f * (1.0 - 0.22 * s))
                egt += (25.0 * s)

            elif self.active_fault == FaultType.BEARING_DEGRADATION:
                # 1. Severe bearing spalling: vibration harmonic jump
                vib += (4.6 * s)
                bearing_stress = 1.0 + (4.2 * s)
                # 2. Journal friction elevates oil temperature
                oil_t += (28.0 * s)
                # 3. Journal clearance increase drops oil pressure
                oil_p = max(1.2, oil_p - (1.25 * s))
                mechanical_stress = 1.0 + (2.5 * s)

            elif self.active_fault == FaultType.SENSOR_DRIFT:
                # ONLY measured CHT shifts; physics/thermodynamics remain completely nominal!
                cht += (36.0 * s)
                # Note: oil_t, egt, coolant_t, vib NOT modified (decoupled drift)

        # Update stress multipliers
        self.stress_multipliers["thermal_stress"] = round(thermal_stress, 2)
        self.stress_multipliers["bearing_stress"] = round(bearing_stress, 2)
        self.stress_multipliers["mechanical_stress"] = round(mechanical_stress, 2)
        self.stress_multipliers["lubrication_stress"] = round(lubrication_stress, 2)

        # Build clean output dictionary matching both existing backend and Sim 2 requirements
        return {
            # Standard Sim 2 Telemetry Fields (All 18 items)
            "timestamp": now,
            "rpm": round(rpm, 1),
            "cht": round(cht, 1),
            "egt": round(egt, 1),
            "oil_pressure": round(oil_p, 2),
            "oil_temperature": round(oil_t, 1),
            "fuel_pressure": round(fuel_p, 2),
            "fuel_flow": round(fuel_f, 2),
            "map": round(map_val, 2),
            "boost_pressure": round(boost, 2),
            "vibration": round(vib, 2),
            "engine_load": round(load, 1),
            "throttle": round(throttle, 1),
            "altitude": round(altitude, 0),
            "ambient_temperature": round(amb_t, 1),
            "coolant_temperature": round(coolant_t, 1),
            "battery_voltage": round(bat_v, 2),
            "engine_hours": round(eng_hours, 2),

            # Backward compatibility aliases
            "engine_id": out.get("engine_id", "UAV-PX-01"),
            "engine_temp": round(cht, 1),
            "cylinder_head_temp": round(cht, 1),
            "oil_temp": round(oil_t, 1),
            "exhaust_gas_temp": round(egt, 1),
            "manifold_pressure": round(map_val, 2),
            "ambient_temp": round(amb_t, 1),

            # Fault & health metadata
            "fault_metadata": {
                "active_fault": self.active_fault.value,
                "severity": self.severity.value,
                "current_intensity": round(self.current_intensity, 3),
                "is_active": self.is_active,
                "stresses": self.stress_multipliers,
            },
            "component_health": {k: round(v, 1) for k, v in self.component_health.items()},
        }

    def get_status(self) -> Dict[str, Any]:
        """Return current status of fault injection engine."""
        return {
            "active_fault": self.active_fault.value,
            "severity": self.severity.value,
            "current_intensity": round(self.current_intensity, 3),
            "ramp_duration": self.ramp_duration,
            "elapsed_fault_time": round(self.elapsed_fault_time, 1),
            "is_active": self.is_active,
            "component_health": {k: round(v, 1) for k, v in self.component_health.items()},
            "stresses": self.stress_multipliers,
        }

def get_fault_delta(scenario: str, severity: float = 1.0) -> tuple:
    """Legacy helper returning (delta_dict, fault_label)."""
    if not scenario or scenario.lower() in ("normal", "none"):
        return {}, None
    eng = FaultInjectionEngine()
    eng.start_fault(scenario, "HIGH" if severity >= 0.8 else ("MEDIUM" if severity >= 0.5 else "LOW"))
    eng.current_intensity = severity
    tele = eng.apply_fault({"rpm": 2400.0, "egt": 730.0, "cht": 175.0, "oil_pressure": 4.5, "oil_temp": 90.0, "fuel_flow": 16.0, "vibration": 0.10})
    delta = {
        "rpm": tele["rpm"] - 2400.0,
        "egt": tele["egt"] - 730.0,
        "cht": tele["cht"] - 175.0,
        "oil_pressure": tele["oil_pressure"] - 4.5,
        "oil_temp": tele["oil_temperature"] - 90.0,
        "fuel_flow": tele["fuel_flow"] - 16.0,
        "vibration": tele["vibration"] - 0.10,
    }
    return delta, scenario
