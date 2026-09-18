from fastapi import APIRouter
from backend.engine_service import EngineService

router = APIRouter()
service = EngineService()

@router.get("/prediction")
def get_prediction():
    ml_pred = service.latest_full_state.get("ml_prediction", {})
    return {
        "ml": ml_pred,
        "prediction": ml_pred,
        "ml_prediction": ml_pred,
        "health": service.latest_full_state.get("health", {}),
        "recommendation": service.latest_full_state.get("recommendation", {})
    }
