import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.database.connection import init_db
from backend.engine_service import EngineService
from backend.api import (
    health,
    sensors,
    twin,
    prediction,
    alerts,
    missions,
    faults,
    reports,
    demo
)

service = EngineService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite Database tables
    init_db()
    # Initial tick to generate state
    service.step(dt=0.1)
    # Start background 10 Hz simulation loop task
    sim_task = asyncio.create_task(service.run_loop())
    print("Backend started successfully with 10 Hz simulation loop.")
    yield
    # Shutdown
    service.is_running = False
    sim_task.cancel()
    print("Backend simulation loop shut down.")

app = FastAPI(
    title="DRDO 26054 UAV Engine Digital Twin Platform",
    description="Predictive Health Monitoring & Prognostic Digital Twin for MALE UAV Piston Engines",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(sensors.router, prefix="/api", tags=["Sensors"])
app.include_router(twin.router, prefix="/api", tags=["Digital Twin"])
app.include_router(prediction.router, prefix="/api", tags=["AI Prediction & RUL"])
app.include_router(alerts.router, prefix="/api", tags=["Alerts"])
app.include_router(missions.router, prefix="/api", tags=["Missions"])
app.include_router(faults.router, prefix="/api", tags=["Fault Injection"])
app.include_router(reports.router, prefix="/api", tags=["Reports"])
app.include_router(demo.router, prefix="/api", tags=["Demo Mode"])

@app.get("/")
def root():
    return {
        "title": "AI-Powered Digital Twin for MALE UAV Piston Engines",
        "objective": "DRDO Problem Statement 26054 Prototype",
        "mode": "SIMULATION MODE",
        "status": "ONLINE",
        "endpoints": {
            "health": "/api/health",
            "sensors": "/api/sensors/latest",
            "twin": "/api/twin/state",
            "prediction": "/api/prediction",
            "missions": "/api/missions",
            "websocket": "/ws/engine",
            "docs": "/docs"
        }
    }

@app.websocket("/ws/engine")
async def websocket_endpoint(websocket: WebSocket):
    await service.ws_manager.connect(websocket)
    # Send immediate state on connect
    if service.latest_full_state:
        await websocket.send_json(service.latest_full_state)
    try:
        while True:
            # Keep listening for client command packets if any
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        service.ws_manager.disconnect(websocket)
    except Exception:
        service.ws_manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=False)
