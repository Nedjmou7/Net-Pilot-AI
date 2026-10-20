import React from 'react';
import { Activity, ShieldCheck, Zap, Download, RefreshCw, FolderOpen } from 'lucide-react';
import { HealthStatus } from '../api/types';

interface HeaderProps {
  health: HealthStatus | null;
  projectName: string;
  onRefreshHealth: () => void;
  onToggleSidebar: () => void;
  onExportJson: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  health,
  projectName,
  onRefreshHealth,
  onToggleSidebar,
  onExportJson
}) => {
  const isOllamaOnline = health?.ollama?.ollama_connected ?? false;
  const isModelReady = health?.ollama?.model_available ?? false;

  return (
    <header className="h-14 border-b border-slate-800 bg-slate-900/80 backdrop-blur px-4 flex items-center justify-between z-20">
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          title="Toggle Projects"
        >
          <FolderOpen className="w-5 h-5" />
        </button>
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-base font-bold bg-gradient-to-r from-white via-cyan-100 to-cyan-400 bg-clip-text text-transparent leading-none">
              TopoGemma
            </h1>
            <p className="text-[10px] text-slate-400 tracking-wider">Cisco Packet Tracer AI Assistant</p>
          </div>
        </div>

        <div className="h-4 w-px bg-slate-800 mx-2" />

        <div className="text-xs font-medium text-slate-300 bg-slate-800/60 px-2.5 py-1 rounded-md border border-slate-700/50">
          <span className="text-slate-500 mr-1.5">Project:</span>
          <span className="text-cyan-400 font-semibold">{projectName}</span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Live Gemma / Local Health Indicator */}
        <div
          onClick={onRefreshHealth}
          className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-slate-800/80 border border-slate-700/60 text-xs cursor-pointer hover:border-slate-600 transition"
          title={`Ollama: ${isOllamaOnline ? 'Connected' : 'Offline'} | Model: ${health?.ollama?.model || 'gemma4:e4b'}`}
        >
          <span className="relative flex h-2 w-2">
            <span
              className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                isOllamaOnline ? (isModelReady ? 'bg-emerald-400' : 'bg-amber-400') : 'bg-rose-400'
              }`}
            />
            <span
              className={`relative inline-flex rounded-full h-2 w-2 ${
                isOllamaOnline ? (isModelReady ? 'bg-emerald-500' : 'bg-amber-500') : 'bg-rose-500'
              }`}
            />
          </span>
          <span className="text-slate-300 font-mono text-[11px]">
            {isOllamaOnline ? (isModelReady ? 'Gemma Online' : 'Model Ready (Base)') : 'Gemma Offline'}
          </span>
          <RefreshCw className="w-3 h-3 text-slate-400 hover:text-white" />
        </div>

        {/* 100% Local Privacy Badge */}
        <div className="hidden sm:flex items-center gap-1.5 px-2 py-1 rounded-md bg-cyan-950/40 border border-cyan-800/40 text-[11px] text-cyan-400">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>100% Local & Private</span>
        </div>

        {/* Export JSON button */}
        <button
          onClick={onExportJson}
          className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 border border-slate-700 transition"
          title="Export Topology JSON"
        >
          <Download className="w-3.5 h-3.5 text-slate-400" />
          <span>Export JSON</span>
        </button>
      </div>
    </header>
  );
};
