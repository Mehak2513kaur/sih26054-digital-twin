import React from 'react';
import { HealthState } from '../types/engine';
import { ShieldCheck, AlertTriangle, AlertOctagon } from 'lucide-react';

interface HealthGaugeProps {
  health: HealthState | undefined;
  engineHours: number;
}

export const HealthGauge: React.FC<HealthGaugeProps> = ({ health, engineHours }) => {
  const score = health?.health_score ?? 96.0;
  const status = health?.status ?? 'HEALTHY';
  
  // Circumference calculation for radius 58
  const radius = 58;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  let strokeColor = '#10b981'; // Emerald
  let badgeBg = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
  let Icon = ShieldCheck;

  if (status === 'DEGRADING') {
    strokeColor = '#f59e0b'; // Amber
    badgeBg = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    Icon = AlertTriangle;
  } else if (status === 'CRITICAL') {
    strokeColor = '#ef4444'; // Rose
    badgeBg = 'bg-rose-500/10 text-rose-400 border-rose-500/30';
    Icon = AlertOctagon;
  }

  return (
    <div className="glass-panel rounded-xl p-5 flex flex-col items-center justify-center relative overflow-hidden">
      <div className="text-[11px] font-mono tracking-wider text-slate-400 uppercase mb-2 flex items-center gap-1.5">
        <Icon className="w-3.5 h-3.5" style={{ color: strokeColor }} />
        <span>ENGINE HEALTH COMPOSITE</span>
      </div>

      {/* Circular Gauge */}
      <div className="relative w-36 h-36 flex items-center justify-center">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 140 140">
          {/* Background circle */}
          <circle
            cx="70"
            cy="70"
            r={radius}
            stroke="#1e293b"
            strokeWidth="10"
            fill="transparent"
          />
          {/* Progress circle */}
          <circle
            cx="70"
            cy="70"
            r={radius}
            stroke={strokeColor}
            strokeWidth="10"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-500 ease-out"
          />
        </svg>

        {/* Center Score Text */}
        <div className="absolute flex flex-col items-center justify-center text-center">
          <span className="text-3xl font-extrabold font-mono tracking-tight text-white">
            {score.toFixed(1)}%
          </span>
          <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-wider uppercase border mt-1 ${badgeBg}`}>
            {status}
          </span>
        </div>
      </div>

      {/* Engine Hours & Degradation stats */}
      <div className="w-full mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono">
        <div className="text-slate-400">
          Engine Hours: <span className="text-slate-200 font-bold">{engineHours?.toFixed(1)} h</span>
        </div>
        <div className="text-slate-400">
          Target: <span className="text-cyan-400">500 h TBO</span>
        </div>
      </div>
    </div>
  );
};
