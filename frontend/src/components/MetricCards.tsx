import React from 'react';
import { Search, Calendar, ChevronDown, Download } from 'lucide-react';

interface MetricCardsProps {
  onExport: () => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
}

export const MetricCards: React.FC<MetricCardsProps> = ({
  onExport,
  searchQuery,
  onSearchChange
}) => {
  return (
    <div className="flex flex-col gap-3.5 mb-3.5">
      {/* Page Title & Controls Bar */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Network topology</h1>
          <p className="mt-0.5 text-xs text-slate-500">Cisco Packet Tracer lab overview</p>
        </div>

        <div className="flex flex-wrap items-center justify-end gap-2">
          {/* Search Box */}
          <div className="relative flex items-center">
            <input
              type="text"
              placeholder="Search"
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              className="w-36 sm:w-48 pl-3 pr-8 py-2 text-xs bg-white border border-slate-200 rounded-lg text-slate-700 placeholder-slate-400 focus:outline-none focus:border-sky-500"
            />
            <Search className="w-3.5 h-3.5 text-slate-500 absolute right-2.5 pointer-events-none" />
          </div>

          {/* Date Picker Button */}
          <button className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-white border border-slate-200 text-xs text-slate-600 hover:bg-slate-50 transition">
            <Calendar className="w-3.5 h-3.5 text-slate-400" />
            <span>Sept 17 - Now</span>
          </button>

          {/* Duration Selector */}
          <button className="hidden sm:flex items-center gap-1 px-3 py-1.5 rounded-md bg-white border border-slate-200 text-xs text-slate-600 hover:bg-slate-50 transition">
            <span>3 days</span>
            <ChevronDown className="w-3 h-3 text-slate-400" />
          </button>

          {/* Export Button */}
          <button
            onClick={onExport}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-xs text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition"
          >
            <span>Export</span>
            <Download className="w-3 h-3 text-slate-400" />
          </button>
        </div>
      </div>

      {/* 4 Top KPI Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3">
        {/* Card 1: Compute Capacity */}
        <div className="bg-[#101520] border border-[#1d2536] rounded-xl p-3.5 flex flex-col justify-between shadow-sm">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[10px] font-bold tracking-wider text-slate-400 uppercase">
              COMPUTE CAPACITY
            </span>
            <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-emerald-950/80 text-emerald-400 border border-emerald-800/60">
              ONLINE
            </span>
          </div>

          <div className="flex items-baseline gap-2 mb-0.5">
            <span className="text-2xl font-extrabold text-white font-mono">512</span>
            <span className="text-xs font-semibold text-slate-300">H100 GPUs</span>
          </div>
          <div className="text-[11px] text-slate-400 mb-3">64 nodes · HGX arch</div>

          {/* Progress Bar */}
          <div>
            <div className="h-1.5 w-full bg-[#182030] rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full w-[80%]" />
            </div>
            <div className="flex justify-between items-center text-[10px] text-slate-400 font-mono mt-1">
              <span>512/640</span>
              <span className="text-cyan-400 font-semibold">80%</span>
            </div>
          </div>
        </div>

        {/* Card 2: Port Latency */}
        <div className="bg-[#101520] border border-[#1d2536] rounded-xl p-3.5 flex flex-col justify-between shadow-sm">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[10px] font-bold tracking-wider text-slate-400 uppercase">
              PORT LATENCY
            </span>
            <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-emerald-950/80 text-emerald-400 border border-emerald-800/60">
              OPTIMAL
            </span>
          </div>

          <div className="flex items-baseline gap-1.5 mb-0.5">
            <span className="text-2xl font-extrabold text-white font-mono">1.15</span>
            <span className="text-xs font-semibold text-slate-300">μs</span>
          </div>
          <div className="text-[11px] text-slate-400 mb-2">RDMA avg · p99: 2.8μs</div>

          {/* Mini Equalizer Bar Chart */}
          <div>
            <div className="flex items-end gap-[3px] h-6 w-full">
              {[4, 6, 8, 12, 10, 16, 20, 24, 22, 18, 14, 12, 9, 7, 5, 4, 3, 4, 6, 5, 3, 2].map((val, i) => (
                <div
                  key={i}
                  style={{ height: `${(val / 24) * 100}%` }}
                  className="flex-1 bg-gradient-to-t from-emerald-600 to-cyan-400 rounded-t-sm opacity-85"
                />
              ))}
            </div>
            <div className="flex justify-between text-[9px] text-slate-500 font-mono mt-1">
              <span>0s</span>
              <span>10s</span>
            </div>
          </div>
        </div>

        {/* Card 3: Fabric Goodput */}
        <div className="bg-[#101520] border border-[#1d2536] rounded-xl p-3.5 flex flex-col justify-between shadow-sm">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[10px] font-bold tracking-wider text-slate-400 uppercase">
              FABRIC GOODPUT
            </span>
            <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-cyan-950/80 text-cyan-400 border border-cyan-800/60">
              ACTIVE
            </span>
          </div>

          <div className="flex items-baseline gap-1.5 mb-0.5">
            <span className="text-2xl font-extrabold text-white font-mono">98.4</span>
            <span className="text-xs font-semibold text-slate-300">%</span>
          </div>
          <div className="text-[11px] text-slate-400 mb-2">IB non-blocking · 51.2 Tb/s peak</div>

          {/* Mini Blue Bar Chart */}
          <div>
            <div className="flex items-end gap-[3px] h-6 w-full">
              {[12, 14, 13, 15, 17, 16, 18, 19, 18, 17, 19, 20, 18, 19, 21, 20, 19, 21, 22, 21, 20, 22].map((val, i) => (
                <div
                  key={i}
                  style={{ height: `${(val / 24) * 100}%` }}
                  className="flex-1 bg-cyan-500 rounded-t-sm opacity-90"
                />
              ))}
            </div>
            <div className="h-1 mt-1" />
          </div>
        </div>

        {/* Card 4: Aggregate Uptime */}
        <div className="bg-[#101520] border border-[#1d2536] rounded-xl p-3.5 flex flex-col justify-between shadow-sm">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[10px] font-bold tracking-wider text-slate-400 uppercase">
              AGGREGATE UPTIME
            </span>
            <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-amber-950/80 text-amber-400 border border-amber-800/60">
              30D
            </span>
          </div>

          <div className="flex items-baseline gap-1.5 mb-0.5">
            <span className="text-2xl font-extrabold text-white font-mono">98.9</span>
            <span className="text-xs font-semibold text-slate-300">%</span>
          </div>
          <div className="text-[11px] text-slate-400 mb-2">0 unscheduled dropouts</div>

          {/* Dot Matrix Grid */}
          <div className="pt-1">
            <div className="grid grid-rows-3 grid-flow-col gap-[3.5px] h-6 items-center">
              {Array.from({ length: 66 }).map((_, i) => (
                <div
                  key={i}
                  className={`w-1.5 h-1.5 rounded-full ${
                    i === 22 || i === 47
                      ? 'bg-amber-600/40'
                      : 'bg-amber-400 shadow-[0_0_3px_rgba(251,191,36,0.3)]'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
