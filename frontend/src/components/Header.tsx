import React from 'react';
import { Bot, ChevronDown, Network, Radio, ShieldCheck, Terminal, Activity } from 'lucide-react';
import { HealthStatus } from '../api/types';

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  health: HealthStatus | null;
  onOpenAssistant: () => void;
  onExportJson: () => void;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab, health, onOpenAssistant }) => {
  const isOllamaOnline = health?.ollama?.ollama_connected ?? false;
  const navItems = [
    { id: 'topology', label: 'Topology', icon: Network },
    { id: 'configs', label: 'IOS Configs', icon: Terminal },
    { id: 'metrics', label: 'Validation', icon: ShieldCheck },
  ];

  return (
    <header className="app-header shrink-0 z-30">
      <div className="header-topline">
        <div className="flex items-center gap-2 text-[11px] font-semibold tracking-wide text-slate-500">
          <span className="brand-mark"><Network className="w-4 h-4" /></span>
          <span>NETPILOT <span className="font-normal text-slate-400">/ NETWORK AUTOMATION</span></span>
        </div>
        <div className="flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-[11px] font-medium text-emerald-700">
          <span className={`w-1.5 h-1.5 rounded-full ${isOllamaOnline ? 'bg-emerald-500' : 'bg-amber-500'}`} />
          {isOllamaOnline ? 'AI agent online' : 'AI agent ready'}
        </div>
      </div>
      <div className="header-main">
        <div className="flex min-w-0 items-center gap-3">
          <div className="brand-icon"><Network className="w-5 h-5" /></div>
          <div className="min-w-0">
            <div className="text-[15px] font-bold tracking-tight text-slate-900">NetPilot <span className="text-cisco">AI</span></div>
            <div className="hidden sm:block text-[11px] text-slate-500">Cisco Packet Tracer workspace</div>
          </div>
          <span className="hidden md:inline-flex items-center gap-1.5 rounded-md bg-blue-50 px-2 py-1 text-[10px] font-semibold text-blue-700"><Radio className="h-3 w-3" /> PACKET TRACER</span>
        </div>

        <nav className="header-nav" aria-label="Main navigation">
          {navItems.map(({ id, label, icon: Icon }) => (
            <button key={id} onClick={() => setActiveTab(id)} className={`header-nav-item ${activeTab === id ? 'active' : ''}`}>
              <Icon className="h-4 w-4" /><span>{label}</span>
            </button>
          ))}
        </nav>

        <div className="header-actions">
          <button onClick={onOpenAssistant} className="assistant-button">
            <Bot className="h-4 w-4" /><span>Ask AI agent</span><span className={`status-dot ${isOllamaOnline ? 'online' : ''}`} />
          </button>
          <button className="profile-button" aria-label="User menu"><span className="profile-avatar">NP</span><ChevronDown className="h-3.5 w-3.5 text-slate-500" /></button>
        </div>
      </div>
      <div className="header-context"><Activity className="h-3.5 w-3.5 text-cisco" /><span>Design, validate, and send network topologies to Packet Tracer</span></div>
    </header>
  );
};
