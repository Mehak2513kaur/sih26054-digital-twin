import React, { useState } from 'react';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend, 
  CartesianGrid 
} from 'recharts';
import { FullEngineState, HistoricalPoint } from '../types/engine';
import { HealthGauge } from '../components/HealthGauge';
import { SensorCard } from '../components/SensorCard';
import { 
  AlertTriangle, 
  BrainCircuit, 
  Hourglass, 
  CheckCircle2, 
  Layers, 
  Sliders, 
  Bell, 
  ShieldAlert 
} from 'lucide-react';
import { acknowledgeAlert } from '../services/api';

interface OverviewProps {
  data: FullEngineState | null;
  history: HistoricalPoint[];
}

export const OverviewDashboard: React.FC<OverviewProps> = ({ data, history }) => {
  const [activeSignals, setActiveSignals] = useState<{ [key: string]: boolean }>({
    engine_temp: true,
    expected_temp: true,
    rpm: false,
    oil_pressure: true,
    vibration: true,
    exhaust_gas_temp: false
  });

  const [timeWindow, setTimeWindow] = useState<'30s' | '1m' | '3m'>('1m');

  const tel = data?.telemetry;
  const exp = data?.expected_physics;
  const res = data?.residuals;
  const der = data?.derived;
  const ml = data?.ml_prediction;
  const health = data?.health;
  const rec = data?.recommendation;
  const alerts = data?.active_alerts || [];

  const toggleSignal = (sig: string) => {
    setActiveSignals((prev) => ({ ...prev, [sig]: !prev[sig] }));
  };

  // Filter history based on time window
  const sliceCount = timeWindow === '30s' ? 30 : timeWindow === '1m' ? 60 : 120;
  const chartData = history.slice(-sliceCount);

  return (
    <div className="space-y-6">
      {/* Top Banner: Primary Engine Health, AI Fault Prediction & RUL */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* 1. Large Circular Health Gauge */}
        <HealthGauge health={health} engineHours={tel?.engine_hours || 1247.4} />

        {/* 2. AI Fault Classification & Early Anomaly Card */}
        <div className="glass-panel rounded-xl p-5 flex flex-col justify-between border-slate-800 relative overflow-hidden">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400">
            <span className="flex items-center gap-1.5 uppercase tracking-wider font-semibold">
              <BrainCircuit className="w-4 h-4 text-cyan-400" />
              AI Powertrain Diagnostics
            </span>
            <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${
              ml?.is_anomaly 
                ? 'bg-rose-500/10 text-rose-400 border-rose-500/30 animate-pulse' 
                : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
            }`}>
              {ml?.is_anomaly ? 'ANOMALY DETECTED' : 'NORMAL ENVELOPE'}
            </span>
          </div>

          <div className="my-3">
            <div className="text-[11px] font-mono text-slate-400">Classified Fault State:</div>
            <div className="text-2xl font-bold font-mono tracking-tight text-white flex items-center gap-2">
              <span className={ml?.predicted_fault !== 'NORMAL' ? 'text-amber-400' : 'text-emerald-400'}>
                {ml?.predicted_fault?.replace(/_/g, ' ') || 'NORMAL'}
              </span>
            </div>
            <div className="flex items-center gap-2 mt-1.5 text-xs font-mono text-slate-400">
              <span>Confidence:</span>
              <span className="text-white font-bold">{ml?.confidence?.toFixed(1) || 95.0}%</span>
              <span className="text-slate-600">•</span>
              <span>Anomaly Intensity:</span>
              <span className="text-cyan-300 font-bold">{ml?.anomaly_intensity?.toFixed(0) || 0}/100</span>
            </div>
          </div>

          {/* Root-cause highlight */}
          <div className="pt-2.5 border-t border-slate-800/80 text-[11px] font-mono text-slate-300">
            <span className="text-slate-500">Root Cause: </span>
            <span>{ml?.explainability?.root_cause_summary || 'All primary sensors nominal.'}</span>
          </div>
        </div>

        {/* 3. Prognostic Remaining Useful Life (RUL) Card */}
        <div className="glass-panel rounded-xl p-5 flex flex-col justify-between border-slate-800 relative overflow-hidden">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400">
            <span className="flex items-center gap-1.5 uppercase tracking-wider font-semibold">
              <Hourglass className="w-4 h-4 text-cyan-400" />
              Prognostic Remaining Life
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-slate-800 text-slate-400 border border-slate-700">
              SIMULATED ESTIMATE
            </span>
          </div>

          <div className="my-3">
            <div className="text-[11px] font-mono text-slate-400">Estimated Life to Overhaul (TBO):</div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold font-mono text-white tracking-tight">
                {ml?.rul?.rul_hours?.toFixed(1) || 480.0}
              </span>
              <span className="text-sm font-mono text-cyan-400 font-bold">HOURS</span>
            </div>
            <div className="flex items-center gap-2 mt-1.5 text-xs font-mono text-slate-400">
              <span>Degradation:</span>
              <span className="text-rose-400 font-bold">+{ml?.rul?.degradation_rate_pct?.toFixed(1) || 0.2}%/hr</span>
              <span className="text-slate-600">•</span>
              <span>Bounds:</span>
              <span className="text-slate-300">
                [{ml?.rul?.confidence_interval?.lower?.toFixed(0) || 440}h - {ml?.rul?.confidence_interval?.upper?.toFixed(0) || 500}h]
              </span>
            </div>
          </div>

          <div className="pt-2.5 border-t border-slate-800/80 text-[11px] font-mono text-slate-400 flex justify-between">
            <span>Confidence Index:</span>
            <span className="text-emerald-400 font-bold">{ml?.rul?.confidence_pct || 94.0}%</span>
          </div>
        </div>
      </div>

      {/* Live Engineering Sensor Cards Grid (12 Cards) */}
      <div>
        <div className="flex items-center justify-between mb-3 text-xs font-mono uppercase tracking-wider text-slate-400">
          <span>Live Powertrain Telemetry Matrix (CAN Frames)</span>
          <span className="text-slate-500">Sampling Rate: 10 Hz</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3.5">
          <SensorCard
            label="Engine Speed"
            value={tel?.rpm || 4600}
            unit="RPM"
            rate={der?.rpm_change}
            rateUnit="/s"
            status={tel && tel.rpm > 5500 ? 'WARNING' : 'NORMAL'}
          />
          <SensorCard
            label="Cylinder Head (CHT)"
            value={tel?.engine_temp || 96.5}
            unit="°C"
            expected={exp?.expected_engine_temp}
            residual={res?.residual_engine_temp}
            rate={der?.temperature_rate}
            status={tel && tel.engine_temp > 120 ? 'CRITICAL' : tel && tel.engine_temp > 108 ? 'WARNING' : 'NORMAL'}
          />
          <SensorCard
            label="Oil Pressure"
            value={tel?.oil_pressure || 4.1}
            unit="bar"
            expected={exp?.expected_oil_pressure}
            residual={res?.residual_oil_pressure}
            rate={der?.oil_pressure_rate}
            status={tel && tel.oil_pressure < 2.0 ? 'CRITICAL' : tel && tel.oil_pressure < 2.8 ? 'WARNING' : 'NORMAL'}
          />
          <SensorCard
            label="Oil Temperature"
            value={tel?.oil_temp || 88.0}
            unit="°C"
            expected={exp?.expected_oil_temp}
            residual={res?.residual_oil_temp}
            status={tel && tel.oil_temp > 115 ? 'CRITICAL' : tel && tel.oil_temp > 102 ? 'WARNING' : 'NORMAL'}
          />
          <SensorCard
            label="RMS Vibration"
            value={tel?.vibration || 1.65}
            unit="mm/s"
            expected={exp?.expected_vibration}
            residual={res?.residual_vibration}
            rate={der?.vibration_rate}
            status={tel && tel.vibration > 4.5 ? 'CRITICAL' : tel && tel.vibration > 2.8 ? 'WARNING' : 'NORMAL'}
          />
          <SensorCard
            label="Fuel Flow"
            value={tel?.fuel_flow || 22.4}
            unit="L/h"
            expected={exp?.expected_fuel_flow}
            residual={res?.residual_fuel_flow}
            rate={der?.fuel_flow_change}
            rateUnit="/s"
          />
          <SensorCard
            label="Manifold Press (MAP)"
            value={tel?.manifold_pressure || 29.2}
            unit="inHg"
            expected={exp?.expected_manifold_pressure}
            residual={res?.residual_manifold_pressure}
          />
          <SensorCard
            label="Exhaust Gas (EGT)"
            value={tel?.exhaust_gas_temp || 760}
            unit="°C"
            expected={exp?.expected_exhaust_gas_temp}
            residual={res?.residual_exhaust_gas_temp}
            status={tel && tel.exhaust_gas_temp > 850 ? 'CRITICAL' : 'NORMAL'}
          />
          <SensorCard
            label="Throttle Setpoint"
            value={tel?.throttle || 65}
            unit="%"
          />
          <SensorCard
            label="Engine Load"
            value={tel?.engine_load || 65}
            unit="%"
          />
          <SensorCard
            label="Flight Altitude"
            value={tel?.altitude || 8000}
            unit="ft"
          />
          <SensorCard
            label="Avionics Battery"
            value={tel?.battery_voltage || 13.8}
            unit="V"
          />
        </div>
      </div>

      {/* Multi-Signal Real-Time Live Telemetry Chart */}
      <div className="glass-panel rounded-xl p-5 border-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono uppercase font-bold tracking-wider text-slate-300">
              Multi-Signal Real-Time Streaming (CAN Telemetry & Virtual Twin)
            </span>
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
          </div>

          {/* Time Window Controls */}
          <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-800 rounded p-1 text-xs font-mono">
            {(['30s', '1m', '3m'] as const).map((w) => (
              <button
                key={w}
                onClick={() => setTimeWindow(w)}
                className={`px-2 py-0.5 rounded text-[11px] font-bold transition-all ${
                  timeWindow === w ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' : 'text-slate-400 hover:text-white'
                }`}
              >
                {w}
              </button>
            ))}
          </div>
        </div>

        {/* Signal Selector Toggles */}
        <div className="flex flex-wrap items-center gap-2 mb-4 text-xs font-mono">
          <span className="text-slate-500 mr-1 text-[11px]">Signals:</span>
          {[
            { id: 'engine_temp', label: 'Observed CHT (°C)', color: '#f43f5e' },
            { id: 'expected_temp', label: 'Expected CHT (°C)', color: '#38bdf8' },
            { id: 'oil_pressure', label: 'Oil Press (bar)', color: '#f59e0b' },
            { id: 'vibration', label: 'Vibration (mm/s)', color: '#a855f7' },
            { id: 'rpm', label: 'RPM / 100', color: '#10b981' },
            { id: 'exhaust_gas_temp', label: 'EGT / 10 (°C)', color: '#ec4899' },
          ].map((s) => {
            const isSel = activeSignals[s.id];
            return (
              <button
                key={s.id}
                onClick={() => toggleSignal(s.id)}
                className={`px-2.5 py-1 rounded text-[11px] flex items-center gap-1.5 border transition-all ${
                  isSel
                    ? 'bg-slate-900 text-white font-bold'
                    : 'bg-slate-900/40 text-slate-500 border-slate-800 hover:text-slate-300'
                }`}
                style={{ borderColor: isSel ? s.color : undefined }}
              >
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: s.color }} />
                <span>{s.label}</span>
              </button>
            );
          })}
        </div>

        {/* Chart View */}
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.6} />
              <XAxis 
                dataKey="time" 
                stroke="#64748b" 
                tick={{ fontSize: 10, fontFamily: 'monospace' }} 
              />
              <YAxis 
                stroke="#64748b" 
                tick={{ fontSize: 10, fontFamily: 'monospace' }} 
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  border: '1px solid #1e293b',
                  borderRadius: '8px',
                  fontSize: '11px',
                  fontFamily: 'monospace'
                }}
              />
              {activeSignals.engine_temp && (
                <Line 
                  type="monotone" 
                  dataKey="engine_temp" 
                  stroke="#f43f5e" 
                  strokeWidth={2} 
                  dot={false} 
                  name="Observed CHT" 
                  isAnimationActive={false} 
                />
              )}
              {activeSignals.expected_temp && (
                <Line 
                  type="monotone" 
                  dataKey="expected_temp" 
                  stroke="#38bdf8" 
                  strokeWidth={2} 
                  strokeDasharray="4 4" 
                  dot={false} 
                  name="Expected CHT" 
                  isAnimationActive={false} 
                />
              )}
              {activeSignals.oil_pressure && (
                <Line 
                  type="monotone" 
                  dataKey="oil_pressure" 
                  stroke="#f59e0b" 
                  strokeWidth={1.8} 
                  dot={false} 
                  name="Oil Press (bar)" 
                  isAnimationActive={false} 
                />
              )}
              {activeSignals.vibration && (
                <Line 
                  type="monotone" 
                  dataKey="vibration" 
                  stroke="#a855f7" 
                  strokeWidth={1.8} 
                  dot={false} 
                  name="Vibration (mm/s)" 
                  isAnimationActive={false} 
                />
              )}
              {activeSignals.rpm && (
                <Line 
                  type="monotone" 
                  dataKey={(d) => (d.rpm ? d.rpm / 100.0 : 0)} 
                  stroke="#10b981" 
                  strokeWidth={1.5} 
                  dot={false} 
                  name="RPM / 100" 
                  isAnimationActive={false} 
                />
              )}
              {activeSignals.exhaust_gas_temp && (
                <Line 
                  type="monotone" 
                  dataKey={(d) => (d.exhaust_gas_temp ? d.exhaust_gas_temp / 10.0 : 0)} 
                  stroke="#ec4899" 
                  strokeWidth={1.5} 
                  dot={false} 
                  name="EGT / 10" 
                  isAnimationActive={false} 
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Active Alerts Panel */}
      {alerts.length > 0 && (
        <div className="glass-panel rounded-xl p-4 border-amber-500/30 bg-amber-950/10">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2 text-xs font-mono uppercase font-bold text-amber-400">
              <Bell className="w-4 h-4" />
              <span>Active Early Warnings & Alarms ({alerts.length})</span>
            </div>
          </div>
          <div className="space-y-2">
            {alerts.slice(0, 3).map((a) => (
              <div 
                key={a.id}
                className="p-3 rounded-lg bg-slate-900/90 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs font-mono"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className={`px-1.5 py-0.2 rounded text-[10px] font-bold ${
                      a.severity === 'CRITICAL' ? 'bg-rose-500/20 text-rose-400' : 'bg-amber-500/20 text-amber-400'
                    }`}>
                      {a.severity}
                    </span>
                    <span className="font-bold text-slate-200">{a.title}</span>
                    <span className="text-slate-500">[{a.time_str}]</span>
                  </div>
                  <p className="text-slate-400 text-[11px] mt-1">{a.message}</p>
                  <p className="text-cyan-300 text-[11px] mt-0.5 font-semibold">Action: {a.recommended_action}</p>
                </div>
                {!a.acknowledged && (
                  <button
                    onClick={() => acknowledgeAlert(a.id)}
                    className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] whitespace-nowrap self-start sm:self-center"
                  >
                    Acknowledge
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
