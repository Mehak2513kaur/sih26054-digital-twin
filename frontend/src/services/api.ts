import { useEffect, useState, useRef } from 'react';
import { FullEngineState, HistoricalPoint } from '../types/engine';

const API_BASE = 'http://localhost:8000/api';
const WS_URL = 'ws://localhost:8000/ws/engine';

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}

export async function fetchSensorsHistory(limit: number = 100): Promise<{ count: number; history: HistoricalPoint[] }> {
  const res = await fetch(`${API_BASE}/sensors/history?limit=${limit}`);
  return res.json();
}

export async function fetchMissions() {
  const res = await fetch(`${API_BASE}/missions`);
  return res.json();
}

export async function startMission(scenario: string, altitude?: number, ambient_temp?: number, throttle?: number) {
  const res = await fetch(`${API_BASE}/missions/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario, altitude, ambient_temp, throttle }),
  });
  return res.json();
}

export async function pauseMission() {
  const res = await fetch(`${API_BASE}/missions/pause`, { method: 'POST' });
  return res.json();
}

export async function resumeMission() {
  const res = await fetch(`${API_BASE}/missions/resume`, { method: 'POST' });
  return res.json();
}

export async function stopMission() {
  const res = await fetch(`${API_BASE}/missions/stop`, { method: 'POST' });
  return res.json();
}

export async function resetMission() {
  const res = await fetch(`${API_BASE}/missions/reset`, { method: 'POST' });
  return res.json();
}

export async function injectFault(fault_type: string, severity: string = 'MEDIUM', ramp_duration: number = 20) {
  const res = await fetch(`${API_BASE}/fault/inject`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ fault_type, severity, ramp_duration }),
  });
  return res.json();
}

export async function clearFault() {
  const res = await fetch(`${API_BASE}/fault/clear`, { method: 'POST' });
  return res.json();
}

export async function fetchMissionReplay(mission_id: string) {
  const res = await fetch(`${API_BASE}/missions/${mission_id}/replay`);
  return res.json();
}

export async function fetchReportJson(mission_id: string) {
  const res = await fetch(`${API_BASE}/report/${mission_id}`);
  return res.json();
}

export function getReportPdfUrl(mission_id: string) {
  return `${API_BASE}/report/${mission_id}/pdf`;
}

export async function startDemo() {
  const res = await fetch(`${API_BASE}/demo/start`, { method: 'POST' });
  return res.json();
}

export async function pauseDemo() {
  const res = await fetch(`${API_BASE}/demo/pause`, { method: 'POST' });
  return res.json();
}

export async function resumeDemo() {
  const res = await fetch(`${API_BASE}/demo/resume`, { method: 'POST' });
  return res.json();
}

export async function restartDemo() {
  const res = await fetch(`${API_BASE}/demo/restart`, { method: 'POST' });
  return res.json();
}

export async function stopDemo() {
  const res = await fetch(`${API_BASE}/demo/stop`, { method: 'POST' });
  return res.json();
}

export async function resetDemo() {
  return restartDemo();
}

export async function fetchDemoStatus() {
  const res = await fetch(`${API_BASE}/demo/status`);
  return res.json();
}

export async function acknowledgeAlert(alert_id: number) {
  const res = await fetch(`${API_BASE}/alerts/acknowledge`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ alert_id }),
  });
  return res.json();
}

export function useEngineStream() {
  const [data, setData] = useState<FullEngineState | null>(null);
  const [history, setHistory] = useState<HistoricalPoint[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Initial fetch of history
    fetchSensorsHistory(80).then((res) => {
      if (res?.history) {
        setHistory(res.history);
      }
    }).catch(() => {});

    let reconnectTimer: ReturnType<typeof setTimeout>;

    function connect() {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const packet: FullEngineState = JSON.parse(event.data);
          setData(packet);

          // Append to local sparkline/history buffer
          setHistory((prev) => {
            const nextPoint: HistoricalPoint = {
              time: packet.time_str,
              timestamp: packet.timestamp,
              rpm: packet.telemetry.rpm,
              engine_temp: packet.telemetry.engine_temp,
              oil_pressure: packet.telemetry.oil_pressure,
              oil_temp: packet.telemetry.oil_temp,
              vibration: packet.telemetry.vibration,
              fuel_flow: packet.telemetry.fuel_flow,
              exhaust_gas_temp: packet.telemetry.exhaust_gas_temp,
              expected_temp: packet.expected_physics.expected_engine_temp,
              expected_oil_press: packet.expected_physics.expected_oil_pressure,
              expected_vib: packet.expected_physics.expected_vibration,
              health_score: packet.health.health_score,
              rul_hours: packet.ml_prediction.rul.rul_hours,
            };
            const updated = [...prev, nextPoint];
            return updated.slice(-120); // Keep last 120 points for smooth performance
          });
        } catch (e) {
          console.error("WS Parse error:", e);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        reconnectTimer = setTimeout(connect, 2000);
      };

      ws.onerror = () => {
        ws.close();
      };
    }

    connect();

    return () => {
      clearTimeout(reconnectTimer);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return { data, history, isConnected };
}
