import React, { useState, useEffect } from 'react';
import { fetchMissions, fetchMissionReplay } from '../services/api';
import { 
  History, 
  Play, 
  Pause, 
  RotateCcw, 
  FastForward, 
  Layers, 
  Calendar, 
  Clock, 
  Activity, 
  CheckCircle2 
} from 'lucide-react';

export const MissionHistoryView: React.FC = () => {
  const [missions, setMissions] = useState<any[]>([]);
  const [currentMission, setCurrentMission] = useState<any>(null);
  const [replayData, setReplayData] = useState<any[]>([]);
  const [replayIndex, setReplayIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [replaySpeed, setReplaySpeed] = useState<1 | 2 | 5>(1);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadMissions();
  }, []);

  const loadMissions = async () => {
    setLoading(true);
    try {
      const res = await fetchMissions();
      setMissions(res.history || []);
      setCurrentMission(res.current || null);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectReplay = async (missionId: string) => {
    try {
      const res = await fetchMissionReplay(missionId);
      if (res?.telemetry_stream?.length > 0) {
        setReplayData(res.telemetry_stream);
        setReplayIndex(0);
        setIsPlaying(true);
      }
    } catch (e) {
      console.error(e);
    }
  };

  // Replay playback loop
  useEffect(() => {
    let timer: ReturnType<typeof setInterval>;
    if (isPlaying && replayData.length > 0) {
      timer = setInterval(() => {
        setReplayIndex((prev) => {
          if (prev + 1 >= replayData.length) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 300 / replaySpeed);
    }
    return () => clearInterval(timer);
  }, [isPlaying, replayData, replaySpeed]);

  const currentPoint = replayData[replayIndex] || null;

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="glass-panel rounded-xl p-5 border-cyan-500/30">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center">
            <History className="w-6 h-6 text-emerald-400" />
          </div>
          <div>
            <h2 className="text-base font-bold font-mono tracking-wide text-white uppercase flex items-center gap-2">
              <span>MISSION HISTORY & CHRONOLOGICAL TELEMETRY REPLAY</span>
              <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-normal">
                TIMELINE SCRUBBER
              </span>
            </h2>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Review completed flight sorties, inspect peak stress excursions, and replay chronological 
              sensor and health streams with interactive timeline playback.
            </p>
          </div>
        </div>
      </div>

      {/* Chronological Replay Player Section */}
      {replayData.length > 0 && (
        <div className="glass-panel rounded-xl p-5 border-cyan-500/50 bg-slate-950/90 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono uppercase font-bold text-cyan-300">
                CHRONOLOGICAL MISSION REPLAY PLAYER
              </span>
              <span className="text-xs font-mono text-slate-500">
                [{replayIndex + 1} / {replayData.length} records]
              </span>
            </div>
            {/* Speed toggle */}
            <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 rounded p-1 text-xs font-mono">
              {([1, 2, 5] as const).map((spd) => (
                <button
                  key={spd}
                  onClick={() => setReplaySpeed(spd)}
                  className={`px-2 py-0.5 rounded font-bold ${
                    replaySpeed === spd ? 'bg-cyan-500/20 text-cyan-300' : 'text-slate-400'
                  }`}
                >
                  {spd}x
                </button>
              ))}
            </div>
          </div>

          {/* Scrubber Timeline */}
          <div className="space-y-1">
            <input
              type="range"
              min="0"
              max={replayData.length - 1}
              value={replayIndex}
              onChange={(e) => setReplayIndex(Number(e.target.value))}
              className="w-full accent-cyan-400 h-2 bg-slate-800 rounded cursor-pointer"
            />
            <div className="flex justify-between text-[11px] font-mono text-slate-500">
              <span>Start: {replayData[0]?.time}</span>
              <span className="text-cyan-400 font-bold">Current: {currentPoint?.time}</span>
              <span>End: {replayData[replayData.length - 1]?.time}</span>
            </div>
          </div>

          {/* Replay Synchronized Telemetry Display */}
          {currentPoint && (
            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3 pt-2 border-t border-slate-800/80">
              <div className="p-2.5 rounded bg-slate-900 border border-slate-800 text-xs font-mono">
                <div className="text-slate-500 text-[10px]">Speed (RPM)</div>
                <div className="text-base font-bold text-white mt-0.5">{currentPoint.rpm?.toFixed(0)}</div>
              </div>
              <div className="p-2.5 rounded bg-slate-900 border border-slate-800 text-xs font-mono">
                <div className="text-slate-500 text-[10px]">CHT Temp</div>
                <div className="text-base font-bold text-white mt-0.5">{currentPoint.engine_temp?.toFixed(1)} °C</div>
              </div>
              <div className="p-2.5 rounded bg-slate-900 border border-slate-800 text-xs font-mono">
                <div className="text-slate-500 text-[10px]">Oil Pressure</div>
                <div className="text-base font-bold text-white mt-0.5">{currentPoint.oil_pressure?.toFixed(2)} bar</div>
              </div>
              <div className="p-2.5 rounded bg-slate-900 border border-slate-800 text-xs font-mono">
                <div className="text-slate-500 text-[10px]">Vibration</div>
                <div className="text-base font-bold text-white mt-0.5">{currentPoint.vibration?.toFixed(2)} mm/s</div>
              </div>
              <div className="p-2.5 rounded bg-slate-900 border border-slate-800 text-xs font-mono">
                <div className="text-slate-500 text-[10px]">Fuel Flow</div>
                <div className="text-base font-bold text-white mt-0.5">{currentPoint.fuel_flow?.toFixed(1)} L/h</div>
              </div>
              <div className="p-2.5 rounded bg-slate-900 border border-slate-800 text-xs font-mono">
                <div className="text-slate-500 text-[10px]">Health Score</div>
                <div className={`text-base font-bold mt-0.5 ${
                  currentPoint.health_score > 80 ? 'text-emerald-400' : 'text-amber-400'
                }`}>
                  {currentPoint.health_score?.toFixed(1)}%
                </div>
              </div>
            </div>
          )}

          {/* Replay Controls */}
          <div className="flex items-center gap-3 pt-2">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="px-4 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-xs font-bold flex items-center gap-1.5"
            >
              {isPlaying ? <Pause className="w-3.5 h-3.5 fill-current" /> : <Play className="w-3.5 h-3.5 fill-current" />}
              <span>{isPlaying ? 'PAUSE' : 'PLAY'}</span>
            </button>
            <button
              onClick={() => { setReplayIndex(0); setIsPlaying(true); }}
              className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 font-mono text-xs font-bold flex items-center gap-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>RESTART</span>
            </button>
          </div>
        </div>
      )}

      {/* Completed Missions Table */}
      <div className="glass-panel rounded-xl p-5 border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xs font-mono uppercase font-bold text-slate-300 tracking-wider">
            Completed Flight Sortie Database (SQLite)
          </h3>
          <button
            onClick={loadMissions}
            className="text-xs font-mono text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
          >
            <RotateCcw className="w-3 h-3" />
            Refresh
          </button>
        </div>

        {missions.length === 0 ? (
          <div className="py-12 text-center text-slate-500 font-mono text-xs">
            No completed missions recorded yet. Run and stop a mission in Mission Control to log history.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="pb-2.5 font-semibold">Mission ID</th>
                  <th className="pb-2.5 font-semibold">Scenario Profile</th>
                  <th className="pb-2.5 font-semibold text-right">Duration</th>
                  <th className="pb-2.5 font-semibold text-right">Peak CHT</th>
                  <th className="pb-2.5 font-semibold text-right">Max Vib</th>
                  <th className="pb-2.5 font-semibold text-right">Final Health</th>
                  <th className="pb-2.5 font-semibold text-right">Final RUL</th>
                  <th className="pb-2.5 font-semibold text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {missions.map((m) => (
                  <tr key={m.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 font-bold text-cyan-300">{m.mission_id}</td>
                    <td className="py-3 text-slate-300">{m.scenario_name}</td>
                    <td className="py-3 text-right text-slate-400">{m.duration} s</td>
                    <td className="py-3 text-right text-white">{m.peak_temp} °C</td>
                    <td className="py-3 text-right text-white">{m.max_vibration} mm/s</td>
                    <td className={`py-3 text-right font-bold ${
                      m.final_health >= 80 ? 'text-emerald-400' : 'text-amber-400'
                    }`}>
                      {m.final_health}%
                    </td>
                    <td className="py-3 text-right text-cyan-400 font-bold">{m.final_rul} h</td>
                    <td className="py-3 text-center">
                      <button
                        onClick={() => handleSelectReplay(m.mission_id)}
                        className="px-2.5 py-1 rounded bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 text-[11px] font-bold inline-flex items-center gap-1"
                      >
                        <Play className="w-3 h-3 fill-current" />
                        Replay
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
