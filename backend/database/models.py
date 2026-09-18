from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, Text
from datetime import datetime
from backend.database.connection import Base

class EngineModel(Base):
    __tablename__ = "engines"
    id = Column(Integer, primary_key=True, index=True)
    engine_id = Column(String(50), unique=True, index=True)
    model_name = Column(String(100), default="Rotax 915 iS Turbocharged Piston")
    installed_hours = Column(Float, default=1247.4)
    status = Column(String(30), default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)

class MissionRecord(Base):
    __tablename__ = "missions"
    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(String(50), unique=True, index=True)
    scenario = Column(String(50), default="NORMAL_MISSION")
    scenario_name = Column(String(100), default="Normal Patrol Cruise")
    state = Column(String(30), default="STOPPED")
    start_time = Column(Float, default=0.0)
    end_time = Column(Float, default=0.0)
    duration_seconds = Column(Float, default=0.0)
    peak_temp = Column(Float, default=0.0)
    max_vibration = Column(Float, default=0.0)
    min_oil_pressure = Column(Float, default=0.0)
    final_health = Column(Float, default=100.0)
    final_rul = Column(Float, default=480.0)
    faults_logged = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

class SensorReadingRecord(Base):
    __tablename__ = "sensor_readings"
    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(String(50), index=True)
    timestamp = Column(Float, index=True)
    rpm = Column(Float)
    engine_temp = Column(Float)
    oil_temp = Column(Float)
    oil_pressure = Column(Float)
    fuel_flow = Column(Float)
    fuel_pressure = Column(Float)
    manifold_pressure = Column(Float)
    exhaust_gas_temp = Column(Float)
    vibration = Column(Float)
    altitude = Column(Float)
    ambient_temp = Column(Float)
    engine_load = Column(Float)
    health_score = Column(Float)
    status = Column(String(30))

class AlertRecord(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(String(50), index=True)
    timestamp = Column(Float, default=0.0)
    time_str = Column(String(30))
    severity = Column(String(20)) # INFO, WARNING, CRITICAL
    title = Column(String(150))
    message = Column(Text)
    recommended_action = Column(Text)
    confidence = Column(Float, default=0.0)
    acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
