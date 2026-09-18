import math
import random
import time
from typing import Dict, Any

class UAVPistonEngine:
    '''
    Thermodynamically coupled simulation of a MALE UAV 4-cylinder turbocharged 
    piston aircraft engine (Rotax 914 / 915 iS class).
    '''
    def __init__(self, engine_id: str = "UAV-PX-01", initial_hours: float = 1247.4):
        self.engine_id = engine_id
        self.engine_hours = initial_hours
        
        # Operational setpoints
        self.throttle = 65.0       # percent (0 - 100)
        self.altitude = 8000.0     # feet
        self.ambient_temp = 18.0   # Celsius
        self.engine_load = 65.0    # percent
        
        # State variables matching theoretical equilibrium at baseline cruise
        self.rpm = 4600.0
        self.cht = 96.5            # Cylinder Head Temp (°C)
        self.oil_temp = 88.0       # Oil Temp (°C)
        self.oil_pressure = 4.10   # Oil Pressure (bar)
        self.fuel_flow = 22.40     # Fuel Flow (L/h)
        self.fuel_pressure = 3.25  # Fuel Pressure (bar)
        self.manifold_pressure = 29.20 # MAP (inHg)
        self.egt = 760.0           # Exhaust Gas Temp (°C)
        self.vibration = 1.65      # RMS Vibration (mm/s)
        self.battery_voltage = 13.85 # Volts
        
        # Thermal inertia tracking
        self._target_cht = 96.5
        self._target_oil_temp = 88.0
        self._thermal_tau = 6.0    # Thermal time constant in seconds
        
        # Degradation & fault modifiers
        self.fault_modifiers: Dict[str, float] = {
            "cooling_degradation": 0.0,
            "misfire_intensity": 0.0,
            "oil_leak_severity": 0.0,
            "mechanical_imbalance": 0.0,
            "fuel_restriction": 0.0,
            "sensor_cht_drift": 0.0,
            "bearing_wear": 0.0,
        }
        self.last_update = time.time()

    def set_conditions(self, throttle: float = None, altitude: float = None, ambient_temp: float = None):
        if throttle is not None:
            self.throttle = max(0.0, min(100.0, float(throttle)))
        if altitude is not None:
            self.altitude = max(0.0, min(30000.0, float(altitude)))
        if ambient_temp is not None:
            self.ambient_temp = max(-40.0, min(60.0, float(ambient_temp)))

    def step(self, dt: float = 0.1) -> Dict[str, Any]:
        now = time.time()
        self.engine_hours += dt / 3600.0
        
        # 1. Barometric ambient pressure as a function of altitude
        p_amb = 29.92 * math.pow(max(0.01, 1.0 - 6.875e-6 * self.altitude), 5.2559)
        t_amb_k = max(220.0, self.ambient_temp + 273.15)
        air_density_ratio = max(0.25, (p_amb / 29.92) * (288.15 / t_amb_k))
        
        # 2. RPM dynamics based on throttle, governor, and misfire
        target_rpm = 1800.0 + (self.throttle / 100.0) * 4307.7
        misfire = self.fault_modifiers.get("misfire_intensity", 0.0)
        if misfire > 0:
            rpm_ripple = -260.0 * misfire * (1.0 + 0.7 * math.sin(now * 18.0))
            target_rpm += rpm_ripple
            
        self.rpm += (target_rpm - self.rpm) * min(1.0, dt * 4.0) + random.gauss(0, 1.8)
        self.rpm = max(1200.0, min(6200.0, self.rpm))
        
        # 3. Engine Load
        base_load = (self.throttle * 0.65) + (self.rpm / 5800.0 * 35.0)
        self.engine_load = max(10.0, min(100.0, base_load + random.gauss(0, 0.2)))
        
        # 4. Manifold Absolute Pressure (MAP) - Turbocharged with wastegate
        turbo_boost = (self.throttle / 100.0) * 10.74
        if self.altitude > 16000.0:
            boost_decay = (self.altitude - 16000.0) / 12000.0 * 6.0
            turbo_boost = max(0.0, turbo_boost - boost_decay)
        map_ideal = p_amb + turbo_boost
        self.manifold_pressure = max(15.0, min(45.0, map_ideal + random.gauss(0, 0.04)))
        
        # 5. Fuel Flow (L/h)
        fuel_res = self.fault_modifiers.get("fuel_restriction", 0.0)
        ideal_fuel_flow = (self.rpm / 5800.0) * (self.manifold_pressure / 29.92) * 28.95 * math.sqrt(288.15 / t_amb_k)
        actual_fuel_flow = ideal_fuel_flow * (1.0 - 0.40 * fuel_res)
        self.fuel_flow = max(4.0, actual_fuel_flow + random.gauss(0, 0.06))
        
        # Fuel pressure (bar)
        base_fuel_press = 3.25 - (fuel_res * 1.3)
        self.fuel_pressure = max(0.8, min(4.5, base_fuel_press + random.gauss(0, 0.01)))
        
        # 6. Thermal Dynamics (CHT & Oil Temp)
        cooling_factor = max(0.32, air_density_ratio * (1.0 - (self.ambient_temp - 15.0) * 0.012))
        cooling_deg = self.fault_modifiers.get("cooling_degradation", 0.0)
        cooling_factor *= max(0.15, (1.0 - cooling_deg * 0.85))
        
        heat_input = (self.fuel_flow * 2.20) + (self.engine_load * 0.22)
        base_target_cht = 39.0 + (heat_input / cooling_factor) * 0.56 + (self.ambient_temp * 0.40)
        
        # Fault thermal impacts
        self._target_cht = base_target_cht + (cooling_deg * 38.0)
        bearing_wear = self.fault_modifiers.get("bearing_wear", 0.0)
        self._target_cht += bearing_wear * 12.0
        
        self.cht += (self._target_cht - self.cht) * min(1.0, dt / self._thermal_tau * 2.5) + random.gauss(0, 0.04)
        
        # Sensor drift applies ONLY to measured CHT
        cht_drift = self.fault_modifiers.get("sensor_cht_drift", 0.0)
        measured_cht = self.cht + cht_drift
        
        # Oil Temperature
        base_target_oil = 36.0 + (self.cht * 0.42) + (self.ambient_temp * 0.18) / (cooling_factor * 1.08) + (self.rpm / 5800.0) * 8.5
        self._target_oil_temp = base_target_oil + (cooling_deg * 25.0) + (bearing_wear * 24.0)
        self.oil_temp += (self._target_oil_temp - self.oil_temp) * min(1.0, dt / (self._thermal_tau * 1.2) * 2.5) + random.gauss(0, 0.03)
        
        # 7. Oil Pressure (bar)
        oil_viscosity_factor = max(0.50, 1.0 - (self.oil_temp - 88.0) * 0.0075)
        oil_leak = self.fault_modifiers.get("oil_leak_severity", 0.0)
        pump_output = 1.90 + (self.rpm / 5800.0) * 2.90
        bearing_loss = bearing_wear * 0.45
        raw_oil_press = (pump_output * oil_viscosity_factor - 0.10 - bearing_loss) * (1.0 - oil_leak * 0.75)
        self.oil_pressure = max(0.60, min(6.50, raw_oil_press + random.gauss(0, 0.01)))
        
        # 8. Exhaust Gas Temperature (EGT in °C)
        lean_spike = fuel_res * 125.0
        base_egt = 650.0 + (self.engine_load * 1.65) + (self.throttle / 100.0 * 4.0) - (self.ambient_temp - 15.0) * 0.25 + lean_spike
        if misfire > 0:
            base_egt += math.sin(now * 18.0) * (80.0 * misfire) - (45.0 * misfire)
        self.egt += (base_egt - self.egt) * min(1.0, dt * 3.0) + random.gauss(0, 0.5)
        
        # 9. Mechanical RMS Vibration (mm/s)
        base_vib = 0.85 + math.pow(self.rpm / 4000.0, 1.85) * 0.58 + (self.engine_load / 100.0) * 0.12
        mech_imbalance = self.fault_modifiers.get("mechanical_imbalance", 0.0)
        vib_contrib = (mech_imbalance * 6.5) + (misfire * 5.8) + (bearing_wear * 3.5)
        self.vibration = max(0.40, min(16.0, base_vib + vib_contrib + random.gauss(0, 0.03)))
        
        # 10. Battery Voltage
        self.battery_voltage = 13.85 + (self.rpm / 5800.0) * 0.35 + random.gauss(0, 0.01)
        
        return {
            "engine_id": self.engine_id,
            "timestamp": now,
            "engine_hours": round(self.engine_hours, 2),
            "rpm": round(self.rpm, 1),
            "engine_temp": round(measured_cht, 1),
            "cylinder_head_temp": round(measured_cht, 1),
            "oil_temp": round(self.oil_temp, 1),
            "oil_pressure": round(self.oil_pressure, 2),
            "fuel_flow": round(self.fuel_flow, 2),
            "fuel_pressure": round(self.fuel_pressure, 2),
            "manifold_pressure": round(self.manifold_pressure, 2),
            "exhaust_gas_temp": round(self.egt, 1),
            "vibration": round(self.vibration, 2),
            "throttle": round(self.throttle, 1),
            "ambient_temp": round(self.ambient_temp, 1),
            "altitude": round(self.altitude, 0),
            "engine_load": round(self.engine_load, 1),
            "battery_voltage": round(self.battery_voltage, 2),
        }
