from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.engine_service import EngineService
from backend.database.connection import SessionLocal
from backend.database.models import MissionRecord, SensorReadingRecord
import time

router = APIRouter()
service = EngineService()

class StartMissionRequest(BaseModel):
    scenario: str = "NORMAL_MISSION"
    mission_id: Optional[str] = None
    altitude: Optional[float] = None
    ambient_temp: Optional[float] = None
    throttle: Optional[float] = None

@router.get("/missions")
def get_missions():
    db = SessionLocal()
    missions = db.query(MissionRecord).order_by(MissionRecord.id.desc()).limit(20).all()
    results = [
        {
            "id": m.id,
            "mission_id": m.mission_id,
            "scenario": m.scenario,
            "scenario_name": m.scenario_name,
            "duration": round(m.duration_seconds, 1),
            "peak_temp": round(m.peak_temp, 1),
            "max_vibration": round(m.max_vibration, 2),
            "min_oil_pressure": round(m.min_oil_pressure, 2),
            "final_health": round(m.final_health, 1),
            "final_rul": round(m.final_rul, 1),
            "status": m.state,
            "date": m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else ""
        }
        for m in missions
    ]
    db.close()
    return {"current": service.mission_controller.get_summary(), "history": results}

@router.post("/missions/start")
def start_mission(req: StartMissionRequest):
    summary = service.mission_controller.start(scenario=req.scenario, mission_id=req.mission_id)
    if req.altitude is not None or req.ambient_temp is not None or req.throttle is not None:
        service.engine.set_conditions(throttle=req.throttle, altitude=req.altitude, ambient_temp=req.ambient_temp)
    return summary

@router.post("/missions/pause")
def pause_mission():
    return service.mission_controller.pause()

@router.post("/missions/resume")
def resume_mission():
    return service.mission_controller.resume()

@router.post("/missions/stop")
def stop_mission():
    summary = service.mission_controller.stop()
    # Save mission record to database
    try:
        db = SessionLocal()
        record = MissionRecord(
            mission_id=summary["mission_id"],
            scenario=summary["scenario"],
            scenario_name=summary["scenario_name"],
            state="COMPLETED",
            duration_seconds=summary["elapsed_time"],
            peak_temp=summary["peak_temp"],
            max_vibration=summary["max_vibration"],
            min_oil_pressure=summary["min_oil_pressure"],
            final_health=summary["final_health"],
            final_rul=summary["final_rul"],
            faults_logged=",".join(summary["faults_observed"])
        )
        db.add(record)
        db.commit()
        db.close()
    except Exception as e:
        print("Error persisting completed mission:", e)
    return summary

@router.post("/missions/reset")
def reset_mission():
    return service.mission_controller.reset()

@router.get("/missions/{mission_id}/replay")
def get_mission_replay(mission_id: str):
    db = SessionLocal()
    readings = db.query(SensorReadingRecord).filter(SensorReadingRecord.mission_id == mission_id).order_by(SensorReadingRecord.timestamp.asc()).all()
    db.close()
    if not readings:
        # Fallback to current history buffer for active session
        readings_data = list(service.history_buffer)
    else:
        readings_data = [
            {
                "time": time.strftime("%H:%M:%S", time.localtime(r.timestamp)),
                "timestamp": r.timestamp,
                "rpm": r.rpm,
                "engine_temp": r.engine_temp,
                "oil_pressure": r.oil_pressure,
                "oil_temp": r.oil_temp,
                "vibration": r.vibration,
                "fuel_flow": r.fuel_flow,
                "exhaust_gas_temp": r.exhaust_gas_temp,
                "altitude": r.altitude,
                "health_score": r.health_score,
                "status": r.status
            }
            for r in readings
        ]
    return {
        "mission_id": mission_id,
        "total_points": len(readings_data),
        "telemetry_stream": readings_data
    }
