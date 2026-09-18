"""
Proxy export for simulator.simulator.fault_injection
Ensures compatibility with both simulator/fault_injection.py and simulator/simulator/fault_injection.py
"""

from simulator.fault_injection import (
    FaultType,
    FaultSeverity,
    FaultInjectionEngine,
    get_fault_delta,
)

__all__ = [
    "FaultType",
    "FaultSeverity",
    "FaultInjectionEngine",
    "get_fault_delta",
]
