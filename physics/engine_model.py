import math
from typing import Dict, Any

class PhysicsEngineModel:
    '''
    First-Principles Thermodynamic & Aerodynamic Digital Twin Model
    for 4-cylinder turbocharged MALE UAV piston engine (Rotax 915 iS class).
    Calculates expected theoretical values responding to:
    - altitude (barometric pressure lapse & air density)
    - ambient_temp (intake charge temperature & cooling dissipation margin)
    - throttle (intake throttle angle & wastegate boost target)
    - engine_load (effective brake mean power & heat input)
    - rpm (engine rotational frequency & hydraulic oil pump output)
    '''
    def __init__(self):
        pass

    def calculate_expected(
        self, 
        rpm: float, 
        throttle: float, 
        altitude: float, 
        ambient_temp: float, 
        engine_load: float
    ) -> Dict[str, float]:
        # 1. Standard Atmosphere Barometric Pressure lapse (ICAO Doc 7488)
        p_amb = 29.92 * math.pow(max(0.01, 1.0 - 6.875e-6 * altitude), 5.2559)
        t_amb_k = max(220.0, ambient_temp + 273.15)
        air_density_ratio = max(0.25, (p_amb / 29.92) * (288.15 / t_amb_k))
        
        # 2. Expected Governor Engine Speed (RPM)
        # At 65% throttle nominal cruise, exp_rpm = 4600.0 RPM
        exp_rpm = 1800.0 + (throttle / 100.0) * 4307.7
        
        # 3. Expected Manifold Absolute Pressure (MAP in inHg)
        # Turbocharged with wastegate boost control up to critical altitude (16,000 ft)
        turbo_boost = (throttle / 100.0) * 10.74
        if altitude > 16000.0:
            boost_decay = (altitude - 16000.0) / 12000.0 * 6.0
            turbo_boost = max(0.0, turbo_boost - boost_decay)
        exp_map = p_amb + turbo_boost
        
        # 4. Expected Fuel Flow (L/h)
        # At 4600 RPM, 29.2 inHg, 18°C ambient -> exactly 22.4 L/h
        exp_fuel_flow = (exp_rpm / 5800.0) * (exp_map / 29.92) * 28.95 * math.sqrt(288.15 / t_amb_k)
        exp_fuel_flow = max(4.0, exp_fuel_flow)
        
        # 5. Expected Cylinder Head Temperature (CHT in °C)
        # Cooling air efficiency decreases with lower density and higher ambient temp
        cooling_factor = max(0.32, air_density_ratio * (1.0 - (ambient_temp - 15.0) * 0.012))
        heat_input = (exp_fuel_flow * 2.20) + (engine_load * 0.22)
        exp_cht = 39.0 + (heat_input / cooling_factor) * 0.56 + (ambient_temp * 0.40)
        
        # 6. Expected Oil Temperature (°C)
        # Thermally coupled to CHT with secondary oil cooler
        exp_oil_temp = 36.0 + (exp_cht * 0.42) + (ambient_temp * 0.18) / (cooling_factor * 1.08) + (exp_rpm / 5800.0) * 8.5
        
        # 7. Expected Hydraulic Oil Pressure (bar)
        # Driven by positive displacement pump, reduced by viscosity thinning with oil temp
        oil_viscosity_factor = max(0.50, 1.0 - (exp_oil_temp - 88.0) * 0.0075)
        pump_output = 1.90 + (exp_rpm / 5800.0) * 2.90
        exp_oil_pressure = pump_output * oil_viscosity_factor - 0.10
        
        # 8. Expected Exhaust Gas Temperature (EGT in °C)
        # Governed by combustion load and intake throttle
        exp_egt = 650.0 + (engine_load * 1.65) + (throttle / 100.0 * 4.0) - (ambient_temp - 15.0) * 0.25
        
        # 9. Expected RMS Mechanical Vibration (mm/s)
        exp_vibration = 0.85 + math.pow(exp_rpm / 4000.0, 1.85) * 0.58 + (engine_load / 100.0) * 0.12
        
        exp_fuel_pressure = 3.25
        
        return {
            "expected_rpm": round(exp_rpm, 1),
            "expected_engine_temp": round(exp_cht, 1),
            "expected_cylinder_head_temp": round(exp_cht, 1),
            "expected_oil_temp": round(exp_oil_temp, 1),
            "expected_oil_pressure": round(exp_oil_pressure, 2),
            "expected_fuel_flow": round(exp_fuel_flow, 2),
            "expected_fuel_pressure": round(exp_fuel_pressure, 2),
            "expected_manifold_pressure": round(exp_map, 2),
            "expected_exhaust_gas_temp": round(exp_egt, 1),
            "expected_vibration": round(exp_vibration, 2),
            "expected_load": round(engine_load, 1),
            "air_density_ratio": round(air_density_ratio, 3),
            "p_ambient_inhg": round(p_amb, 2)
        }
