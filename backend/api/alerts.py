from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.engine_service import EngineService

router = APIRouter()
service = EngineService()

class AckAlertRequest(BaseModel):
    alert_id: int

@router.get("/alerts")
def get_alerts():
    return {
        "count": len(service.alerts_buffer),
        "alerts": list(service.alerts_buffer)
    }

@router.post("/alerts/acknowledge")
def acknowledge_alert(req: AckAlertRequest):
    for a in service.alerts_buffer:
        if a.get("id") == req.alert_id:
            a["acknowledged"] = True
            return {"status": "SUCCESS", "alert_id": req.alert_id}
    return {"status": "NOT_FOUND"}
