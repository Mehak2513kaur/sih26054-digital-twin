from fastapi import APIRouter
from backend.engine_service import EngineService

router = APIRouter()
service = EngineService()

@router.post("/demo/start")
def start_demo():
    return service.demo_runner.start()

@router.post("/demo/pause")
def pause_demo():
    return service.demo_runner.pause()

@router.post("/demo/resume")
def resume_demo():
    return service.demo_runner.resume()

@router.post("/demo/restart")
def restart_demo():
    return service.demo_runner.restart()

@router.post("/demo/stop")
def stop_demo():
    return service.demo_runner.stop()

@router.post("/demo/reset")
def reset_demo():
    return service.demo_runner.reset()

@router.get("/demo/status")
def get_demo_status():
    return service.demo_runner.get_status()
