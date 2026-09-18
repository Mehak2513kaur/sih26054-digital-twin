from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.engine_service import EngineService

router = APIRouter()
service = EngineService()

class InjectFaultRequest(BaseModel):
    fault_type: str
    severity: str = "MEDIUM" # LOW, MEDIUM, HIGH
    ramp_duration: float = 20.0

@router.post("/fault/inject")
def inject_fault(req: InjectFaultRequest):
    # Route to Sim 2 engine
    try:
        sim2_event = service.fault_injection.start_fault(
            fault_name=req.fault_type,
            severity=req.severity,
            ramp_duration=req.ramp_duration
        )
    except Exception:
        sim2_event = None

    # Also route to legacy fault manager if recognized
    try:
        legacy_event = service.fault_manager.inject(
            fault_type=req.fault_type,
            severity=req.severity,
            ramp_duration=req.ramp_duration
        )
        return legacy_event
    except Exception:
        if sim2_event:
            return sim2_event
        raise ValueError(f"Unknown fault type: {req.fault_type}")

@router.post("/fault/clear")
def clear_fault():
    service.fault_injection.stop_fault()
    return service.fault_manager.clear()

@router.post("/fault/sim2/inject")
def inject_sim2_fault(req: InjectFaultRequest):
    return service.fault_injection.start_fault(
        fault_name=req.fault_type,
        severity=req.severity,
        ramp_duration=req.ramp_duration
    )

@router.post("/fault/sim2/clear")
def clear_sim2_fault():
    return service.fault_injection.stop_fault()

@router.get("/fault/sim2/status")
def get_sim2_fault_status():
    return service.fault_injection.get_status()
