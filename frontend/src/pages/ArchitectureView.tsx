import React from 'react';
import { FullEngineState } from '../types/engine';
import { 
  Network, 
  Cpu, 
  Activity, 
  ShieldCheck, 
  HardDrive, 
  Laptop, 
  ArrowDown, 
  ArrowRight, 
  CheckCircle2, 
  Radio 
} from 'lucide-react';

interface ArchitectureProps {
  data: FullEngineState | null;
}

export const ArchitectureView: React.FC<ArchitectureProps> = ({ data }) => {
  const can = data?.can_bus;
  const qual = data?.quality;

  const pipelineStages = [
    {
      title: '1. UAV ENGINE & SENSORS',
      icon: Activity,
      color: 'border-cyan-500/50 bg-cyan-950/20 text-cyan-300',
      desc: 'Rotax 915 iS class 4-cylinder turbocharged piston engine telemetry: RPM, CHT, EGT, Oil P/T, Fuel Flow, MAP, Vibration, Altitude.'
    },
    {
      title: '2. CAN / SOCKETCAN DATA LAYER',
      icon: Radio,
      color: 'border-blue-500/50 bg-blue-950/20 text-blue-300',
      desc: 'Virtual vcan0 socket bus streaming packaged 11/29-bit CAN identifiers at 10-20 Hz with simulated latency (1.9 ms) and 0.00% packet loss.'
    },
    {
      title: '3. EDGE PREPROCESSING',
      icon: Cpu,
      color: 'border-purple-500/50 bg-purple-950/20 text-purple-300',
      desc: 'ADC transient spike rejection, sliding window smoothing, and derived feature engineering (temperature_rate, vibration_rate, Z-scores).'
    },
    {
      title: '4. DIGITAL TWIN CORE',
      icon: Network,
      color: 'border-emerald-500/50 bg-emerald-950/20 text-emerald-300',
      desc: 'Thermodynamic first-principles model calculates expected states. Residual Analyzer computes observed vs expected deltas (Observed - Expected).'
    },
    {
      title: '5. AI/ML ENGINE & XAI',
      icon: Cpu,
      color: 'border-amber-500/50 bg-amber-950/20 text-amber-300',
      desc: 'Isolation Forest (unsupervised anomaly detection) + Multi-Class Random Forest (8 fault classes) + Physics-guided Prognostic RUL + Feature Attribution.'
    },
    {
      title: '6. HEALTH FUSION & WEBSOCKET',
      icon: HardDrive,
      color: 'border-rose-500/50 bg-rose-950/20 text-rose-300',
      desc: 'Composite 0-100 Health Score fusion, SQLite mission history persistence, and real-time WebSocket broadcast server.'
    },
    {
      title: '7. OPERATOR DASHBOARD',
      icon: Laptop,
      color: 'border-cyan-500/50 bg-cyan-950/20 text-cyan-300',
      desc: 'Aerospace-grade React + Vite + Tailwind operator console with live cockpits, chronological replayer, and automated PDF debrief generation.'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="glass-panel rounded-xl p-5 border-cyan-500/30">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center">
            <Network className="w-6 h-6 text-cyan-400" />
          </div>
          <div>
            <h2 className="text-base font-bold font-mono tracking-wide text-white uppercase flex items-center gap-2">
              <span>SYSTEM ARCHITECTURE & PROTOCOL DATA FLOW</span>
              <span className="text-xs px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-normal">
                DRDO PROBLEM STATEMENT 26054
              </span>
            </h2>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              End-to-end data pipeline: from sensor ingestion over simulated CAN bus to edge signal cleansing, 
              first-principles Digital Twin modeling, machine learning prognostic fusion, and WebSocket telemetry.
            </p>
          </div>
        </div>
      </div>

      {/* Simulated CAN Link & Signal Quality Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* CAN Bus Status Box */}
        <div className="glass-panel rounded-xl p-5 border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase font-bold text-slate-300 tracking-wider">
              Simulated CAN / SocketCAN Protocol Layer
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              {can?.status || 'CONNECTED'}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs font-mono pt-1">
            <div className="p-3 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-500 text-[11px]">Bus Interface:</span>
              <div className="text-white font-bold mt-0.5">{can?.bus_type || 'SocketCAN vcan0'}</div>
            </div>
            <div className="p-3 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-500 text-[11px]">Packet Throughput:</span>
              <div className="text-cyan-300 font-bold mt-0.5">{can?.packets_per_sec || 15} pkts/sec</div>
            </div>
            <div className="p-3 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-500 text-[11px]">Bus Latency & Jitter:</span>
              <div className="text-white font-bold mt-0.5">{can?.latency_ms || 2.1} ms</div>
            </div>
            <div className="p-3 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-500 text-[11px]">Packet Loss Rate:</span>
              <div className="text-emerald-400 font-bold mt-0.5">{can?.packet_loss_pct || 0.0}%</div>
            </div>
          </div>
        </div>

        {/* Edge Sensor Stream Quality Monitor Box */}
        <div className="glass-panel rounded-xl p-5 border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase font-bold text-slate-300 tracking-wider">
              Edge Sensor Quality & Glitch Rejection
            </span>
            <span className="text-xs font-mono text-slate-500">
              Total Ingested: {qual?.total_packets || 0}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs font-mono pt-1">
            <div className="p-3 rounded bg-slate-900 border border-slate-800">
              <div className="flex justify-between text-[11px]">
                <span className="text-slate-500">RPM Stream:</span>
                <span className="text-emerald-400 font-bold">{qual?.quality_rpm || 99.8}%</span>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full mt-1.5 overflow-hidden">
                <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${qual?.quality_rpm || 99.8}%` }} />
              </div>
            </div>

            <div className="p-3 rounded bg-slate-900 border border-slate-800">
              <div className="flex justify-between text-[11px]">
                <span className="text-slate-500">Thermal Stream:</span>
                <span className="text-emerald-400 font-bold">{qual?.quality_temp || 98.9}%</span>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full mt-1.5 overflow-hidden">
                <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${qual?.quality_temp || 98.9}%` }} />
              </div>
            </div>

            <div className="p-3 rounded bg-slate-900 border border-slate-800">
              <div className="flex justify-between text-[11px]">
                <span className="text-slate-500">Hydraulic Oil:</span>
                <span className="text-emerald-400 font-bold">{qual?.quality_oil || 97.5}%</span>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full mt-1.5 overflow-hidden">
                <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${qual?.quality_oil || 97.5}%` }} />
              </div>
            </div>

            <div className="p-3 rounded bg-slate-900 border border-slate-800">
              <div className="flex justify-between text-[11px]">
                <span className="text-slate-500">Vibration Stream:</span>
                <span className="text-emerald-400 font-bold">{qual?.quality_vib || 99.1}%</span>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full mt-1.5 overflow-hidden">
                <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${qual?.quality_vib || 99.1}%` }} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Visual Pipeline Block Flow */}
      <div className="glass-panel rounded-xl p-6 border-slate-800">
        <h3 className="text-xs font-mono uppercase font-bold text-slate-300 tracking-wider mb-6 text-center">
          Continuous Real-Time Data Pipeline Architecture
        </h3>

        <div className="space-y-4 max-w-2xl mx-auto">
          {pipelineStages.map((stage, i) => {
            const Icon = stage.icon;
            return (
              <React.Fragment key={stage.title}>
                <div className={`p-4 rounded-xl border ${stage.color} flex items-start gap-4 transition-all hover:scale-[1.01]`}>
                  <div className="w-9 h-9 rounded-lg bg-slate-900/80 border border-slate-800 flex items-center justify-center shrink-0 mt-0.5">
                    <Icon className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold font-mono text-white">{stage.title}</h4>
                    <p className="text-xs font-mono text-slate-300 mt-1 leading-relaxed">{stage.desc}</p>
                  </div>
                </div>
                {i < pipelineStages.length - 1 && (
                  <div className="flex justify-center my-1">
                    <ArrowDown className="w-4 h-4 text-cyan-400/60 animate-bounce" />
                  </div>
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>
    </div>
  );
};
