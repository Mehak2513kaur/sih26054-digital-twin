import React from 'react';
import { FullEngineState } from '../types/engine';
import { 
  BrainCircuit, 
  AlertTriangle, 
  CheckCircle2, 
  HelpCircle, 
  ShieldAlert, 
  BarChart3, 
  Wrench, 
  Info 
} from 'lucide-react';

interface AIDiagnosticsProps {
  data: FullEngineState | null;
}

export const AIDiagnosticsView: React.FC<AIDiagnosticsProps> = ({ data }) => {
  const ml = data?.ml_prediction;
  const health = data?.health;
  const rec = data?.recommendation;
  const xai = ml?.explainability;
  const contributions = xai?.contributions || [];
  const narrative = xai?.diagnostic_narrative || [];

  const faultClasses = [
    'NORMAL',
    'OVERHEATING',
    'MISFIRE',
    'OIL_PRESSURE_FAILURE',
    'VIBRATION_ANOMALY',
    'FUEL_SYSTEM_ANOMALY',
    'SENSOR_DRIFT',
    'BEARING_DEGRADATION'
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="glass-panel rounded-xl p-5 border-cyan-500/30">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-purple-500/10 border border-purple-500/30 flex items-center justify-center">
            <BrainCircuit className="w-6 h-6 text-purple-400" />
          </div>
          <div>
            <h2 className="text-base font-bold font-mono tracking-wide text-white uppercase flex items-center gap-2">
              <span>EXPLAINABLE AI (XAI) & MULTI-CLASS FAULT CLASSIFICATION</span>
              <span className="text-xs px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 font-normal">
                RANDOM FOREST + ISOLATION FOREST
              </span>
            </h2>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Unsupervised anomaly score combined with multi-class supervised fault recognition. 
              Feature attribution shows exactly WHY an anomaly or failure prediction was triggered.
            </p>
          </div>
        </div>
      </div>

      {/* Model State Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Classified Fault Card */}
        <div className="glass-panel rounded-xl p-5 border-slate-800">
          <div className="text-[11px] font-mono text-slate-400 uppercase">Predicted Powertrain Fault</div>
          <div className="text-2xl font-bold font-mono text-white mt-2">
            <span className={ml?.predicted_fault !== 'NORMAL' ? 'text-amber-400' : 'text-emerald-400'}>
              {ml?.predicted_fault?.replace(/_/g, ' ') || 'NORMAL'}
            </span>
          </div>
          <div className="mt-3 flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400">Model Confidence:</span>
            <span className="text-emerald-400 font-bold text-sm">{ml?.confidence?.toFixed(1) || 95.0}%</span>
          </div>
          {/* Progress bar */}
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1.5">
            <div 
              className="bg-gradient-to-r from-cyan-500 to-emerald-500 h-full rounded-full transition-all duration-300"
              style={{ width: `${ml?.confidence || 95}%` }}
            />
          </div>
        </div>

        {/* Isolation Forest Anomaly Intensity */}
        <div className="glass-panel rounded-xl p-5 border-slate-800">
          <div className="text-[11px] font-mono text-slate-400 uppercase">Isolation Forest Anomaly Intensity</div>
          <div className="text-2xl font-bold font-mono text-white mt-2 flex items-baseline gap-1.5">
            <span className={ml?.is_anomaly ? 'text-rose-400 font-extrabold' : 'text-cyan-300'}>
              {ml?.anomaly_intensity?.toFixed(1) || 0.0}
            </span>
            <span className="text-xs text-slate-500 font-normal">/ 100</span>
          </div>
          <div className="mt-3 flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400">Anomaly Status:</span>
            <span className={ml?.is_anomaly ? 'text-rose-400 font-bold' : 'text-emerald-400 font-bold'}>
              {ml?.is_anomaly ? 'ANOMALY DETECTED' : 'NORMAL ENVELOPE'}
            </span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1.5">
            <div 
              className={`h-full rounded-full transition-all duration-300 ${
                ml?.is_anomaly ? 'bg-rose-500' : 'bg-cyan-500'
              }`}
              style={{ width: `${Math.min(100, ml?.anomaly_intensity || 0)}%` }}
            />
          </div>
        </div>

        {/* Composite Health Fusion Impact */}
        <div className="glass-panel rounded-xl p-5 border-slate-800">
          <div className="text-[11px] font-mono text-slate-400 uppercase">Composite Health Deduction</div>
          <div className="text-2xl font-bold font-mono text-amber-400 mt-2">
            -{(health?.penalties?.ml_penalty || 0).toFixed(1)} pts
          </div>
          <div className="mt-3 flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400">Total Health Score:</span>
            <span className="text-white font-bold text-sm">{health?.health_score?.toFixed(1) || 96.0}%</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1.5">
            <div 
              className="bg-amber-500 h-full rounded-full transition-all duration-300"
              style={{ width: `${Math.min(100, (health?.penalties?.ml_penalty || 0) / 35 * 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* WHY THIS PREDICTION? (Feature Attribution Horizontal Bar Chart) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Feature Attribution Bars */}
        <div className="glass-panel rounded-xl p-5 border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xs font-mono uppercase font-bold text-slate-300 tracking-wider flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-cyan-400" />
              <span>Feature Contribution Attribution (Ranked Factors)</span>
            </h3>
            <span className="text-[10px] font-mono text-slate-500">Normalized % Weight</span>
          </div>

          <div className="space-y-3">
            {contributions.map((c, i) => (
              <div key={c.feature} className="space-y-1">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-slate-300 font-medium">
                    {i + 1}. {c.label}
                  </span>
                  <span className="text-cyan-300 font-bold">{c.weight_pct.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden border border-slate-800">
                  <div 
                    className="bg-gradient-to-r from-cyan-600 via-cyan-400 to-blue-500 h-full rounded-full transition-all duration-500"
                    style={{ width: `${c.weight_pct}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Engineering Diagnostic Reasoning Narrative */}
        <div className="glass-panel rounded-xl p-5 border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xs font-mono uppercase font-bold text-slate-300 tracking-wider flex items-center gap-2">
                <HelpCircle className="w-4 h-4 text-purple-400" />
                <span>Why This Prediction? (Aerospace Reasoning)</span>
              </h3>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-purple-500/10 text-purple-300 border border-purple-500/30">
                AI ROOT CAUSE
              </span>
            </div>

            <div className="space-y-2.5">
              {narrative.map((item, idx) => (
                <div 
                  key={idx}
                  className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs font-mono text-slate-300 flex items-start gap-2.5"
                >
                  <span className="text-cyan-400 font-bold mt-0.5">•</span>
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Root-cause conclusion summary */}
          <div className="mt-4 pt-3 border-t border-slate-800/80 text-xs font-mono">
            <span className="text-slate-500">Diagnostic Verdict: </span>
            <span className="text-amber-400 font-bold">
              {xai?.root_cause_summary || 'Powertrain operating normally.'}
            </span>
          </div>
        </div>
      </div>

      {/* Recommended Action Directive */}
      {rec && (
        <div className="glass-panel rounded-xl p-5 border-amber-500/30 bg-amber-950/10">
          <div className="flex items-start gap-3">
            <div className="w-9 h-9 rounded-lg bg-amber-500/20 border border-amber-500/40 flex items-center justify-center shrink-0 mt-0.5">
              <Wrench className="w-5 h-5 text-amber-400" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider bg-amber-500/20 text-amber-400 border border-amber-500/40">
                  {rec.urgency} ACTION REQUIRED
                </span>
                <h4 className="text-sm font-bold font-mono text-white">{rec.title}</h4>
              </div>
              <p className="text-xs font-mono text-slate-300 mt-2 leading-relaxed">
                {rec.recommended_action}
              </p>
              <div className="text-[10px] font-mono text-slate-500 mt-2">
                {rec.disclaimer}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
