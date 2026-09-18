import React, { useState } from 'react';
import { FullEngineState } from '../types/engine';
import { 
  startMission, 
  pauseMission, 
  resumeMission, 
  stopMission, 
  resetMission, 
  injectFault, 
  clearFault 
} from '../services/api';
import { 
  Play, 
  Pause, 
  Square, 
  RotateCcw, 
  Sliders, 
  AlertTriangle, 
  CheckCircle2, 
  Flame, 
  Activity, 
  Wind, 
  Sun, 
  Clock 
} from 'lucide-react';

interface MissionControlProps {
  data: FullEngineState | null;
}

export const MissionControlView: React.FC<MissionControlProps> = ({ data }) => {
  const mission = data?.mission;
  const faultInfo = data?.fault_injection;

  const [scenario, setScenario] = useState('NORMAL_MISSION');
  const [altitude, setAltitude] = useState(8000);
  const [ambientTemp, setAmbientTemp] = useState(18);
  const [throttle, setThrottle] = useState(65);

  const [selectedFault, setSelectedFault] = useState('OVERHEATING');
  const [faultSeverity, setFaultSeverity] = useState<'LOW' | 'MEDIUM' | 'HIGH'>('MEDIUM');
  const [rampDuration, setRampDuration] = useState(20);
  const [actionFeedback, setActionFeedback] = useState<string | null>(null);

  const showFeedback = (msg: string) => {
    setActionFeedback(msg);
    setTimeout(() => setActionFeedback(null), 3500);
  };

  const handleStart = async () => {
    await startMission(scenario, altitude, ambientTemp, throttle);
    showFeedback(`Started ${scenario} profile`);
  };

  const handlePause = async () => {
    await pauseMission();
    showFeedback('Mission paused');
  };

  const handleResume = async () => {
    await resumeMission();
    showFeedback('Mission resumed');
  };

  const handleStop = async () => {
    await stopMission();
    showFeedback('Mission stopped & saved to database');
  };

  const handleReset = async () => {
    await resetMission();
    showFeedback('Mission reset to idle');
  };

  const handleInjectFault = async () => {
    await injectFault(selectedFault, faultSeverity, rampDuration);
    showFeedback(`Injected ${selectedFault} (${faultSeverity})`);
  };

  const handleClearFault = async () => {
    await clearFault();
    showFeedback('Cleared active faults');
  };

  const scenariosList = [
    { id: 'NORMAL_MISSION', name: 'Normal Patrol Cruise', icon: Activity, desc: 'Nominal cruise at 8,000 ft, 65% throttle, 18°C ambient.' },
    { id: 'HIGH_ALTITUDE', name: 'High Altitude Climax', icon: Wind, desc: 'Climb profile to 22,000 ft testing turbocharger and thin-air cooling.' },
    { id: 'HOT_WEATHER', name: 'Hot Desert Recon', icon: Sun, desc: 'Hot 45°C ambient conditions stressing engine thermal cooling envelope.' },
    { id: 'LONG_ENDURANCE', name: 'Long Endurance Loiter', icon: Clock, desc: '14-hour extended loiter tracking continuous thermal soak.' },
    { id: 'RAPID_LOAD_CHANGE', name: 'Rapid Tactical Maneuver', icon: Sliders, desc: 'Fast throttle cycling (35% <-> 92%) testing thermal load transient.' }
  ];

  const faultTypes = [
    { id: 'OVERHEATING', name: 'Cooling System Overheating', desc: 'Gradual coolant loss; CHT and oil temp climb steadily.' },
    { id: 'MISFIRE', name: 'Cylinder Combustion Misfire', desc: 'Periodic torque drop, high vibration harmonic, and unburnt fuel in EGT.' },
    { id: 'OIL_PRESSURE_FAILURE', name: 'Oil Pressure Degradation', desc: 'Pump cavitation / leak; pressure decays dangerously below 2.0 bar.' },
    { id: 'VIBRATION_ANOMALY', name: 'Excessive Vibration (Imbalance)', desc: 'Propeller/crankshaft imbalance spike > 6.0 mm/s.' },
    { id: 'FUEL_SYSTEM_ANOMALY', name: 'Fuel Delivery Restriction', desc: 'Filter restriction; lean condition causes EGT to spike.' },
    { id: 'SENSOR_DRIFT', name: 'Sensor Calibration Drift', desc: 'Transducer offset; CHT reads artificially high without coupling.' },
    { id: 'BEARING_DEGRADATION', name: 'Crank Bearing Spalling', desc: 'High frequency vibration rise and friction heat.' }
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="glass-panel rounded-xl p-5 border-cyan-500/30">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-blue-500/10 border border-blue-500/30 flex items-center justify-center">
            <Sliders className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <h2 className="text-base font-bold font-mono tracking-wide text-white uppercase flex items-center gap-2">
              <span>MISSION CONTROL & FAULT INJECTION LABORATORY</span>
              <span className="text-xs px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 font-normal">
                HARDWARE-IN-THE-LOOP (HIL) SIMULATION
              </span>
            </h2>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Launch operational mission flight scenarios and inject progressive fault degradation models 
              to evaluate AI anomaly detection and early warning prognostics.
            </p>
          </div>
        </div>
      </div>

      {actionFeedback && (
        <div className="p-3 rounded-lg bg-cyan-950/80 border border-cyan-500/50 text-cyan-200 text-xs font-mono flex items-center gap-2 animate-fadeIn">
          <CheckCircle2 className="w-4 h-4 text-cyan-400" />
          <span>{actionFeedback}</span>
        </div>
      )}

      {/* Two Column Grid: Left = Mission Control, Right = Fault Injection */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Mission Control Panel */}
        <div className="glass-panel rounded-xl p-5 border-slate-800 space-y-5">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-mono uppercase font-bold text-slate-200 tracking-wider">
              1. Flight Mission Lifecycle
            </h3>
            <span className={`px-2.5 py-0.5 rounded text-[10px] font-mono font-bold uppercase border ${
              mission?.state === 'RUNNING' 
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 animate-pulse' 
                : mission?.state === 'PAUSED'
                ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                : 'bg-slate-800 text-slate-400 border-slate-700'
            }`}>
              STATE: {mission?.state || 'IDLE'}
            </span>
          </div>

          {/* Scenario Selectors */}
          <div className="space-y-2">
            <label className="text-[11px] font-mono text-slate-400">Select Mission Scenario:</label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {scenariosList.map((sc) => {
                const Icon = sc.icon;
                const isSelected = scenario === sc.id;
                return (
                  <button
                    key={sc.id}
                    onClick={() => setScenario(sc.id)}
                    className={`p-3 rounded-lg text-left transition-all border ${
                      isSelected
                        ? 'bg-cyan-500/15 border-cyan-500/50 text-white'
                        : 'bg-slate-900/80 border-slate-800 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <div className="flex items-center gap-2 text-xs font-bold font-mono">
                      <Icon className={`w-3.5 h-3.5 ${isSelected ? 'text-cyan-400' : 'text-slate-500'}`} />
                      <span>{sc.name}</span>
                    </div>
                    <p className="text-[10px] text-slate-500 mt-1 font-sans line-clamp-2">{sc.desc}</p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Environmental Setpoints */}
          <div className="space-y-3 pt-2 border-t border-slate-800/80">
            <div className="text-xs font-mono text-slate-400 font-semibold">Environment & Throttle Overrides:</div>
            
            <div className="space-y-1">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-400">Flight Altitude:</span>
                <span className="text-white font-bold">{altitude} ft</span>
              </div>
              <input
                type="range"
                min="1000"
                max="25000"
                step="500"
                value={altitude}
                onChange={(e) => setAltitude(Number(e.target.value))}
                className="w-full accent-cyan-400 h-1 bg-slate-800 rounded"
              />
            </div>

            <div className="space-y-1">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-400">Ambient Temperature:</span>
                <span className="text-white font-bold">{ambientTemp} °C</span>
              </div>
              <input
                type="range"
                min="-20"
                max="50"
                step="1"
                value={ambientTemp}
                onChange={(e) => setAmbientTemp(Number(e.target.value))}
                className="w-full accent-cyan-400 h-1 bg-slate-800 rounded"
              />
            </div>

            <div className="space-y-1">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-400">Throttle Position:</span>
                <span className="text-white font-bold">{throttle} %</span>
              </div>
              <input
                type="range"
                min="20"
                max="100"
                step="5"
                value={throttle}
                onChange={(e) => setThrottle(Number(e.target.value))}
                className="w-full accent-cyan-400 h-1 bg-slate-800 rounded"
              />
            </div>
          </div>

          {/* Mission Buttons */}
          <div className="pt-3 border-t border-slate-800/80 grid grid-cols-2 sm:grid-cols-4 gap-2">
            <button
              onClick={handleStart}
              className="py-2 px-3 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-mono text-xs font-bold flex items-center justify-center gap-1.5 transition-all shadow-md shadow-emerald-600/20"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>START</span>
            </button>

            {mission?.state === 'RUNNING' ? (
              <button
                onClick={handlePause}
                className="py-2 px-3 rounded bg-amber-600 hover:bg-amber-500 text-white font-mono text-xs font-bold flex items-center justify-center gap-1.5 transition-all shadow-md shadow-amber-600/20"
              >
                <Pause className="w-3.5 h-3.5 fill-current" />
                <span>PAUSE</span>
              </button>
            ) : (
              <button
                onClick={handleResume}
                className="py-2 px-3 rounded bg-blue-600 hover:bg-blue-500 text-white font-mono text-xs font-bold flex items-center justify-center gap-1.5 transition-all shadow-md shadow-blue-600/20"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>RESUME</span>
              </button>
            )}

            <button
              onClick={handleStop}
              className="py-2 px-3 rounded bg-rose-700 hover:bg-rose-600 text-white font-mono text-xs font-bold flex items-center justify-center gap-1.5 transition-all shadow-md shadow-rose-700/20"
            >
              <Square className="w-3.5 h-3.5 fill-current" />
              <span>STOP</span>
            </button>

            <button
              onClick={handleReset}
              className="py-2 px-3 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 font-mono text-xs font-bold flex items-center justify-center gap-1.5 transition-all border border-slate-700"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>RESET</span>
            </button>
          </div>
        </div>

        {/* Fault Injection Panel */}
        <div className="glass-panel rounded-xl p-5 border-slate-800 space-y-5">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-mono uppercase font-bold text-slate-200 tracking-wider flex items-center gap-2">
              <Flame className="w-4 h-4 text-rose-500" />
              <span>2. Powertrain Fault Injection Matrix</span>
            </h3>
            <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase border ${
              faultInfo?.active_fault !== 'NORMAL'
                ? 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                : 'bg-slate-800 text-slate-500 border-slate-700'
            }`}>
              ACTIVE: {faultInfo?.active_fault || 'NONE'}
            </span>
          </div>

          {/* Fault Dropdown List */}
          <div className="space-y-2">
            <label className="text-[11px] font-mono text-slate-400">Target Aerospace Fault Model:</label>
            <div className="space-y-1.5 max-h-56 overflow-y-auto pr-1">
              {faultTypes.map((f) => {
                const isSelected = selectedFault === f.id;
                return (
                  <button
                    key={f.id}
                    onClick={() => setSelectedFault(f.id)}
                    className={`w-full p-2.5 rounded-lg text-left transition-all border ${
                      isSelected
                        ? 'bg-rose-500/15 border-rose-500/50 text-white'
                        : 'bg-slate-900/80 border-slate-800 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <div className="text-xs font-bold font-mono text-slate-200">{f.name}</div>
                    <p className="text-[10px] text-slate-500 mt-0.5">{f.desc}</p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Severity & Duration */}
          <div className="space-y-3 pt-2 border-t border-slate-800/80">
            <div>
              <label className="text-[11px] font-mono text-slate-400">Fault Severity Envelope:</label>
              <div className="grid grid-cols-3 gap-2 mt-1">
                {(['LOW', 'MEDIUM', 'HIGH'] as const).map((sev) => (
                  <button
                    key={sev}
                    onClick={() => setFaultSeverity(sev)}
                    className={`py-1.5 rounded text-xs font-mono font-bold border transition-all ${
                      faultSeverity === sev
                        ? 'bg-rose-500/20 text-rose-300 border-rose-500/50 shadow-sm'
                        : 'bg-slate-900 border-slate-800 text-slate-500 hover:text-slate-300'
                    }`}
                  >
                    {sev}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-1">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-400">Gradual Progression Duration:</span>
                <span className="text-white font-bold">{rampDuration} s</span>
              </div>
              <input
                type="range"
                min="5"
                max="45"
                step="5"
                value={rampDuration}
                onChange={(e) => setRampDuration(Number(e.target.value))}
                className="w-full accent-rose-500 h-1 bg-slate-800 rounded"
              />
              <p className="text-[10px] font-mono text-slate-500">
                Gradual ramp demonstrates AI early detection prior to catastrophic threshold trip.
              </p>
            </div>
          </div>

          {/* Active Fault Progress Bar */}
          {faultInfo && faultInfo.active_fault !== 'NORMAL' && (
            <div className="p-3 rounded-lg bg-rose-950/20 border border-rose-500/30 space-y-1.5">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-rose-400 font-bold">Ramp Progression:</span>
                <span className="text-white font-bold">{faultInfo.ramp_progress.toFixed(0)}%</span>
              </div>
              <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden border border-slate-800">
                <div 
                  className="bg-gradient-to-r from-amber-500 to-rose-500 h-full rounded-full transition-all duration-300"
                  style={{ width: `${faultInfo.ramp_progress}%` }}
                />
              </div>
            </div>
          )}

          {/* Fault Buttons */}
          <div className="pt-2 border-t border-slate-800/80 flex gap-3">
            <button
              onClick={handleInjectFault}
              className="flex-1 py-2 px-4 rounded bg-rose-600 hover:bg-rose-500 text-white font-mono text-xs font-bold tracking-wide uppercase flex items-center justify-center gap-2 shadow-md shadow-rose-600/30 transition-all"
            >
              <Flame className="w-4 h-4" />
              <span>INJECT FAULT</span>
            </button>
            <button
              onClick={handleClearFault}
              className="py-2 px-4 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 font-mono text-xs font-bold border border-slate-700 transition-all"
            >
              CLEAR
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
