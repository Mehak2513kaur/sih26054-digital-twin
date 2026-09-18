import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface SensorCardProps {
  label: string;
  value: number | string;
  unit: string;
  expected?: number;
  residual?: number;
  rate?: number;
  rateUnit?: string;
  minRange?: number;
  maxRange?: number;
  status?: 'NORMAL' | 'WARNING' | 'CRITICAL';
}

export const SensorCard: React.FC<SensorCardProps> = ({
  label,
  value,
  unit,
  expected,
  residual,
  rate,
  rateUnit = '/min',
  minRange,
  maxRange,
  status = 'NORMAL'
}) => {
  const numVal = typeof value === 'number' ? value : parseFloat(value) || 0;
  
  // Color styling based on status
  let borderColor = 'border-slate-800';
  let badgeColor = 'text-emerald-400';
  if (status === 'WARNING') {
    borderColor = 'border-amber-500/50 bg-amber-950/20';
    badgeColor = 'text-amber-400';
  } else if (status === 'CRITICAL') {
    borderColor = 'border-rose-500/60 bg-rose-950/30';
    badgeColor = 'text-rose-400';
  }

  // Trend direction
  const rateNum = rate ?? 0;
  const isUp = rateNum > 0.1;
  const isDown = rateNum < -0.1;

  return (
    <div className={`glass-panel rounded-xl p-3.5 border ${borderColor} transition-all hover:border-cyan-500/40 relative overflow-hidden group`}>
      <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 mb-1">
        <span className="truncate pr-2 font-medium">{label}</span>
        {rate !== undefined && (
          <div className="flex items-center gap-0.5 text-[10px]">
            {isUp ? (
              <TrendingUp className="w-3 h-3 text-rose-400" />
            ) : isDown ? (
              <TrendingDown className="w-3 h-3 text-cyan-400" />
            ) : (
              <Minus className="w-3 h-3 text-slate-500" />
            )}
            <span className={isUp ? 'text-rose-400' : isDown ? 'text-cyan-400' : 'text-slate-500'}>
              {rate > 0 ? `+${rate.toFixed(1)}` : rate.toFixed(1)}{rateUnit}
            </span>
          </div>
        )}
      </div>

      {/* Main Value Display */}
      <div className="flex items-baseline gap-1.5 my-1">
        <span className="text-2xl font-bold font-mono text-white tracking-tight">
          {typeof value === 'number' ? value.toFixed(unit === 'bar' || unit === 'inHg' || unit === 'mm/s' ? 2 : 1) : value}
        </span>
        <span className="text-xs font-mono text-slate-400">{unit}</span>
      </div>

      {/* Expected & Residual footer (Digital Twin view) */}
      {expected !== undefined && residual !== undefined && (
        <div className="mt-2 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] font-mono text-slate-400">
          <div>
            Exp: <span className="text-slate-300">{expected.toFixed(1)}</span>
          </div>
          <div className={Math.abs(residual) > 4 ? 'text-rose-400 font-bold' : 'text-cyan-300'}>
            Res: {residual > 0 ? `+${residual.toFixed(1)}` : residual.toFixed(1)}
          </div>
        </div>
      )}
    </div>
  );
};
