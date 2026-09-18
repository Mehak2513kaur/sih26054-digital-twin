import React, { useState, useEffect } from 'react';
import { FullEngineState } from '../types/engine';
import { fetchReportJson, getReportPdfUrl } from '../services/api';
import { 
  FileText, 
  Download, 
  CheckCircle2, 
  AlertTriangle, 
  Printer, 
  ShieldCheck, 
  Wrench, 
  Cpu 
} from 'lucide-react';

interface HealthReportProps {
  data: FullEngineState | null;
}

export const HealthReportView: React.FC<HealthReportProps> = ({ data }) => {
  const missionId = data?.mission?.mission_id || 'MISSION-042';
  const [reportData, setReportData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadReport();
  }, [missionId]);

  const loadReport = async () => {
    setLoading(true);
    try {
      const res = await fetchReportJson(missionId);
      setReportData(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPdf = () => {
    const url = getReportPdfUrl(missionId);
    window.open(url, '_blank');
  };

  const r = reportData || {};

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Top Banner & Export Button */}
      <div className="glass-panel rounded-xl p-5 border-cyan-500/30 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center">
            <FileText className="w-6 h-6 text-cyan-400" />
          </div>
          <div>
            <h2 className="text-base font-bold font-mono tracking-wide text-white uppercase flex items-center gap-2">
              <span>MISSION HEALTH DEBRIEF REPORT</span>
              <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-cyan-300 font-normal">
                DRDO PS 26054
              </span>
            </h2>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Automated post-flight engineering debrief with telemetry excursions, AI diagnostic findings, 
              and defense maintenance work order directives.
            </p>
          </div>
        </div>

        <button
          onClick={handleDownloadPdf}
          className="px-4 py-2.5 rounded bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-mono text-xs font-bold tracking-wide flex items-center gap-2 shadow-lg shadow-cyan-600/30 transition-all self-start sm:self-center"
        >
          <Download className="w-4 h-4" />
          <span>EXPORT PDF REPORT</span>
        </button>
      </div>

      {/* Report Document Sheet (Military / Aerospace Styling) */}
      <div className="bg-[#0b1220] border border-slate-700/80 rounded-xl p-8 shadow-2xl font-mono text-slate-300 space-y-6">
        {/* Document Header */}
        <div className="border-b border-slate-700/80 pb-6 flex flex-col sm:flex-row justify-between gap-4">
          <div>
            <div className="text-xs text-cyan-400 font-bold uppercase tracking-widest">
              DEFENCE RESEARCH & DEVELOPMENT ORGANISATION (DRDO)
            </div>
            <h1 className="text-xl font-extrabold text-white mt-1">
              MALE UAV POWERTRAIN HEALTH DEBRIEF
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Document Ref: DRDO-26054-DT-{missionId} — CLASSIFICATION: SIMULATED UNCLASSIFIED
            </p>
          </div>
          <div className="text-left sm:text-right text-xs text-slate-400 space-y-1">
            <div>Date: <span className="text-slate-200">{r.date || new Date().toISOString().replace('T', ' ').substring(0, 19)}</span></div>
            <div>Powertrain: <span className="text-cyan-300 font-bold">{r.engine_id || 'UAV-PX-01'}</span></div>
            <div>Cumulative Hours: <span className="text-slate-200">{r.engine_hours || 1247.4} h</span></div>
          </div>
        </div>

        {/* Section 1: Executive Summary */}
        <div className="space-y-3">
          <h3 className="text-xs uppercase font-bold text-cyan-400 tracking-wider flex items-center gap-1.5">
            <span>1. EXECUTIVE SORTIE SUMMARY</span>
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 rounded-lg bg-slate-900/80 border border-slate-800 text-xs">
            <div>
              <span className="text-slate-500">Flight Profile:</span>
              <div className="text-white font-bold mt-0.5">{r.scenario || 'Normal Cruise'}</div>
            </div>
            <div>
              <span className="text-slate-500">Duration:</span>
              <div className="text-white font-bold mt-0.5">{r.duration_seconds || 0} seconds</div>
            </div>
            <div>
              <span className="text-slate-500">Final Health Score:</span>
              <div className={`text-base font-bold mt-0.5 ${
                (r.final_health_score || 96) >= 80 ? 'text-emerald-400' : 'text-amber-400'
              }`}>
                {(r.final_health_score || 96).toFixed(1)}%
              </div>
            </div>
            <div>
              <span className="text-slate-500">Projected RUL:</span>
              <div className="text-cyan-300 font-bold text-base mt-0.5">
                {(r.final_rul_hours || 480).toFixed(1)} hours
              </div>
            </div>
          </div>
        </div>

        {/* Section 2: Peak Stress Excursions */}
        <div className="space-y-3">
          <h3 className="text-xs uppercase font-bold text-cyan-400 tracking-wider">
            2. POWERTRAIN STRESS & PEAK EXCURSIONS
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 text-xs">
              <span className="text-slate-500">Peak Cylinder Head Temp (CHT):</span>
              <div className="text-xl font-bold text-white mt-1">
                {(r.peak_temperature || 96.5).toFixed(1)} °C
              </div>
              <div className="text-[11px] text-slate-500 mt-1">Maximum continuous limit: 125 °C</div>
            </div>
            <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 text-xs">
              <span className="text-slate-500">Maximum RMS Vibration:</span>
              <div className="text-xl font-bold text-white mt-1">
                {(r.max_vibration || 1.65).toFixed(2)} mm/s
              </div>
              <div className="text-[11px] text-slate-500 mt-1">Alert trip threshold: 4.5 mm/s</div>
            </div>
            <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 text-xs">
              <span className="text-slate-500">Minimum Oil Pressure:</span>
              <div className="text-xl font-bold text-white mt-1">
                {(r.min_oil_pressure || 4.1).toFixed(2)} bar
              </div>
              <div className="text-[11px] text-slate-500 mt-1">Low pressure warning: 2.5 bar</div>
            </div>
          </div>
        </div>

        {/* Section 3: AI Diagnostic Findings & Residuals */}
        <div className="space-y-3">
          <h3 className="text-xs uppercase font-bold text-cyan-400 tracking-wider">
            3. ARTIFICIAL INTELLIGENCE & DIGITAL TWIN FINDINGS
          </h3>
          <div className="p-4 rounded-lg bg-slate-900/80 border border-slate-800 space-y-2 text-xs">
            {r.ai_findings && r.ai_findings.length > 0 ? (
              r.ai_findings.map((f: string, i: number) => (
                <div key={i} className="flex items-start gap-2">
                  <span className="text-cyan-400 font-bold">•</span>
                  <span>{f}</span>
                </div>
              ))
            ) : (
              <div className="text-slate-400">All primary thermodynamic and mechanical sensors remained nominal.</div>
            )}
          </div>
        </div>

        {/* Section 4: Maintenance Directive */}
        <div className="space-y-3">
          <h3 className="text-xs uppercase font-bold text-cyan-400 tracking-wider">
            4. DEFENSE MAINTENANCE ACTION DIRECTIVE
          </h3>
          <div className="p-4 rounded-lg bg-slate-900/80 border border-amber-500/30 text-xs space-y-1.5">
            <div className="text-amber-400 font-bold">Recommended Engineering Protocol:</div>
            <p className="text-slate-200 leading-relaxed">
              {r.recommended_maintenance || 'Nominal post-flight borescope and oil particulate check.'}
            </p>
          </div>
        </div>

        {/* Footer Disclaimer */}
        <div className="pt-6 border-t border-slate-800 text-[10px] text-slate-500 flex flex-col sm:flex-row justify-between gap-2">
          <span>NOTICE: {r.disclaimer || 'Generated in SIMULATION MODE for DRDO PS 26054 prototype demonstration.'}</span>
          <span>SYSTEM TIME: {new Date().toUTCString()}</span>
        </div>
      </div>
    </div>
  );
};
