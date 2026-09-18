"""
MALE UAV Piston Engine Digital Twin - MQTT Publisher (Sim 2)
DRDO Problem Statement 26054

Publishes real-time telemetry, fault events, component health, and AI alerts
to MQTT topics with automatic mock-mode fallback if no broker is active.
"""

import json
import os
import time
import logging
from collections import deque
from typing import Dict, Any, Optional, List

# Configure logger
logger = logging.getLogger("UAV_MQTT_Publisher")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [MQTT] %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class MQTTSimulatorPublisher:
    """
    MQTT Publisher for UAV Piston Engine Simulation (Sim 2).
    Publishes to:
      - uav/engine/telemetry
      - uav/engine/faults
      - uav/engine/health
      - uav/engine/alerts
    """

    TOPIC_TELEMETRY = "uav/engine/telemetry"
    TOPIC_FAULTS = "uav/engine/faults"
    TOPIC_HEALTH = "uav/engine/health"
    TOPIC_ALERTS = "uav/engine/alerts"

    # The 18 mandatory telemetry fields specified for Sim 2
    MANDATORY_TELEMETRY_FIELDS = [
        "timestamp",
        "rpm",
        "cht",
        "egt",
        "oil_pressure",
        "oil_temperature",
        "fuel_pressure",
        "fuel_flow",
        "map",
        "boost_pressure",
        "vibration",
        "engine_load",
        "throttle",
        "altitude",
        "ambient_temperature",
        "coolant_temperature",
        "battery_voltage",
        "engine_hours",
    ]

    def __init__(
        self,
        broker: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        client_id: str = "uav-engine-sim2-publisher",
        mock_mode: Optional[bool] = None,
    ):
        # Configuration from arguments or environment variables
        self.broker = broker or os.getenv("MQTT_BROKER", "localhost")
        self.port = int(port or os.getenv("MQTT_PORT", "1883"))
        self.username = username or os.getenv("MQTT_USERNAME", None)
        self.password = password or os.getenv("MQTT_PASSWORD", None)
        self.client_id = client_id

        # Internal state
        self.client = None
        self.is_connected = False
        self.mock_mode = False
        self.total_published = 0
        self.topic_counts: Dict[str, int] = {
            self.TOPIC_TELEMETRY: 0,
            self.TOPIC_FAULTS: 0,
            self.TOPIC_HEALTH: 0,
            self.TOPIC_ALERTS: 0,
        }

        # In-memory buffer of recent published payloads (useful for mock inspection & tests)
        self.published_buffer: deque = deque(maxlen=200)

        # Initialize connection or mock fallback
        forced_mock = mock_mode if mock_mode is not None else (os.getenv("MQTT_MOCK_MODE", "").lower() in ("1", "true"))
        if forced_mock:
            self._activate_mock_mode("Explicit mock mode enabled")
        else:
            self._connect()

    def _connect(self):
        """Attempt connection to real MQTT broker using paho-mqtt."""
        try:
            import paho.mqtt.client as mqtt

            # Compatibility across paho-mqtt v1 and v2
            try:
                self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=self.client_id)
            except AttributeError:
                self.client = mqtt.Client(client_id=self.client_id)

            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)

            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect

            logger.info(f"Connecting to MQTT Broker at {self.broker}:{self.port}...")
            self.client.connect_async(self.broker, self.port, keepalive=60)
            self.client.loop_start()

            # Wait briefly for connection verification
            timeout = 1.5
            start = time.time()
            while time.time() - start < timeout and not self.is_connected:
                time.sleep(0.05)

            if not self.is_connected:
                self._activate_mock_mode(f"Broker {self.broker}:{self.port} not reachable within {timeout}s")

        except ImportError:
            self._activate_mock_mode("paho-mqtt package not installed")
        except Exception as e:
            self._activate_mock_mode(f"MQTT connection failed: {e}")

    def _on_connect(self, client, userdata, flags, rc, *extra):
        if rc == 0:
            self.is_connected = True
            self.mock_mode = False
            logger.info(f"Successfully connected to MQTT Broker ({self.broker}:{self.port})")
        else:
            logger.warning(f"MQTT broker connection refused with code {rc}")
            self._activate_mock_mode(f"Connection refused (code {rc})")

    def _on_disconnect(self, client, userdata, rc, *extra):
        self.is_connected = False
        if rc != 0:
            logger.warning(f"Unexpected disconnection from MQTT broker (code {rc}). Switching to mock mode.")
            self.mock_mode = True

    def _activate_mock_mode(self, reason: str):
        self.mock_mode = True
        self.is_connected = False
        logger.info(f"[SIMULATION MODE] MQTT Publisher running in MOCK MODE ({reason}). Payloads safely recorded locally.")

    def _format_telemetry_payload(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all 18 mandatory telemetry fields are formatted as clean JSON numbers."""
        now = telemetry.get("timestamp", time.time())
        cht = float(telemetry.get("cht", telemetry.get("cylinder_head_temp", telemetry.get("engine_temp", 96.5))))
        oil_t = float(telemetry.get("oil_temperature", telemetry.get("oil_temp", 88.0)))
        egt = float(telemetry.get("egt", telemetry.get("exhaust_gas_temp", 760.0)))
        map_val = float(telemetry.get("map", telemetry.get("manifold_pressure", 29.20)))
        alt = float(telemetry.get("altitude", 8000.0))
        amb_t = float(telemetry.get("ambient_temperature", telemetry.get("ambient_temp", 18.0)))

        # Derived boost pressure & coolant temperature if not explicitly supplied
        boost = float(telemetry.get("boost_pressure", max(0.0, map_val - (29.92 * max(0.01, 1.0 - 6.875e-6 * alt) ** 5.2559))))
        coolant = float(telemetry.get("coolant_temperature", cht * 0.88 + amb_t * 0.08))

        return {
            "timestamp": round(now, 3),
            "rpm": round(float(telemetry.get("rpm", 4600.0)), 1),
            "cht": round(cht, 1),
            "egt": round(egt, 1),
            "oil_pressure": round(float(telemetry.get("oil_pressure", 4.10)), 2),
            "oil_temperature": round(oil_t, 1),
            "fuel_pressure": round(float(telemetry.get("fuel_pressure", 3.25)), 2),
            "fuel_flow": round(float(telemetry.get("fuel_flow", 22.40)), 2),
            "map": round(map_val, 2),
            "boost_pressure": round(boost, 2),
            "vibration": round(float(telemetry.get("vibration", 1.65)), 2),
            "engine_load": round(float(telemetry.get("engine_load", 65.0)), 1),
            "throttle": round(float(telemetry.get("throttle", 65.0)), 1),
            "altitude": round(alt, 0),
            "ambient_temperature": round(amb_t, 1),
            "coolant_temperature": round(coolant, 1),
            "battery_voltage": round(float(telemetry.get("battery_voltage", 13.85)), 2),
            "engine_hours": round(float(telemetry.get("engine_hours", 1247.4)), 2),
        }

    def _publish_raw(self, topic: str, payload_dict: Dict[str, Any], qos: int = 0) -> bool:
        """Internal publish dispatcher (supports both real MQTT and mock mode)."""
        payload_str = json.dumps(payload_dict)
        now = time.time()

        record = {
            "topic": topic,
            "timestamp": now,
            "payload": payload_dict,
            "mock_mode": self.mock_mode,
        }
        self.published_buffer.append(record)
        self.total_published += 1
        self.topic_counts[topic] = self.topic_counts.get(topic, 0) + 1

        if self.is_connected and self.client is not None:
            try:
                self.client.publish(topic, payload_str, qos=qos)
                return True
            except Exception as e:
                logger.error(f"Failed to publish to {topic}: {e}")
                return False
        else:
            # Successfully logged in mock mode
            return True

    def publish_telemetry(self, telemetry: Dict[str, Any]) -> bool:
        """
        Publishes 18-signal simulated engine telemetry to uav/engine/telemetry.
        """
        payload = self._format_telemetry_payload(telemetry)
        return self._publish_raw(self.TOPIC_TELEMETRY, payload, qos=0)

    def publish_fault(self, fault_event: Dict[str, Any]) -> bool:
        """
        Publishes fault injection events to uav/engine/faults.
        """
        payload = {
            "timestamp": fault_event.get("timestamp", time.time()),
            "fault_type": fault_event.get("fault_type", "NONE"),
            "severity": fault_event.get("severity", "NONE"),
            "target_severity": fault_event.get("target_severity", 0.0),
            "current_intensity": fault_event.get("current_intensity", fault_event.get("current_severity", 0.0)),
            "action": fault_event.get("action", fault_event.get("event", "UPDATED")),
            "stresses": fault_event.get("stresses", {}),
        }
        return self._publish_raw(self.TOPIC_FAULTS, payload, qos=1)

    def publish_health(self, health_data: Dict[str, Any]) -> bool:
        """
        Publishes component health and wear metrics to uav/engine/health.
        """
        payload = {
            "timestamp": time.time(),
            "overall_health_score": health_data.get("overall_health_score", health_data.get("health_score", 95.0)),
            "health_status": health_data.get("status", health_data.get("health_status", "HEALTHY")),
            "subsystems": health_data.get("subsystems", health_data.get("component_health", {})),
            "estimated_rul_hours": health_data.get("estimated_rul_hours", health_data.get("rul_hours", 450.0)),
            "degradation_velocity": health_data.get("degradation_velocity", 0.0),
        }
        return self._publish_raw(self.TOPIC_HEALTH, payload, qos=1)

    def publish_alert(self, alert_data: Dict[str, Any]) -> bool:
        """
        Publishes AI anomaly / diagnostic alert events to uav/engine/alerts.
        """
        payload = {
            "timestamp": alert_data.get("timestamp", time.time()),
            "alert_id": alert_data.get("alert_id", f"ALT-{int(time.time()*1000)%100000}"),
            "anomaly_detected": alert_data.get("anomaly_detected", alert_data.get("is_anomaly", True)),
            "anomaly_score": alert_data.get("anomaly_score", alert_data.get("anomaly_intensity", 85.0)),
            "predicted_fault": alert_data.get("predicted_fault", alert_data.get("fault_type", "OVERHEATING")),
            "confidence": alert_data.get("confidence", 95.0),
            "severity": alert_data.get("severity", "WARNING"),
            "directive": alert_data.get("directive", alert_data.get("message", "Investigate engine telemetry divergence")),
            "xai_top_factor": alert_data.get("xai_top_factor", "Cylinder Head Temp (CHT)"),
        }
        return self._publish_raw(self.TOPIC_ALERTS, payload, qos=1)

    def get_stats(self) -> Dict[str, Any]:
        """Return publishing statistics and current broker connection status."""
        return {
            "broker": f"{self.broker}:{self.port}",
            "is_connected": self.is_connected,
            "mock_mode": self.mock_mode,
            "total_published": self.total_published,
            "topic_counts": dict(self.topic_counts),
            "buffer_depth": len(self.published_buffer),
        }

    def get_recent_messages(self, topic: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent published JSON records."""
        items = list(self.published_buffer)
        if topic:
            items = [x for x in items if x["topic"] == topic]
        return items[-limit:]

    def stop(self):
        """Cleanly shutdown MQTT network loop."""
        if self.client is not None and self.is_connected:
            try:
                self.client.loop_stop()
                self.client.disconnect()
            except Exception:
                pass
        self.is_connected = False

# Backward-compatibility alias
Publisher = MQTTSimulatorPublisher
