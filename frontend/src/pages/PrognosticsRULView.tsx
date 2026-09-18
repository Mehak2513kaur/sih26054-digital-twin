import React from 'react';
import { FullEngineState, HistoricalPoint } from '../types/engine';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  ReferenceLine 
} from 'recharts';
import { Hourglass, TrendingDown, ShieldAlert, CheckCircle, AlertTriangle } from 'lucide-react';

interface PrognosticsProps {
  data: FullEngineState | null;
  history: HistoricalPoint[];
}

export const PrognosticsRULView: React.FC<PrognosticsProps> = ({ data, history }) => {
  const ml = data?.ml_prediction;
  const rul = ml?.rul;
  const currentRUL = rul?.rul_hours || 480.0;
  const initialRUL = rul?.initial_rul || 480.0;
  const degRate = rul?.degradation_rate_pct || 0.2;
  const degIndex = rul?.degradation_index || 8.5;
  const degVelocity = rul?.degradation_velocity || 0.20;
  const confInterval = rul?.confidence_interval || { lower: 440, upper: 500 };
  const wear = rul?.component_wear_pct;
  const rulLabel = rul?.label || 'PROTOTYPE / SIMULATED RUL ESTIMATE';

  // Synthesize degradation projection curve (past 40 points + next 60 points projected)
  const pastPoints = history.slice(-40).map((pt) => ({
    time: pt.time,
    historical_rul: pt.rul_hours,
    projected_rul: pt.rul_hours,
  }));

  // Future projection
  const futurePoints: { time: string; historical_rul: number | null; projected_rul: number }[] = [];
  const lastTime = pastPoints.length > 0 ? pastPoints[pastPoints.length - 1].historical_rul : currentRUL;
  for (let i = 1; i <= 30; i++) {
    const projected = Math.max(15.0, lastTime - (degRate * i * 1.5));
    futurePoints.push({
      time: `+${i * 2}m`,
      historical_rul: null,
      projected_rul: projected,
    });
  }

  const projectionData = [...pastPoints, ...futurePoints];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="glass-panel rounded-xl p-5 border-cyan-500/30">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center">
            <Hourglass className="w-6 h-6 text-cyan-400" />
          </div>
          <div className="flex-1">
            <h2 className="text-base font-bold font-mono tracking-wide text-white uppercase flex items-center gap-2">
              <span>PROGNOSTIC REMAINING USEFUL LIFE (RUL) ESTIMATION</span>
              <span className="text-xs px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-normal border border-amber-500/30">
                {rulLabel}
              </span>
            </h2>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Continuously computes fatigue damage accumulation and residual acceleration factors 
              to forecast remaining operating hours before maintenance overhaul (TBO).
            </p>
          </div>
        </div>
      </div>

      {/* Hero Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="glass-panel rounded-xl p-5 border-slate-800">
          <div className="text-[11px] font-mono text-slate-400 uppercase">Current Estimated RUL</div>
          <div className="flex items-baseline gap-2 mt-1.5">
            <span className="text-3xl font-extrabold font-mono text-white tracking-tight">
              {currentRUL.toFixed(1)}
            </span>
            <span className="text-sm font-mono text-cyan-400 font-bold">HOURS</span>
          </div>
          <div className="text-[10px] font-mono text-slate-500 mt-1">
            Initial baseline: {initialRUL.toFixed(0)} h TBO
          </div>
        </div>

        <div className="glass-panel rounded-xl p-5 border-slate-800">
          <div className="text-[11px] font-mono text-slate-400 uppercase">Degradation Index</div>
          <div className="text-2xl font-bold font-mono text-white mt-1.5 flex items-baseline gap-1.5">
            <span className={degIndex > 40 ? 'text-rose-400' : degIndex > 20 ? 'text-amber-400' : 'text-cyan-300'}>
              {degIndex.toFixed(1)}
            </span>
            <span className="text-xs text-slate-500 font-normal">/ 100</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-2">
            <div 
              className={`h-full rounded-full transition-all duration-300 ${
                degIndex > 40 ? 'bg-rose-500' : degIndex > 20 ? 'bg-amber-500' : 'bg-cyan-500'
              }`}
              style={{ width: `${Math.min(100, degIndex)}%` }}
            />
          </div>
        </div>

        <div className="glass-panel rounded-xl p-5 border-slate-800">
          <div className="text-[11px] font-mono text-slate-400 uppercase">Degradation Velocity</div>
          <div className="text-2xl font-bold font-mono text-rose-400 mt-1.5 flex items-center gap-1.5">
            <TrendingDown className="w-5 h-5" />
            <span>+{degVelocity.toFixed(2)}%/hr</span>
          </div>
          <div className="text-[10px] font-mono text-slate-500 mt-1">
            Normal burn rate: 0.20%/hr
          </div>
        </div>

        <div className="glass-panel rounded-xl p-5 border-slate-800">
          <div className="text-[11px] font-mono text-slate-400 uppercase">95% Confidence Bounds</div>
          <div className="text-2xl font-bold font-mono text-white mt-1.5">
            [{confInterval.lower.toFixed(0)}h - {confInterval.upper.toFixed(0)}h]
          </div>
          <div className="text-[10px] font-mono text-emerald-400 mt-1">
            Model Confidence: {rul?.confidence_pct || 94}%
          </div>
        </div>

        <div className="glass-panel rounded-xl p-5 border-slate-800">
          <div className="text-[11px] font-mono text-slate-400 uppercase">Stress Multiplier</div>
          <div className="text-2xl font-bold font-mono text-cyan-300 mt-1.5">
            {(1.0 + (degIndex / 100.0) * 2.5).toFixed(2)}x
          </div>
          <div className="text-[10px] font-mono text-slate-500 mt-1">
            Healthy baseline: 1.00x
          </div>
        </div>
      </div>

      {/* Degradation Curve Projection Chart */}
      <div className="glass-panel rounded-xl p-5 border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <h3 className="text-xs font-mono uppercase font-bold text-slate-300 tracking-wider">
              RUL Degradation Trajectory & Overhaul Forecast
            </h3>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">
              SIMULATED / PROTOTYPE ESTIMATE
            </span>
          </div>
          <div className="text-xs font-mono text-slate-400 flex items-center gap-3">
            <span className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
              Observed RUL
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-400" />
              Projected Decay
            </span>
          </div>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={projectionData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.6} />
              <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 10, fontFamily: 'monospace' }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 10, fontFamily: 'monospace' }} domain={[0, 500]} />
              <Tooltip 
                contentStyle={{
                  backgroundColor: '#0f172a',
                  border: '1px solid #1e293b',
                  borderRadius: '8px',
                  fontSize: '11px',
                  fontFamily: 'monospace'
                }}
              />
              <ReferenceLine y={100} stroke="#ef4444" strokeDasharray="4 4" label={{ value: 'CRITICAL LIMIT (100h)', fill: '#ef4444', fontSize: 10 }} />
              <ReferenceLine y={250} stroke="#f59e0b" strokeDasharray="4 4" label={{ value: 'WARNING LIMIT (250h)', fill: '#f59e0b', fontSize: 10 }} />
              <Line type="monotone" dataKey="historical_rul" stroke="#06b6d4" strokeWidth={2.5} dot={false} connectNulls={false} />
              <Line type="monotone" dataKey="projected_rul" stroke="#f43f5e" strokeWidth={2} strokeDasharray="5 5" dot={false} connectNulls={true} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Subsystem Component Wear Breakdown */}
      <div className="glass-panel rounded-xl p-5 border-slate-800">
        <h3 className="text-xs font-mono uppercase font-bold text-slate-300 tracking-wider mb-4">
          Subsystem Wear & Fatigue Accumulation
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { name: 'Thermal Barrier & Cylinder Head', wear: wear?.thermal_barrier || 37.0, color: 'from-rose-500 to-amber-500' },
            { name: 'Crankshaft & Connecting Rod Bearings', wear: wear?.crank_bearings || 32.0, color: 'from-amber-500 to-cyan-500' },
            { name: 'Hydraulic Lubrication Circuit', wear: wear?.lubrication_system || 28.0, color: 'from-blue-500 to-cyan-500' },
            { name: 'Fuel Injection Manifold & Nozzles', wear: wear?.fuel_injection || 25.0, color: 'from-emerald-500 to-cyan-500' },
          ].map((item) => (
            <div key={item.name} className="p-4 rounded-lg bg-slate-900/90 border border-slate-800">
              <div className="flex items-center justify-between text-xs font-mono mb-2">
                <span className="text-slate-300 font-medium truncate pr-2">{item.name}</span>
                <span className="text-cyan-300 font-bold">{item.wear.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div 
                  className={`bg-gradient-to-r ${item.color} h-full rounded-full transition-all duration-300`}
                  style={{ width: `${item.wear}%` }}
                />
              </div>
              <div className="text-[10px] font-mono text-slate-500 mt-2 flex justify-between">
                <span>Status:</span>
                <span className={item.wear > 60 ? 'text-amber-400' : 'text-emerald-400 font-medium'}>
                  {item.wear > 60 ? 'ELEVATED WEAR' : 'NOMINAL WEAR'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
