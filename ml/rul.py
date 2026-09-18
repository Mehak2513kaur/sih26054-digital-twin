import math
from typing import Dict, Any

class RULPredictor:
    '''
    Physics-Guided Prognostic Remaining Useful Life (RUL) Model
    Calibrated against a nominal 500-hour Time-Between-Overhaul (TBO) design envelope.
    Derives degradation index from measurable stress indicators:
    - Accumulated operating hours
    - CHT thermal exceedance & rate of rise
    - Mechanical RMS vibration stress
    - Hydraulic oil pressure deficit
    - EGT combustion temperature stress
    - Cumulative engine load
    - ML anomaly intensity
    '''
    NOMINAL_TBO = 500.0

    def __init__(self, initial_rul: float = 480.0):
        self.current_rul = initial_rul
        self.initial_rul = initial_rul
        self.smooth_degradation_index = 8.5

    def estimate(
        self,
        engine_hours: float,
        anomaly_intensity: float,
        physics_residuals: Dict[str, Any],
        derived_features: Dict[str, Any],
        telemetry: Dict[str, Any],
        predicted_fault: str
    ) -> Dict[str, Any]:
        # 1. Base wear from operational engine hours
        hours_in_cycle = engine_hours % self.NOMINAL_TBO
        base_wear = min(35.0, (hours_in_cycle / self.NOMINAL_TBO) * 30.0)

        # 2. Measurable Stress Indicators
        cht = telemetry.get("engine_temp", 96.5)
        oil_p = telemetry.get("oil_pressure", 4.10)
        vib = telemetry.get("vibration", 1.65)
        egt = telemetry.get("exhaust_gas_temp", 760.0)
        load = telemetry.get("engine_load", 65.0)

        z_scores = physics_residuals.get("z_scores", {})
        z_temp = abs(z_scores.get("temp", 0.0))
        z_oil = max(0.0, -z_scores.get("oil_press", 0.0))
        z_vib = abs(z_scores.get("vib", 0.0))
        z_egt = max(0.0, z_scores.get("egt", 0.0))

        # Thermal stress
        s_temp = min(22.0, max(0.0, cht - 102.0) * 0.70 + z_temp * 1.8)
        # Vibration stress
        s_vib = min(20.0, max(0.0, vib - 2.2) * 3.5 + z_vib * 1.5)
        # Lubrication hydraulic deficit
        s_oil = min(25.0, max(0.0, 3.2 - oil_p) * 11.0 + z_oil * 2.2)
        # EGT thermal stress
        s_egt = min(12.0, max(0.0, egt - 785.0) * 0.22 + z_egt * 1.0)
        # High load fatigue
        s_load = min(8.0, max(0.0, load - 75.0) * 0.35)
        # Anomaly intensity contribution
        s_anomaly = (anomaly_intensity / 100.0) * 15.0

        if predicted_fault != "NORMAL":
            s_anomaly += 8.0

        raw_deg_index = base_wear + s_temp + s_vib + s_oil + s_egt + s_load + s_anomaly
        raw_deg_index = max(4.0, min(96.0, raw_deg_index))

        # Smooth degradation index
        self.smooth_degradation_index += (raw_deg_index - self.smooth_degradation_index) * 0.20
        deg_index = round(self.smooth_degradation_index, 1)

        # 3. Calculate Remaining Useful Life (RUL in hours)
        remaining_ratio = max(0.03, 1.0 - (deg_index / 100.0))
        target_rul = max(15.0, self.NOMINAL_TBO * math.pow(remaining_ratio, 1.35))
        
        self.current_rul += (target_rul - self.current_rul) * 0.18
        final_rul = round(self.current_rul, 1)

        # 4. Degradation Velocity (%/hr)
        excess_stress = max(0.0, deg_index - 10.0)
        deg_velocity = round(0.20 + (excess_stress / 90.0) * 12.5, 2)

        # 5. Confidence Interval (± hours)
        margin = max(5.0, final_rul * 0.07 + (excess_stress * 0.12))
        lower_bound = round(max(5.0, final_rul - margin), 1)
        upper_bound = round(final_rul + margin, 1)
        confidence_pct = round(max(70.0, 96.0 - (deg_index * 0.25)), 1)

        # 6. Component-Level Wear Breakdown
        thermal_wear = min(98.0, base_wear + s_temp * 2.8)
        bearing_wear = min(98.0, base_wear + s_vib * 2.5 + s_oil * 1.5)
        lube_wear = min(98.0, base_wear + s_oil * 3.0)
        fuel_sys_wear = min(98.0, base_wear + s_egt * 2.5)

        return {
            "degradation_index": deg_index,
            "rul_hours": final_rul,
            "initial_rul": self.initial_rul,
            "degradation_velocity": deg_velocity,
            "degradation_rate_pct": deg_velocity,
            "confidence_pct": confidence_pct,
            "confidence_interval": {
                "lower": lower_bound,
                "upper": upper_bound
            },
            "measurable_indicators": {
                "thermal_stress": round(s_temp, 1),
                "vibration_stress": round(s_vib, 1),
                "oil_pressure_deficit": round(s_oil, 1),
                "egt_stress": round(s_egt, 1),
                "cumulative_load": round(s_load, 1),
                "anomaly_influence": round(s_anomaly, 1),
                "operating_hours_wear": round(base_wear, 1)
            },
            "component_wear_pct": {
                "thermal_barrier": round(thermal_wear, 1),
                "crank_bearings": round(bearing_wear, 1),
                "lubrication_system": round(lube_wear, 1),
                "fuel_injection": round(fuel_sys_wear, 1)
            },
            "label": "PROTOTYPE / SIMULATED RUL ESTIMATE",
            "disclaimer": "Simulated prototype estimate for DRDO demonstration. Not validated military data."
        }
