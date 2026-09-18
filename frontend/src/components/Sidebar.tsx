import React from 'react';
import { 
  Activity, 
  Cpu, 
  BrainCircuit, 
  Hourglass, 
  Sliders, 
  History, 
  FileText, 
  Network,
  AlertCircle
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  alertCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onSelectTab, alertCount }) => {
  const navItems = [
    { id: 'overview', label: 'Live Cockpit', icon: Activity },
    { id: 'twin', label: 'Digital Twin View', icon: Cpu },
    { id: 'diagnostics', label: 'AI Diagnostics (XAI)', icon: BrainCircuit },
    { id: 'prognostics', label: 'RUL Prognostics', icon: Hourglass },
    { id: 'control', label: 'Mission & Faults', icon: Sliders },
    { id: 'history', label: 'History & Replay', icon: History },
    { id: 'report', label: 'Mission Report', icon: FileText },
    { id: 'architecture', label: 'Architecture & CAN', icon: Network },
  ];

  return (
    <aside className="w-64 bg-[#0a0f1d] border-r border-slate-800/80 flex flex-col justify-between select-none">
      <div className="py-4">
        <div className="px-5 mb-3 text-[11px] font-mono tracking-wider text-slate-500 uppercase">
          Navigation Modules
        </div>
        <nav className="space-y-1 px-3">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-sm font-semibold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </div>
                {item.id === 'diagnostics' && alertCount > 0 && (
                  <span className="px-1.5 py-0.2 rounded-full text-[10px] font-mono font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30">
                    {alertCount}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Engine Specs Box */}
      <div className="p-4 m-3 rounded-lg bg-slate-900/90 border border-slate-800 text-[11px] font-mono space-y-1 text-slate-400">
        <div className="text-slate-300 font-bold text-xs flex items-center justify-between">
          <span>ROTAX 915 iS</span>
          <span className="text-cyan-400">141 HP</span>
        </div>
        <div className="text-slate-500">Turbocharged 4-Cyl Piston</div>
        <div className="pt-1.5 border-t border-slate-800 text-[10px] flex justify-between">
          <span className="text-slate-500">Service Ceiling:</span>
          <span className="text-slate-300">23,000 ft</span>
        </div>
        <div className="flex justify-between text-[10px]">
          <span className="text-slate-500">Redline RPM:</span>
          <span className="text-slate-300">5,800 RPM</span>
        </div>
      </div>
    </aside>
  );
};
