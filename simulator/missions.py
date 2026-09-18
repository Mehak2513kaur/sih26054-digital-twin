import time
from typing import Dict, Any, List, Optional

class MissionController:
    '''
    Manages mission state and predefined flight profiles.
    '''
    SCENARIOS = {
        "NORMAL_MISSION": {
            "name": "Normal Patrol Cruise",
            "target_altitude": 8000.0,
            "ambient_temp": 18.0,
            "throttle": 65.0,
            "description": "Stable cruise patrol at standard altitude with nominal engine parameters."
        },
        "HIGH_ALTITUDE": {
            "name": "High Altitude Climax",
            "target_altitude": 22000.0,
            "ambient_temp": -10.0,
            "throttle": 78.0,
            "description": "Climb profile to 22,000 ft testing turbocharger wastegate and thin-air cooling."
        },
        "HOT_WEATHER": {
            "name": "Hot Desert Recon",
            "target_altitude": 4500.0,
            "ambient_temp": 45.0,
            "throttle": 70.0,
            "description": "High ambient temperature desert profile stressing engine cooling systems."
        },
        "LONG_ENDURANCE": {
            "name": "Long Endurance Loiter",
            "target_altitude": 10000.0,
            "ambient_temp": 12.0,
            "throttle": 58.0,
            "description": "Extended 14-hour simulated loiter tracking continuous thermal soak."
        },
        "RAPID_LOAD_CHANGE": {
            "name": "Rapid Tactical Maneuver",
            "target_altitude": 6000.0,
            "ambient_temp": 20.0,
            "throttle": 85.0,
            "description": "Rapid throttle and pitch cycling between 35% and 95% engine load."
        },
        "FAULT_INJECTION": {
            "name": "Fault Evaluation Profile",
            "target_altitude": 8000.0,
            "ambient_temp": 22.0,
            "throttle": 65.0,
            "description": "Baseline flight designed specifically for scheduled fault injection evaluation."
        }
    }

    def __init__(self):
        self.state: str = "IDLE"
        self.mission_id: str = "MISSION-042"
        self.current_scenario: str = "NORMAL_MISSION"
        self.start_time: float = 0.0
        self.pause_time: float = 0.0
        self.elapsed_time: float = 0.0
        
        self.peak_temp: float = 0.0
        self.max_vibration: float = 0.0
        self.min_oil_pressure: float = 99.0
        self.final_health: float = 100.0
        self.final_rul: float = 480.0
        self.faults_observed: List[str] = []

    def start(self, scenario: str = "NORMAL_MISSION", mission_id: Optional[str] = None):
        if scenario not in self.SCENARIOS:
            scenario = "NORMAL_MISSION"
        self.current_scenario = scenario
        self.mission_id = mission_id or f"MISSION-{int(time.time()) % 1000:03d}"
        self.state = "RUNNING"
        self.start_time = time.time()
        self.elapsed_time = 0.0
        self.peak_temp = 0.0
        self.max_vibration = 0.0
        self.min_oil_pressure = 99.0
        self.faults_observed = []
        return self.get_summary()

    def pause(self):
        if self.state == "RUNNING":
            self.state = "PAUSED"
            self.pause_time = time.time()
        return self.get_summary()

    def resume(self):
        if self.state == "PAUSED":
            self.state = "RUNNING"
        return self.get_summary()

    def stop(self):
        self.state = "STOPPED"
        return self.get_summary()

    def reset(self):
        self.state = "IDLE"
        self.elapsed_time = 0.0
        self.start_time = 0.0
        self.peak_temp = 0.0
        self.max_vibration = 0.0
        self.min_oil_pressure = 99.0
        return self.get_summary()

    def update(self, dt: float, engine, fault_manager) -> Dict[str, Any]:
        if self.state != "RUNNING":
            return self.get_summary()
            
        self.elapsed_time += dt
        cfg = self.SCENARIOS.get(self.current_scenario, self.SCENARIOS["NORMAL_MISSION"])
        
        if self.current_scenario == "HIGH_ALTITUDE":
            climb_rate = (22000.0 - 3000.0) / 120.0
            new_alt = min(22000.0, 3000.0 + self.elapsed_time * climb_rate)
            new_temp = 20.0 - (new_alt / 1000.0) * 1.98
            engine.set_conditions(throttle=cfg["throttle"], altitude=new_alt, ambient_temp=new_temp)
        elif self.current_scenario == "HOT_WEATHER":
            engine.set_conditions(throttle=cfg["throttle"], altitude=cfg["target_altitude"], ambient_temp=cfg["ambient_temp"])
        elif self.current_scenario == "RAPID_LOAD_CHANGE":
            cycle = (self.elapsed_time % 24.0)
            throttle = 92.0 if cycle < 12.0 else 38.0
            engine.set_conditions(throttle=throttle, altitude=cfg["target_altitude"], ambient_temp=cfg["ambient_temp"])
        else:
            engine.set_conditions(throttle=cfg["throttle"], altitude=cfg["target_altitude"], ambient_temp=cfg["ambient_temp"])

        if engine.cht > self.peak_temp:
            self.peak_temp = engine.cht
        if engine.vibration > self.max_vibration:
            self.max_vibration = engine.vibration
        if engine.oil_pressure < self.min_oil_pressure:
            self.min_oil_pressure = engine.oil_pressure
            
        if fault_manager.active_fault != "NORMAL" and fault_manager.active_fault not in self.faults_observed:
            self.faults_observed.append(fault_manager.active_fault)

        return self.get_summary()

    def get_summary(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "scenario": self.current_scenario,
            "scenario_name": self.SCENARIOS.get(self.current_scenario, {}).get("name", "Normal"),
            "state": self.state,
            "elapsed_time": round(self.elapsed_time, 1),
            "peak_temp": round(self.peak_temp, 1),
            "max_vibration": round(self.max_vibration, 2),
            "min_oil_pressure": round(self.min_oil_pressure if self.min_oil_pressure < 90 else 4.1, 2),
            "faults_observed": list(self.faults_observed),
            "final_health": round(self.final_health, 1),
            "final_rul": round(self.final_rul, 1)
        }
