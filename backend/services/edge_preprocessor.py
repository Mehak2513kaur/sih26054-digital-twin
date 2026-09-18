from collections import deque
import numpy as np
from typing import Dict, Any

class EdgePreprocessor:
    '''
    Edge processing module for UAV telemetry:
    - Rejects ADC spikes and transient glitches
    - Calculates rolling statistics and rates of change
    - Derives composite cross-feature ratios
    - Computes sensor stream quality metrics
    '''
    PHYSICAL_LIMITS = {
        "rpm": (800.0, 6500.0, 600.0),       # min, max, max_step_dt
        "engine_temp": (20.0, 180.0, 15.0),
        "oil_temp": (15.0, 160.0, 12.0),
        "oil_pressure": (0.2, 7.5, 2.0),
        "fuel_flow": (1.0, 60.0, 10.0),
        "vibration": (0.1, 20.0, 8.0)
    }

    def __init__(self, window_size: int = 15):
        self.window_size = window_size
        self.history = {k: deque(maxlen=window_size) for k in self.PHYSICAL_LIMITS}
        self.time_history = deque(maxlen=window_size)
        
        self.total_packets = 0
        self.glitches_detected = 0
        self.sensor_glitch_counts = {k: 0 for k in self.PHYSICAL_LIMITS}
        self.last_valid = {}

    def process(self, raw_telemetry: Dict[str, Any]) -> Dict[str, Any]:
        self.total_packets += 1
        clean = dict(raw_telemetry)
        now = raw_telemetry.get("timestamp", 0.0)
        
        is_glitch_packet = False
        for sensor, (min_v, max_v, max_step) in self.PHYSICAL_LIMITS.items():
            val = raw_telemetry.get(sensor, 0.0)
            prev_val = self.last_valid.get(sensor, val)
            
            # Out of bounds or impossible step delta
            if val < min_v or val > max_v or abs(val - prev_val) > max_step:
                self.glitches_detected += 1
                self.sensor_glitch_counts[sensor] += 1
                is_glitch_packet = True
                if self.history[sensor]:
                    val = float(np.mean(self.history[sensor]))
                else:
                    val = prev_val
                clean[sensor] = round(val, 2)
            
            self.last_valid[sensor] = val
            self.history[sensor].append(val)
            
        self.time_history.append(now)

        dt_span = 1.0
        if len(self.time_history) >= 2:
            dt_span = max(0.1, self.time_history[-1] - self.time_history[0])
            
        temp_rate = 0.0
        vib_rate = 0.0
        oil_press_rate = 0.0
        rpm_change = 0.0
        fuel_flow_change = 0.0
        
        if len(self.history["engine_temp"]) >= 2:
            temp_rate = (self.history["engine_temp"][-1] - self.history["engine_temp"][0]) / (dt_span / 60.0)
        if len(self.history["vibration"]) >= 2:
            vib_rate = (self.history["vibration"][-1] - self.history["vibration"][0]) / (dt_span / 60.0)
        if len(self.history["oil_pressure"]) >= 2:
            oil_press_rate = (self.history["oil_pressure"][-1] - self.history["oil_pressure"][0]) / (dt_span / 60.0)
        if len(self.history["rpm"]) >= 2:
            rpm_change = (self.history["rpm"][-1] - self.history["rpm"][0]) / dt_span
        if len(self.history["fuel_flow"]) >= 2:
            fuel_flow_change = (self.history["fuel_flow"][-1] - self.history["fuel_flow"][0]) / dt_span

        rolling_temp_mean = float(np.mean(self.history["engine_temp"])) if self.history["engine_temp"] else clean["engine_temp"]
        rolling_vib_mean = float(np.mean(self.history["vibration"])) if self.history["vibration"] else clean["vibration"]
        rolling_oil_mean = float(np.mean(self.history["oil_pressure"])) if self.history["oil_pressure"] else clean["oil_pressure"]
        temp_vib_ratio = rolling_temp_mean / max(0.1, rolling_vib_mean)

        total = max(1, self.total_packets)
        quality_rpm = round(max(90.0, 100.0 - (self.sensor_glitch_counts["rpm"] / total * 100.0)), 1)
        quality_temp = round(max(90.0, 100.0 - (self.sensor_glitch_counts["engine_temp"] / total * 100.0)), 1)
        quality_oil = round(max(90.0, 100.0 - (self.sensor_glitch_counts["oil_pressure"] / total * 100.0)), 1)
        quality_vib = round(max(90.0, 100.0 - (self.sensor_glitch_counts["vibration"] / total * 100.0)), 1)

        derived = {
            "temperature_rate": round(temp_rate, 2),
            "vibration_rate": round(vib_rate, 2),
            "oil_pressure_rate": round(oil_press_rate, 2),
            "rpm_change": round(rpm_change, 1),
            "fuel_flow_change": round(fuel_flow_change, 2),
            "temperature_vibration_ratio": round(temp_vib_ratio, 2),
            "rolling_temperature_mean": round(rolling_temp_mean, 1),
            "rolling_vibration_mean": round(rolling_vib_mean, 2),
            "rolling_oil_pressure_mean": round(rolling_oil_mean, 2),
            "is_glitch_filtered": is_glitch_packet
        }

        quality = {
            "quality_rpm": quality_rpm,
            "quality_temp": quality_temp,
            "quality_oil": quality_oil,
            "quality_vib": quality_vib,
            "total_packets": self.total_packets,
            "glitches_filtered": self.glitches_detected
        }

        return {
            "cleaned_telemetry": clean,
            "derived_features": derived,
            "quality_metrics": quality
        }
