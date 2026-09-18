import math
from typing import Dict, Any

class ResidualCalculator:
    '''
    Calculates Observed vs Expected Digital Twin residuals for all 8 core parameters:
    CHT, Oil Temperature, Oil Pressure, EGT, MAP, Fuel Flow, RMS Vibration, and RPM.
    For each parameter:
    - Observed
    - Expected
    - Residual (Observed - Expected)
    - Normalized Residual / Z-score (Residual / Sigma)
    - Status: ALIGNED (|Z| <= 1.8), WARNING (1.8 < |Z| <= 3.0), DIVERGENT (|Z| > 3.0)
    '''
    SIGMAS = {
        "cht": 2.2,
        "oil_temp": 1.8,
        "oil_pressure": 0.12,
        "egt": 8.5,
        "map": 0.45,
        "fuel_flow": 0.65,
        "vibration": 0.18,
        "rpm": 35.0
    }

    def _eval_status(self, z_score: float) -> str:
        abs_z = abs(z_score)
        if abs_z > 3.0:
            return "DIVERGENT"
        elif abs_z > 1.8:
            return "WARNING"
        return "ALIGNED"

    def calculate(self, observed: Dict[str, Any], expected: Dict[str, float]) -> Dict[str, Any]:
        obs_cht = observed.get("engine_temp", observed.get("cylinder_head_temp", 96.5))
        exp_cht = expected.get("expected_engine_temp", 96.5)
        res_cht = obs_cht - exp_cht
        z_cht = res_cht / self.SIGMAS["cht"]

        obs_oil_temp = observed.get("oil_temp", 88.0)
        exp_oil_temp = expected.get("expected_oil_temp", 88.0)
        res_oil_temp = obs_oil_temp - exp_oil_temp
        z_oil_temp = res_oil_temp / self.SIGMAS["oil_temp"]

        obs_oil_press = observed.get("oil_pressure", 4.10)
        exp_oil_press = expected.get("expected_oil_pressure", 4.10)
        res_oil_press = obs_oil_press - exp_oil_press
        z_oil_press = res_oil_press / self.SIGMAS["oil_pressure"]

        obs_egt = observed.get("exhaust_gas_temp", 760.0)
        exp_egt = expected.get("expected_exhaust_gas_temp", 760.0)
        res_egt = obs_egt - exp_egt
        z_egt = res_egt / self.SIGMAS["egt"]

        obs_map = observed.get("manifold_pressure", 29.20)
        exp_map = expected.get("expected_manifold_pressure", 29.20)
        res_map = obs_map - exp_map
        z_map = res_map / self.SIGMAS["map"]

        obs_fuel = observed.get("fuel_flow", 22.40)
        exp_fuel = expected.get("expected_fuel_flow", 22.40)
        res_fuel = obs_fuel - exp_fuel
        z_fuel = res_fuel / self.SIGMAS["fuel_flow"]

        obs_vib = observed.get("vibration", 1.65)
        exp_vib = expected.get("expected_vibration", 1.65)
        res_vib = obs_vib - exp_vib
        z_vib = res_vib / self.SIGMAS["vibration"]

        obs_rpm = observed.get("rpm", 4600.0)
        exp_rpm = expected.get("expected_rpm", 4600.0)
        res_rpm = obs_rpm - exp_rpm
        z_rpm = res_rpm / self.SIGMAS["rpm"]

        # 8 Core Structured Parameters Table
        parameters = {
            "cht": {
                "name": "Cylinder Head Temp (CHT)",
                "unit": "°C",
                "observed": round(obs_cht, 1),
                "expected": round(exp_cht, 1),
                "residual": round(res_cht, 2),
                "z_score": round(z_cht, 2),
                "status": self._eval_status(z_cht)
            },
            "oil_temp": {
                "name": "Oil Temperature",
                "unit": "°C",
                "observed": round(obs_oil_temp, 1),
                "expected": round(exp_oil_temp, 1),
                "residual": round(res_oil_temp, 2),
                "z_score": round(z_oil_temp, 2),
                "status": self._eval_status(z_oil_temp)
            },
            "oil_pressure": {
                "name": "Oil Pressure",
                "unit": "bar",
                "observed": round(obs_oil_press, 2),
                "expected": round(exp_oil_press, 2),
                "residual": round(res_oil_press, 2),
                "z_score": round(z_oil_press, 2),
                "status": self._eval_status(z_oil_press)
            },
            "egt": {
                "name": "Exhaust Gas Temp (EGT)",
                "unit": "°C",
                "observed": round(obs_egt, 1),
                "expected": round(exp_egt, 1),
                "residual": round(res_egt, 2),
                "z_score": round(z_egt, 2),
                "status": self._eval_status(z_egt)
            },
            "map": {
                "name": "Manifold Pressure (MAP)",
                "unit": "inHg",
                "observed": round(obs_map, 2),
                "expected": round(exp_map, 2),
                "residual": round(res_map, 2),
                "z_score": round(z_map, 2),
                "status": self._eval_status(z_map)
            },
            "fuel_flow": {
                "name": "Fuel Flow",
                "unit": "L/h",
                "observed": round(obs_fuel, 2),
                "expected": round(exp_fuel, 2),
                "residual": round(res_fuel, 2),
                "z_score": round(z_fuel, 2),
                "status": self._eval_status(z_fuel)
            },
            "vibration": {
                "name": "RMS Vibration",
                "unit": "mm/s",
                "observed": round(obs_vib, 2),
                "expected": round(exp_vib, 2),
                "residual": round(res_vib, 2),
                "z_score": round(z_vib, 2),
                "status": self._eval_status(z_vib)
            },
            "rpm": {
                "name": "Engine Speed (RPM)",
                "unit": "RPM",
                "observed": round(obs_rpm, 1),
                "expected": round(exp_rpm, 1),
                "residual": round(res_rpm, 1),
                "z_score": round(z_rpm, 2),
                "status": self._eval_status(z_rpm)
            }
        }

        # Composite residual norm across all 8 parameters
        norm_sq = (z_cht**2 + z_oil_temp**2 + z_oil_press**2 + z_egt**2 + z_map**2 + z_fuel**2 + z_vib**2 + z_rpm**2) / 8.0
        composite_norm = math.sqrt(max(0.0, norm_sq))

        return {
            "residual_engine_temp": round(res_cht, 2),
            "residual_oil_temp": round(res_oil_temp, 2),
            "residual_oil_pressure": round(res_oil_press, 2),
            "residual_fuel_flow": round(res_fuel, 2),
            "residual_manifold_pressure": round(res_map, 2),
            "residual_exhaust_gas_temp": round(res_egt, 2),
            "residual_vibration": round(res_vib, 2),
            "residual_rpm": round(res_rpm, 1),
            "z_scores": {
                "temp": round(z_cht, 2),
                "oil_temp": round(z_oil_temp, 2),
                "oil_press": round(z_oil_press, 2),
                "egt": round(z_egt, 2),
                "map": round(z_map, 2),
                "fuel": round(z_fuel, 2),
                "vib": round(z_vib, 2),
                "rpm": round(z_rpm, 2)
            },
            "composite_residual_norm": round(composite_norm, 2),
            "parameters": parameters
        }
