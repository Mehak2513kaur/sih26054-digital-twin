from fastapi import APIRouter
from backend.engine_service import EngineService

router = APIRouter()
service = EngineService()

@router.get("/twin/state")
def get_twin_state():
    return {
        "observed": service.latest_full_state.get("telemetry", {}),
        "expected": service.latest_full_state.get("expected_physics", {}),
        "residuals": service.latest_full_state.get("residuals", {})
    }
