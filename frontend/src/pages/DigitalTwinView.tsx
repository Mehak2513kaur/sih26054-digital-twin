import React from 'react';
import { FullEngineState } from '../types/engine';
import { Cpu, ArrowRight, Gauge, Activity, AlertTriangle, Layers, Wind, Mountain, Thermometer, Zap } from 'lucide-react';

interface DigitalTwinProps {
  data: FullEngineState | null;
}

export const DigitalTwinView: React.FC<DigitalTwinProps> = ({ data }) => {
  const tel = data?.telemetry;
  const exp = data?.expected_physics;
  const res = data?.residuals;
  const health = data?.health;

  const comparisonRows = [
    {
      parameter: '1. Cylinder Head Temp (CHT)',
      unit: '°C',
      observed: tel?.engine_temp,
      expected: exp?.expected_engine_temp,
      residual: res?.residual_engine_temp,
      sigma: 2.2,
      criticalLimit: 12.0
    },
    {
      parameter: '2. Oil Temperature',
      unit: '°C',
      observed: tel?.oil_temp,
      expected: exp?.expected_oil_temp,
      residual: res?.residual_oil_temp,
      sigma: 1.8,
      criticalLimit: 10.0
    },
    {
      parameter: '3. Hydraulic Oil Pressure',
      unit: 'bar',
      observed: tel?.oil_pressure,
      expected: exp?.expected_oil_pressure,
      residual: res?.residual_oil_pressure,
      sigma: 0.12,
      criticalLimit: -0.6
    },
    {
      parameter: '4. Exhaust Gas Temp (EGT)',
      unit: '°C',
      observed: tel?.exhaust_gas_temp,
      expected: exp?.expected_exhaust_gas_temp,
      residual: res?.residual_exhaust_gas_temp,
      sigma: 8.5,
      criticalLimit: 40.0
    },
    {
      parameter: '5. Manifold Air Press (MAP)',
      unit: 'inHg',
      observed: tel?.manifold_pressure,
      expected: exp?.expected_manifold_pressure,
      residual: res?.residual_manifold_pressure,
      sigma: 0.45,
      criticalLimit: 3.5
    },
    {
      parameter: '6. Fuel Flow Rate',
      unit: 'L/h',
      observed: tel?.fuel_flow,
      expected: exp?.expected_fuel_flow,
      residual: res?.residual_fuel_flow,
      sigma: 0.65,
      criticalLimit: 4.0
    },
    {
      parameter: '7. Mechanical RMS Vibration',
      unit: 'mm/s',
      observed: tel?.vibration,
      expected: exp?.expected_vibration,
      residual: res?.residual_vibration,
      sigma: 0.18,
      criticalLimit: 2.0
    },
    {
      parameter: '8. Engine Rotational Speed (RPM)',
      unit: 'RPM',
      observed: tel?.rpm,
      expected: exp?.expected_rpm,
      residual: tel && exp ? tel.rpm - exp.expected_rpm : 0,
      sigma: 35.0,
      criticalLimit: 120.0
    }
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner: Core Digital Twin Concept */}
      <div className="glass-panel rounded-xl p-5 border-cyan-500/30">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center">
            <Cpu className="w-6 h-6 text-cyan-400" />
          </div>
          <div>
            <h2 className="text-base font-bold font-mono tracking-wide text-white uppercase flex items-center gap-2">
              <span>PHYSICAL UAV ENGINE vs FIRST-PRINCIPLES VIRTUAL TWIN</span>
              <span className="text-xs px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-normal">
                RESIDUAL DIVERGENCE ENGINE
              </span>
            </h2>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              The Digital Twin computes expected thermodynamic, aerodynamic & mechanical equilibrium in real time.
              Residual = Observed - Expected. Divergence triggers predictive prognostics hours before threshold alarms.
            </p>
          </div>
        </div>
      </div>

      {/* Environmental & Flight Operating Conditions Influencing the Twin */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
        <div className="glass-panel rounded-xl p-3.5 border-slate-800 flex items-center gap-3">
          <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
            <Mountain className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] font-mono text-slate-400 uppercase">Altitude Compensation</div>
            <div className="text-base font-bold font-mono text-white">{tel?.altitude?.toFixed(0) || 8000} ft</div>
            <div className="text-[10px] font-mono text-blue-400">Air Density Ratio: {(Math.exp(-(tel?.altitude || 8000) / 29500)).toFixed(2)}</div>
          </div>
        </div>

        <div className="glass-panel rounded-xl p-3.5 border-slate-800 flex items-center gap-3">
          <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
            <Thermometer className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] font-mono text-slate-400 uppercase">Ambient Temperature</div>
            <div className="text-base font-bold font-mono text-white">{tel?.ambient_temp?.toFixed(1) || 18.0} °C</div>
            <div className="text-[10px] font-mono text-amber-400">Cooling Influx Delta: {((tel?.engine_temp || 96.5) - (tel?.ambient_temp || 18.0)).toFixed(1)} °C</div>
          </div>
        </div>

        <div className="glass-panel rounded-xl p-3.5 border-slate-800 flex items-center gap-3">
          <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
            <Zap className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] font-mono text-slate-400 uppercase">Throttle Demand</div>
            <div className="text-base font-bold font-mono text-white">{tel?.throttle?.toFixed(1) || 65.0} %</div>
            <div className="text-[10px] font-mono text-cyan-400">Load: {tel?.engine_load?.toFixed(1) || 65.0}%</div>
          </div>
        </div>

        <div className="glass-panel rounded-xl p-3.5 border-slate-800 flex items-center gap-3">
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] font-mono text-slate-400 uppercase">Twin Alignment Status</div>
            <div className="text-base font-bold font-mono text-emerald-400">
              {res && res.composite_residual_norm > 3.0 ? 'DIVERGENT' : res && res.composite_residual_norm > 1.8 ? 'WARNING' : 'ALIGNED'}
            </div>
            <div className="text-[10px] font-mono text-slate-400">Residual Norm: {res?.composite_residual_norm?.toFixed(2) || '0.15'} σ</div>
          </div>
        </div>
      </div>

      {/* Side-by-Side 8-Parameter Telemetry Matrix */}
      <div className="glass-panel rounded-xl p-5 border-slate-800">
        <div className="text-xs font-mono uppercase font-bold text-slate-300 mb-4 tracking-wider flex items-center justify-between">
          <span>Real Engine State vs Virtual Twin State (8 Core Parameters)</span>
          <span className="text-slate-500 text-[11px]">Real-Time Z-Score Residual Analysis (σ normalized)</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="pb-2.5 font-semibold">Engine Parameter</th>
                <th className="pb-2.5 font-semibold text-right">Physical Observed</th>
                <th className="pb-2.5 font-semibold text-right">Virtual Expected</th>
                <th className="pb-2.5 font-semibold text-right">Residual Delta (Δ)</th>
                <th className="pb-2.5 font-semibold text-right">Normalized Z-Score</th>
                <th className="pb-2.5 font-semibold text-center">Twin Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {comparisonRows.map((row) => {
                const obs = row.observed ?? 0;
                const expVal = row.expected ?? 0;
                const residual = row.residual ?? (obs - expVal);
                const zScore = residual / row.sigma;
                const isCritical = Math.abs(zScore) > 3.0;
                const isWarning = Math.abs(zScore) > 1.8;

                return (
                  <tr key={row.parameter} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 text-slate-200 font-medium">
                      {row.parameter}
                    </td>
                    <td className="py-3 text-right font-bold text-white">
                      {typeof obs === 'number' ? obs.toFixed(row.unit === 'bar' || row.unit === 'inHg' || row.unit === 'mm/s' ? 2 : (row.unit === 'RPM' ? 0 : 1)) : obs} {row.unit}
                    </td>
                    <td className="py-3 text-right text-cyan-300">
                      {typeof expVal === 'number' ? expVal.toFixed(row.unit === 'bar' || row.unit === 'inHg' || row.unit === 'mm/s' ? 2 : (row.unit === 'RPM' ? 0 : 1)) : expVal} {row.unit}
                    </td>
                    <td className={`py-3 text-right font-bold ${
                      isCritical ? 'text-rose-400' : isWarning ? 'text-amber-400' : 'text-slate-300'
                    }`}>
                      {residual > 0 ? `+${residual.toFixed(2)}` : residual.toFixed(2)} {row.unit}
                    </td>
                    <td className="py-3 text-right font-mono">
                      <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                        isCritical ? 'bg-rose-500/20 text-rose-300' : isWarning ? 'bg-amber-500/20 text-amber-300' : 'bg-slate-800 text-slate-400'
                      }`}>
                        {zScore > 0 ? `+${zScore.toFixed(2)}` : zScore.toFixed(2)} σ
                      </span>
                    </td>
                    <td className="py-3 text-center">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        isCritical ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' : isWarning ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                      }`}>
                        {isCritical ? 'DIVERGENT' : isWarning ? 'WARNING' : 'ALIGNED'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
