import React, { useState } from 'react';
import { useEngineStream } from './services/api';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { OverviewDashboard } from './pages/OverviewDashboard';
import { DigitalTwinView } from './pages/DigitalTwinView';
import { AIDiagnosticsView } from './pages/AIDiagnosticsView';
import { PrognosticsRULView } from './pages/PrognosticsRULView';
import { MissionControlView } from './pages/MissionControlView';
import { MissionHistoryView } from './pages/MissionHistoryView';
import { HealthReportView } from './pages/HealthReportView';
import { ArchitectureView } from './pages/ArchitectureView';

export function App() {
  const { data, history, isConnected } = useEngineStream();
  const [activeTab, setActiveTab] = useState('overview');

  const alertCount = data?.active_alerts?.filter((a) => !a.acknowledged).length || 0;

  return (
    <div className="min-h-screen bg-[#080c14] text-slate-100 flex flex-col font-sans">
      {/* Top Avionics Navigation Bar */}
      <Header data={data} isConnected={isConnected} />

      {/* Main Workspace Frame */}
      <div className="flex-1 flex overflow-hidden">
        {/* Navigation Sidebar */}
        <Sidebar
          currentTab={activeTab}
          onSelectTab={setActiveTab}
          alertCount={alertCount}
        />

        {/* Dynamic Content Panel */}
        <main className="flex-1 p-6 overflow-y-auto max-h-[calc(100vh-4rem)]">
          {activeTab === 'overview' && (
            <OverviewDashboard data={data} history={history} />
          )}
          {activeTab === 'twin' && (
            <DigitalTwinView data={data} />
          )}
          {activeTab === 'diagnostics' && (
            <AIDiagnosticsView data={data} />
          )}
          {activeTab === 'prognostics' && (
            <PrognosticsRULView data={data} history={history} />
          )}
          {activeTab === 'control' && (
            <MissionControlView data={data} />
          )}
          {activeTab === 'history' && (
            <MissionHistoryView />
          )}
          {activeTab === 'report' && (
            <HealthReportView data={data} />
          )}
          {activeTab === 'architecture' && (
            <ArchitectureView data={data} />
          )}
        </main>
      </div>

      {/* Bottom Status Bar */}
      <footer className="h-8 bg-[#090d18] border-t border-slate-800/80 px-6 flex items-center justify-between text-[11px] font-mono text-slate-500 select-none">
        <div className="flex items-center gap-4">
          <span>DRDO PS 26054 PROTOTYPE</span>
          <span className="text-slate-700">|</span>
          <span className="text-cyan-500">MALE UAV PISTON ENGINE DIGITAL TWIN</span>
          <span className="text-slate-700">|</span>
          <span className="text-amber-500/80">SYNTHETIC SIMULATION (NOT CONNECTED TO PHYSICAL AIRCRAFT)</span>
        </div>
        <div className="flex items-center gap-3">
          <span>SOCKETCAN: {isConnected ? 'SYNCHRONIZED (10 Hz)' : 'DISCONNECTED'}</span>
          <span className="text-slate-700">|</span>
          <span>BUILD: V2.0-DRDO-READY</span>
        </div>
      </footer>
    </div>
  );
}

export default App;
