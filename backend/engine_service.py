import time
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import deque

from simulator.engine import UAVPistonEngine
from simulator.sensors import SensorSuite
from simulator.faults import FaultManager
from simulator.fault_injection import FaultInjectionEngine
from simulator.publisher import MQTTSimulatorPublisher
from simulator.missions import MissionController
from physics.engine_model import PhysicsEngineModel
from physics.residuals import ResidualCalculator
from backend.services.edge_preprocessor import EdgePreprocessor
from backend.services.health_fusion import HealthFusionEngine
from backend.services.recommendations import RecommendationEngine
from backend.services.communication_sim import CANBusSimulator
from backend.services.demo_runner import DemoRunner
from ml.inference import EngineAIInference
from backend.websocket.manager import ConnectionManager
from backend.database.connection import SessionLocal
from backend.database.models import MissionRecord, SensorReadingRecord, AlertRecord

class EngineService:
    '''
    Master Singleton Coordinator for the UAV Digital Twin platform:
    - Runs continuous 10 Hz physical simulation loop
    - Computes edge preprocessing, physics model, AI inference & health fusion
    - Stores historical points in database & in-memory sliding buffer
    - Broadcasts live state via WebSocket
    '''
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(EngineService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True

        self.engine = UAVPistonEngine(engine_id="UAV-PX-01", initial_hours=1247.4)
        self.sensor_suite = SensorSuite()
        self.fault_manager = FaultManager()
        self.fault_injection = FaultInjectionEngine()
        self.mqtt_publisher = MQTTSimulatorPublisher()
        self.mission_controller = MissionController()
        self.physics_model = PhysicsEngineModel()
        self.residual_calculator = ResidualCalculator()
        self.edge_preprocessor = EdgePreprocessor(window_size=15)
        self.health_fusion = HealthFusionEngine()
        self.recommendation_engine = RecommendationEngine()
        self.can_bus = CANBusSimulator()
        self.ai_inference = EngineAIInference()
        self.ws_manager = ConnectionManager()
        self.demo_runner = DemoRunner(self)

        # Sliding telemetry buffer for charts (last 300 points = ~30s at 10Hz, downsampled)
        self.history_buffer = deque(maxlen=400)
        self.alerts_buffer = deque(maxlen=50)
        self.latest_full_state: Dict[str, Any] = {}
        
        self.is_running = True
        self.db_save_counter = 0

    def step(self, dt: float = 0.1) -> Dict[str, Any]:
        # 1. Update Faults & Mission
        fault_info = self.fault_manager.update(dt=dt, engine=self.engine)
        sim2_fault_status = self.fault_injection.update(dt=dt)
        mission_info = self.mission_controller.update(dt=dt, engine=self.engine, fault_manager=self.fault_manager)
        demo_info = self.demo_runner.update(dt=dt)

        # 2. Step Engine Physics
        raw_telemetry = self.engine.step(dt=dt)

        # Sim 2: Logical Fault Injection Pipeline
        modified_telemetry = self.fault_injection.apply_fault(raw_telemetry)

        # Sim 2: MQTT Publish Telemetry (uav/engine/telemetry)
        self.mqtt_publisher.publish_telemetry(modified_telemetry)

        # Sensor suite & edge preprocessing take modified telemetry
        sensor_telemetry = self.sensor_suite.process(modified_telemetry)

        # 3. Edge Preprocessing
        edge_output = self.edge_preprocessor.process(sensor_telemetry)
        clean_telemetry = edge_output["cleaned_telemetry"]
        derived_features = edge_output["derived_features"]
        quality_metrics = edge_output["quality_metrics"]

        # 4. Physics-Based Digital Twin Model
        expected_physics = self.physics_model.calculate_expected(
            rpm=clean_telemetry["rpm"],
            throttle=clean_telemetry["throttle"],
            altitude=clean_telemetry["altitude"],
            ambient_temp=clean_telemetry["ambient_temp"],
            engine_load=clean_telemetry["engine_load"]
        )

        # 5. Physics Residuals
        residuals = self.residual_calculator.calculate(clean_telemetry, expected_physics)

        # 6. AI/ML Inference (Anomaly Detection, Fault Classifier, RUL, Explainability)
        ml_prediction = self.ai_inference.predict(clean_telemetry, residuals, derived_features, expected_physics)

        # 7. Health Fusion
        health_output = self.health_fusion.calculate(
            physics_residuals=residuals,
            ml_prediction=ml_prediction,
            derived_features=derived_features,
            fault_info=fault_info
        )

        # Sync health to mission
        self.mission_controller.final_health = health_output["health_score"]
        self.mission_controller.final_rul = ml_prediction["rul"]["rul_hours"]

        # 8. Recommendation Engine
        pred_fault = ml_prediction["predicted_fault"]
        recommendation = self.recommendation_engine.get_recommendation(
            fault_class=pred_fault,
            severity=fault_info.get("severity_name", "MEDIUM")
        )

        # 9. CAN Bus Simulation
        can_status = self.can_bus.step()

        # 10. Alert Handling
        if health_output["status"] != "HEALTHY" or pred_fault != "NORMAL":
            self._handle_alert(health_output, ml_prediction, recommendation)

        # Sim 2: MQTT Publish Component Health (uav/engine/health)
        self.mqtt_publisher.publish_health({
            "health_score": health_output["health_score"],
            "status": health_output["status"],
            "component_health": self.fault_injection.component_health,
            "rul_hours": ml_prediction["rul"]["rul_hours"],
            "degradation_velocity": ml_prediction["rul"].get("degradation_velocity", 0.0),
        })

        # Sim 2: MQTT Publish AI/Anomaly Events (uav/engine/alerts)
        if ml_prediction.get("is_anomaly") or pred_fault != "NORMAL":
            self.mqtt_publisher.publish_alert({
                "timestamp": time.time(),
                "anomaly_detected": ml_prediction.get("is_anomaly", True),
                "anomaly_score": ml_prediction.get("anomaly_intensity", 85.0),
                "predicted_fault": pred_fault,
                "confidence": ml_prediction.get("confidence", 95.0),
                "severity": fault_info.get("severity_name", "WARNING"),
                "directive": recommendation.get("recommended_action", ""),
            })

        # Sim 2: MQTT Publish Fault Event if active
        if self.fault_injection.is_active:
            self.mqtt_publisher.publish_fault(sim2_fault_status)

        # Assemble Full State
        full_packet = {
            "timestamp": time.time(),
            "time_str": datetime.now().strftime("%H:%M:%S"),
            "engine_id": self.engine.engine_id,
            "engine_hours": clean_telemetry["engine_hours"],
            "mission": mission_info,
            "demo": demo_info,
            "telemetry": clean_telemetry,
            "sim2_telemetry": modified_telemetry,
            "derived": derived_features,
            "quality": quality_metrics,
            "expected_physics": expected_physics,
            "residuals": residuals,
            "ml_prediction": ml_prediction,
            "health": health_output,
            "recommendation": recommendation,
            "can_bus": can_status,
            "fault_injection": fault_info,
            "sim2_fault_injection": sim2_fault_status,
            "mqtt_stats": self.mqtt_publisher.get_stats(),
            "active_alerts": list(self.alerts_buffer)
        }

        self.latest_full_state = full_packet
        
        # Add to in-memory chart buffer every 3rd step (~3.3 Hz) to conserve client bandwidth
        if self.db_save_counter % 3 == 0:
            self.history_buffer.append({
                "time": full_packet["time_str"],
                "timestamp": full_packet["timestamp"],
                "rpm": clean_telemetry["rpm"],
                "engine_temp": clean_telemetry["engine_temp"],
                "oil_pressure": clean_telemetry["oil_pressure"],
                "oil_temp": clean_telemetry["oil_temp"],
                "vibration": clean_telemetry["vibration"],
                "fuel_flow": clean_telemetry["fuel_flow"],
                "exhaust_gas_temp": clean_telemetry["exhaust_gas_temp"],
                "expected_temp": expected_physics["expected_engine_temp"],
                "expected_oil_press": expected_physics["expected_oil_pressure"],
                "expected_vib": expected_physics["expected_vibration"],
                "health_score": health_output["health_score"],
                "rul_hours": ml_prediction["rul"]["rul_hours"]
            })

        # Save to DB every 10 steps (~1 second) when mission or demo is active
        self.db_save_counter += 1
        if self.db_save_counter >= 10:
            self.db_save_counter = 0
            if self.mission_controller.state == "RUNNING" or self.demo_runner.is_active:
                self._persist_telemetry(clean_telemetry, health_output)

        return full_packet

    def _handle_alert(self, health_output, ml_prediction, recommendation):
        now = time.time()
        # Avoid duplicate alerts within 8 seconds
        if self.alerts_buffer:
            last_alert = self.alerts_buffer[0]
            if (now - last_alert["timestamp"]) < 8.0 and last_alert["title"] == recommendation["title"]:
                return

        severity = "CRITICAL" if health_output["status"] == "CRITICAL" else "WARNING"
        alert_item = {
            "id": int(now * 1000) % 1000000,
            "timestamp": now,
            "time_str": datetime.now().strftime("%H:%M:%S"),
            "severity": severity,
            "title": recommendation["title"],
            "message": f"Health score degraded to {health_output['health_score']}%. Fault pattern: {ml_prediction['predicted_fault']} (Confidence: {ml_prediction['confidence']}%).",
            "recommended_action": recommendation["recommended_action"],
            "confidence": ml_prediction["confidence"],
            "acknowledged": False
        }
        self.alerts_buffer.appendleft(alert_item)

        # Persist alert to database
        try:
            db = SessionLocal()
            record = AlertRecord(
                mission_id=self.mission_controller.mission_id,
                timestamp=now,
                time_str=alert_item["time_str"],
                severity=severity,
                title=alert_item["title"],
                message=alert_item["message"],
                recommended_action=alert_item["recommended_action"],
                confidence=alert_item["confidence"],
                acknowledged=False
            )
            db.add(record)
            db.commit()
            db.close()
        except Exception as e:
            pass

    def _persist_telemetry(self, telemetry, health):
        try:
            db = SessionLocal()
            record = SensorReadingRecord(
                mission_id=self.mission_controller.mission_id,
                timestamp=telemetry["timestamp"],
                rpm=telemetry["rpm"],
                engine_temp=telemetry["engine_temp"],
                oil_temp=telemetry["oil_temp"],
                oil_pressure=telemetry["oil_pressure"],
                fuel_flow=telemetry["fuel_flow"],
                fuel_pressure=telemetry["fuel_pressure"],
                manifold_pressure=telemetry["manifold_pressure"],
                exhaust_gas_temp=telemetry["exhaust_gas_temp"],
                vibration=telemetry["vibration"],
                altitude=telemetry["altitude"],
                ambient_temp=telemetry["ambient_temp"],
                engine_load=telemetry["engine_load"],
                health_score=health["health_score"],
                status=health["status"]
            )
            db.add(record)
            db.commit()
            db.close()
        except Exception:
            pass

    async def run_loop(self):
        print("Starting UAV Engine Digital Twin 10 Hz simulation loop...")
        while self.is_running:
            packet = self.step(dt=0.1)
            # Broadcast to connected WebSocket clients
            if self.ws_manager.active_connections:
                await self.ws_manager.broadcast(packet)
            await asyncio.sleep(0.1)
