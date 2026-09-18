from fastapi import APIRouter, Query
from backend.engine_service import EngineService

router = APIRouter()
service = EngineService()

@router.get("/sensors/latest")
def get_latest_sensors():
    return {
        "telemetry": service.latest_full_state.get("telemetry", {}),
        "derived": service.latest_full_state.get("derived", {})
    }

@router.get("/sensors/history")
def get_sensors_history(limit: int = Query(150, ge=10, le=400)):
    items = list(service.history_buffer)
    return {
        "count": len(items[-limit:]),
        "history": items[-limit:]
    }

@router.get("/quality")
def get_sensor_quality():
    return service.latest_full_state.get("quality", {})
