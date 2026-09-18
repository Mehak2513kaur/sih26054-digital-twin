import random
import time
from typing import Dict, Any

class CANBusSimulator:
    '''
    Simulates CAN / SocketCAN aerospace data link layer:
    - Packet transmission rates (12 - 18 Hz)
    - Protocol frame latency and jitter (1.8 - 2.8 ms)
    - Bus load percentage and error counter
    '''
    def __init__(self):
        self.status = "CONNECTED"
        self.bus_type = "SocketCAN (Virtual vcan0)"
        self.baud_rate = "1 Mbps"
        self.packet_count = 0
        self.error_count = 0
        self.start_time = time.time()
        self.latency_ms = 2.1
        self.packet_loss_pct = 0.0

    def step(self) -> Dict[str, Any]:
        self.packet_count += 1
        now = time.time()
        elapsed = max(0.1, now - self.start_time)
        packets_per_sec = round(self.packet_count / elapsed, 1)
        
        self.latency_ms = round(1.9 + random.gauss(0, 0.2), 2)
        if random.random() < 0.001:
            self.error_count += 1
        self.packet_loss_pct = round((self.error_count / max(1, self.packet_count)) * 100.0, 3)
        bus_load = round(min(85.0, 18.0 + (packets_per_sec / 20.0) * 12.0 + random.gauss(0, 0.5)), 1)

        return {
            "status": self.status,
            "bus_type": self.bus_type,
            "baud_rate": self.baud_rate,
            "packets_per_sec": min(20.0, max(8.0, packets_per_sec)),
            "latency_ms": max(1.2, self.latency_ms),
            "packet_loss_pct": self.packet_loss_pct,
            "bus_load_pct": bus_load,
            "total_frames": self.packet_count,
            "error_frames": self.error_count,
            "security": {
                "communication": "SECURE SIMULATION",
                "checksum_algorithm": "CRC-16 Aerospace Standard",
                "authentication": "ENABLED"
            }
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "bus_type": self.bus_type,
            "baud_rate": self.baud_rate,
            "packets_sent": self.packet_count,
            "error_frames": self.error_count,
            "latency_ms": self.latency_ms,
            "packet_loss_pct": self.packet_loss_pct
        }
