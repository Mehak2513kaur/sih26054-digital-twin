"""
Proxy export for simulator.simulator.publisher
Ensures compatibility with both simulator/publisher.py and simulator/simulator/publisher.py
"""

from simulator.publisher import MQTTSimulatorPublisher, Publisher

__all__ = ["MQTTSimulatorPublisher", "Publisher"]
