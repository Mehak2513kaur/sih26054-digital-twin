import React from 'react';
import { Radio, Clock, ShieldCheck, Activity, Play, Pause, RotateCcw, Square, AlertTriangle } from 'lucide-react';
import { FullEngineState } from '../types/engine';
import { startDemo, pauseDemo, resumeDemo, restartDemo, stopDemo } from '../services/api';

interface HeaderProps {
  data: FullEngineState | null;
  isConnected: boolean;
}

export const Header: React.FC<HeaderProps> = ({ data, isConnected }) => {
  const can = data?.can_bus;
  const demo = data?.demo;
  const mission = data?.mission;

  const handleStart = async () => {
    await startDemo();
  };

  const handlePauseResume = async () => {
    if (demo?.is_paused) {
      await resumeDemo();
    } else {
      await pauseDemo();
    }
  };

  const handleRestart = async () => {
    await restartDemo();
  };

  const handleStop = async () => {
    await stopDemo();
  };

  return (
    <header className="h-16 bg-[#0b1120] border-b border-slate-800/80 px-6 flex items-center justify-between sticky top-0 z-50">
      {/* Left: Branding & Subtitle */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-bold tracking-wider text-slate-100 uppercase">
                DIGITAL TWIN <span className="text-cyan-400 font-mono">UAV-PX-01</span>
              </h1>
              <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider rounded bg-amber-500/10 text-amber-400 border border-amber-500/30">
                SIMULATION MODE
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono">
              DRDO PS 26054 — Predictive Powertrain Health Monitoring
            </p>
          </div>
        </div>

        {/* Mission ID Pill */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1 rounded bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300">
          <span className="text-slate-500">MISSION:</span>
          <span className="text-cyan-300 font-bold">{mission?.mission_id || 'IDLE'}</span>
          <span className="text-slate-500">|</span>
          <span className="text-emerald-400">{mission?.scenario_name || 'Normal'}</span>
        </div>
      </div>

      {/* Middle: Dedicated 120-second Demo Control Panel */}
      <div className="flex items-center gap-2.5">
        {demo?.demo_active ? (
          <div className="flex items-center gap-2 bg-slate-900/90 border border-cyan-500/40 rounded-lg p-1.5 shadow-lg shadow-cyan-950/40">
            <div className="flex items-center gap-1.5 px-2 py-0.5 text-xs font-mono">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
              <span className="text-slate-400">STAGE {demo.step_index}/12:</span>
              <span className="font-semibold text-white max-w-[140px] truncate">{demo.step_name}</span>
              <span className="text-cyan-300 font-bold ml-1">
                {Math.floor((demo.current_time_sec || 0) / 60).toString().padStart(2, '0')}:
                {Math.floor((demo.current_time_sec || 0) % 60).toString().padStart(2, '0')} / 02:00
              </span>
            </div>

            {/* Stage timeline pill bar */}
            <div className="hidden xl:flex items-center gap-0.5 w-32 h-2 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 transition-all duration-300"
                style={{ width: `${demo.total_progress_pct || 0}%` }}
              />
            </div>

            {/* Pause / Resume button */}
            <button
              onClick={handlePauseResume}
              title={demo.is_paused ? "Resume Demo" : "Pause Demo"}
              className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-amber-300 transition-colors"
            >
              {demo.is_paused ? <Play className="w-3.5 h-3.5 fill-current" /> : <Pause className="w-3.5 h-3.5" />}
            </button>

            {/* Restart button */}
            <button
              onClick={handleRestart}
              title="Restart Demo from 00:00"
              className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-cyan-300 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>

            {/* Stop button */}
            <button
              onClick={handleStop}
              title="Stop Demo"
              className="p-1.5 rounded bg-rose-950/80 hover:bg-rose-900 text-rose-400 border border-rose-700/50 transition-colors"
            >
              <Square className="w-3.5 h-3.5 fill-current" />
            </button>
          </div>
        ) : (
          <button
            onClick={handleStart}
            className="px-3.5 py-1.5 rounded-lg text-xs font-bold font-mono tracking-wide uppercase transition-all flex items-center gap-2 bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 hover:from-cyan-500 hover:to-blue-500 text-white shadow-lg shadow-cyan-600/30 border border-cyan-400/30"
          >
            <Play className="w-3.5 h-3.5 fill-current text-cyan-200" />
            <span>2-MIN DEMO SEQUENCE</span>
          </button>
        )}
      </div>

      {/* Right: CAN Bus Status & Clock */}
      <div className="flex items-center gap-4 text-xs font-mono">
        {/* Virtual CAN status */}
        <div className="hidden md:flex items-center gap-2.5 px-3 py-1 rounded bg-slate-900/80 border border-slate-800">
          <div className="flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
            <span className="text-slate-400 text-[11px]">CAN:</span>
            <span className={isConnected ? 'text-emerald-300 font-bold' : 'text-rose-400'}>
              {isConnected ? 'ONLINE' : 'OFFLINE'}
            </span>
          </div>
          {isConnected && can && (
            <>
              <span className="text-slate-600">|</span>
              <span className="text-slate-400 text-[11px]">{can.packets_per_sec} pkts/s</span>
              <span className="text-slate-600">|</span>
              <span className="text-slate-400 text-[11px]">{can.latency_ms} ms</span>
            </>
          )}
        </div>

        {/* Time Display */}
        <div className="flex items-center gap-1.5 px-3 py-1 rounded bg-slate-900/80 border border-slate-800 text-slate-300">
          <Clock className="w-3.5 h-3.5 text-cyan-400" />
          <span>{data?.time_str || '--:--:--'}</span>
        </div>
      </div>
    </header>
  );
};
