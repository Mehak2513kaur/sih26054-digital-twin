import random
from typing import Dict, Any

class SensorSuite:
    '''
    Simulates sensor quantization, transient ADC spikes, and glitch injection.
    '''
    def __init__(self):
        self.glitch_rate = 0.005

    def process(self, raw_telemetry: Dict[str, Any]) -> Dict[str, Any]:
        telemetry = dict(raw_telemetry)
        if random.random() < self.glitch_rate:
            spike_sensor = random.choice(["rpm", "engine_temp", "vibration", "oil_pressure"])
            if spike_sensor == "rpm":
                telemetry["rpm"] = round(telemetry["rpm"] + random.choice([-800.0, 900.0]), 1)
            elif spike_sensor == "engine_temp":
                telemetry["engine_temp"] = round(telemetry["engine_temp"] + random.choice([-35.0, 45.0]), 1)
            elif spike_sensor == "vibration":
                telemetry["vibration"] = round(telemetry["vibration"] + random.choice([12.0, 15.0]), 2)
            elif spike_sensor == "oil_pressure":
                telemetry["oil_pressure"] = round(telemetry["oil_pressure"] + random.choice([-2.5, 3.0]), 2)
            telemetry["_is_glitch_injected"] = True
        else:
            telemetry["_is_glitch_injected"] = False

        return telemetry
