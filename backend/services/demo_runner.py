import time
from typing import Dict, Any, List

class DemoRunner:
    '''
    Coordinates the 12-step 120-second (2-minute) DRDO Problem Statement 26054 Demo Flow.
    Provides complete state reset, pause, resume, restart, and step tracking.
    '''
    TOTAL_DURATION = 120.0

    STAGES = [
        {"index": 1, "name": "Baseline Flight", "start_time": 0.0, "duration": 10.0, 
         "desc": "Healthy cruise at 8,000 ft, 65% throttle. Health score 95%, physics residuals < 0.2 sigma."},
        {"index": 2, "name": "High Altitude Climb", "start_time": 10.0, "duration": 10.0, 
         "desc": "UAV climbs to 15,000 ft. Physics Digital Twin compensates for thin-air density and cooling."},
        {"index": 3, "name": "Twin Alignment Check", "start_time": 20.0, "duration": 10.0, 
         "desc": "Virtual vs Real comparison: 8 core parameters observed vs expected residuals verified."},
        {"index": 4, "name": "Overheating Injected", "start_time": 30.0, "duration": 10.0, 
         "desc": "Cooling cowl restriction fault injected. Thermal airflow drops by 70%."},
        {"index": 5, "name": "Early Divergence", "start_time": 40.0, "duration": 10.0, 
         "desc": "CHT diverges (+18°C residual). Conventional static threshold alarms remain silent."},
        {"index": 6, "name": "AI Anomaly Detection", "start_time": 50.0, "duration": 10.0, 
         "desc": "Isolation Forest detects multivariate divergence. Anomaly score triggers WARNING."},
        {"index": 7, "name": "Fault Classification", "start_time": 60.0, "duration": 10.0, 
         "desc": "Supervised Random Forest classifies signature as OVERHEATING with >95% confidence."},
        {"index": 8, "name": "Health Degradation", "start_time": 70.0, "duration": 10.0, 
         "desc": "Digital Twin health fusion drops score from 95% to 58% (DEGRADING state)."},
        {"index": 9, "name": "RUL Prognostic Decay", "start_time": 80.0, "duration": 10.0, 
         "desc": "Physics-guided RUL contracts from 480h to ~85h. Degradation velocity increases to 4.2%/hr."},
        {"index": 10, "name": "XAI Factor Attribution", "start_time": 90.0, "duration": 10.0, 
         "desc": "Dynamic feature attribution highlights CHT (+74%) and Oil Temp (+18%) as primary drivers."},
        {"index": 11, "name": "Maintenance Directive", "start_time": 100.0, "duration": 10.0, 
         "desc": "Prescriptive action generated: Reduce throttle to 50%, enrich mixture, RTB at nearest base."},
        {"index": 12, "name": "Mission Debrief Ready", "start_time": 110.0, "duration": 10.0, 
         "desc": "Demo complete. Full telemetry recorded in SQLite. PDF debrief report ready for export."}
    ]

    def __init__(self, engine_service):
        self.srv = engine_service
        self.is_active = False
        self.is_paused = False
        self.current_time = 0.0
        self.current_stage_idx = 0
        self.last_applied_stage = -1

    def start(self):
        if self.is_paused:
            self.is_paused = False
            return self.get_status()
        self.restart()
        self.is_active = True
        return self.get_status()

    def pause(self):
        if self.is_active:
            self.is_paused = True
        return self.get_status()

    def resume(self):
        if self.is_active and self.is_paused:
            self.is_paused = False
        return self.get_status()

    def restart(self):
        self.is_active = True
        self.is_paused = False
        self.current_time = 0.0
        self.current_stage_idx = 0
        self.last_applied_stage = -1
        
        # Complete state reset on engine service
        self.srv.fault_manager.clear()
        self.srv.engine.set_conditions(throttle=65.0, altitude=8000.0, ambient_temp=18.0)
        self.srv.engine.cht = 96.5
        self.srv.engine.oil_temp = 88.0
        self.srv.engine.oil_pressure = 4.10
        self.srv.engine.rpm = 4600.0
        self.srv.engine.egt = 760.0
        self.srv.engine.vibration = 1.65
        self.srv.engine.fuel_flow = 22.4
        
        # Reset RUL predictor
        self.srv.ai_inference.rul_predictor.current_rul = 480.0
        self.srv.ai_inference.rul_predictor.smooth_degradation_index = 8.5
        
        # Clear buffers
        self.srv.history_buffer.clear()
        self.srv.alerts_buffer.clear()
        
        # Start mission
        self.srv.mission_controller.start("DEMO_PS26054", "DRDO-DEMO-MALE-UAV")
        self._apply_stage(0)
        return self.get_status()

    def stop(self):
        self.is_active = False
        self.is_paused = False
        self.current_time = 0.0
        self.current_stage_idx = 0
        self.last_applied_stage = -1
        self.srv.fault_manager.clear()
        self.srv.engine.set_conditions(throttle=65.0, altitude=8000.0, ambient_temp=18.0)
        self.srv.mission_controller.stop()
        return self.get_status()

    def reset(self):
        return self.restart()

    def update(self, dt: float):
        if not self.is_active or self.is_paused:
            return self.get_status()

        self.current_time += dt
        if self.current_time >= self.TOTAL_DURATION:
            self.current_time = self.TOTAL_DURATION
            self.is_active = False

        # Determine stage index based on elapsed seconds
        stage_idx = int(self.current_time // 10.0)
        stage_idx = min(stage_idx, len(self.STAGES) - 1)
        self.current_stage_idx = stage_idx

        if stage_idx != self.last_applied_stage:
            self._apply_stage(stage_idx)
            self.last_applied_stage = stage_idx

        return self.get_status()

    def _apply_stage(self, idx: int):
        if idx == 0:
            # Baseline flight
            self.srv.fault_manager.clear()
            self.srv.engine.set_conditions(throttle=65.0, altitude=8000.0, ambient_temp=18.0)
        elif idx == 1:
            # Climb to 15,000 ft
            self.srv.engine.set_conditions(throttle=75.0, altitude=15000.0, ambient_temp=8.0)
        elif idx == 2:
            # High altitude cruise alignment
            self.srv.engine.set_conditions(throttle=68.0, altitude=15000.0, ambient_temp=8.0)
        elif idx == 3:
            # Inject gradual overheating fault
            self.srv.fault_manager.inject("OVERHEATING", severity="HIGH", ramp_duration=15.0)
        elif idx == 6:
            # Full severity reached
            self.srv.fault_manager.current_severity = 0.92

    def get_status(self) -> Dict[str, Any]:
        curr = self.STAGES[self.current_stage_idx]
        stage_elapsed = self.current_time - curr["start_time"]
        stage_progress = min(100.0, max(0.0, (stage_elapsed / curr["duration"]) * 100.0))
        total_progress = min(100.0, max(0.0, (self.current_time / self.TOTAL_DURATION) * 100.0))

        stages_summary = []
        for s in self.STAGES:
            is_past = self.current_time >= (s["start_time"] + s["duration"])
            is_curr = s["index"] == (self.current_stage_idx + 1) and self.is_active
            stages_summary.append({
                "index": s["index"],
                "name": s["name"],
                "start_time": s["start_time"],
                "duration": s["duration"],
                "is_active": is_curr,
                "is_completed": is_past
            })

        return {
            "demo_active": self.is_active,
            "is_active": self.is_active,
            "is_paused": self.is_paused,
            "current_time_sec": round(self.current_time, 1),
            "total_duration_sec": self.TOTAL_DURATION,
            "total_progress_pct": round(total_progress, 1),
            "step_index": self.current_stage_idx + 1,
            "total_steps": len(self.STAGES),
            "step_name": curr["name"],
            "step_description": curr["desc"],
            "step_progress_pct": round(stage_progress, 1),
            "step_elapsed": round(stage_elapsed, 1),
            "step_duration": curr["duration"],
            "timeline": stages_summary
        }
