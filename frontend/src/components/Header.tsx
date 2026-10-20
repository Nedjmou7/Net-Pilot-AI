import React from "react";
import { Network, Cpu, RefreshCw, ToggleLeft, ToggleRight, PanelLeftClose, PanelLeftOpen } from "lucide-react";
import { HealthResponse } from "../types/topology";

interface HeaderProps {
  health: HealthResponse | null;
  onRefreshHealth: () => void;
  useMock: boolean;
  onToggleMock: () => void;
  isAssistantVisible: boolean;
  onToggleAssistant: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  health,
  onRefreshHealth,
  useMock,
  onToggleMock,
  isAssistantVisible,
  onToggleAssistant
}) => {
  const isOnline = health?.ollama_online ?? false;
  const modelName = health?.ollama_model || "gemma4:e4b";

  return (
    <header className="h-14 bg-slate-900 border-b border-slate-800 px-4 flex items-center justify-between shrink-0 select-none">
      {/* Brand & Logo */}
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-sky-600 to-teal-400 flex items-center justify-center shadow-lg shadow-sky-500/20">
          <Network className="w-4 h-4 text-white" />
        </div>
        <div>
          <div className="flex items-center space-x-1.5">
            <h1 className="font-bold text-sm tracking-tight text-white">TopoGemma</h1>
            <span className="text-[10px] font-mono uppercase bg-sky-500/10 text-sky-400 px-1.5 py-0.2 rounded border border-sky-500/30">
              Net-Pilot AI
            </span>
          </div>
          <p className="text-[10px] text-slate-400">Local AI Assistant for Cisco Packet Tracer</p>
        </div>
      </div>

      {/* Center Status Indicators */}
      <div className="flex items-center space-x-3">
      {/* Assistant Panel Toggle */}
      <button
        onClick={onToggleAssistant}
        className="hidden sm:flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-950 px-2.5 py-1.5 text-xs text-slate-300 transition-colors hover:border-sky-500/50 hover:bg-slate-800 hover:text-sky-300"
        title={isAssistantVisible ? "Hide Gemma Assistant" : "Show Gemma Assistant"}
        aria-label={isAssistantVisible ? "Hide Gemma Assistant" : "Show Gemma Assistant"}
      >
        {isAssistantVisible ? (
          <PanelLeftClose className="h-3.5 w-3.5" />
        ) : (
          <PanelLeftOpen className="h-3.5 w-3.5" />
        )}
        <span>{isAssistantVisible ? "Hide Assistant" : "Show Assistant"}</span>
      </button>

      {/* Model Badge */}
        <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-xs">
          <Cpu className="w-3.5 h-3.5 text-sky-400" />
          <span className="text-slate-400 font-mono text-[11px]">{modelName}</span>
        </div>

        {/* Health Status Indicator */}
        <div className="flex items-center space-x-2 px-3 py-1 rounded-lg bg-slate-950 border border-slate-800">
          <span className="relative flex h-2 w-2">
            {isOnline ? (
              <>
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </>
            ) : (
              <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
            )}
          </span>
          <span className="text-xs text-slate-300 font-medium">
            {isOnline ? "Gemma Online" : "Local Engine (Offline Mock)"}
          </span>
          <button
            onClick={onRefreshHealth}
            title="Refresh Status"
            className="text-slate-500 hover:text-slate-300 transition-colors p-0.5"
          >
            <RefreshCw className="w-3 h-3" />
          </button>
        </div>

        {/* Mock API Toggle */}
        <button
          onClick={onToggleMock}
          className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-lg border text-xs transition-colors ${
            useMock
              ? "bg-amber-950/60 border-amber-600/40 text-amber-300"
              : "bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200"
          }`}
          title="Toggle between mock responses and live local backend"
        >
          {useMock ? <ToggleRight className="w-4 h-4 text-amber-400" /> : <ToggleLeft className="w-4 h-4 text-slate-500" />}
          <span className="text-[11px]">Mock Mode: {useMock ? "ON" : "OFF"}</span>
        </button>
      </div>
    </header>
  );
};
