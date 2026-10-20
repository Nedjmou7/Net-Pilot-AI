import React from 'react';
import { AlertCircle, AlertTriangle, ChevronRight, Zap } from 'lucide-react';

interface RightColumnWidgetsProps {
  onOpenAlertDetails?: (alert: string) => void;
  onOpenAssistant: () => void;
}

export const RightColumnWidgets: React.FC<RightColumnWidgetsProps> = ({
  onOpenAlertDetails,
  onOpenAssistant
}) => {
  return (
    <div className="flex flex-col gap-3 h-full overflow-y-auto pr-0.5">
      {/* 1. GPU Thermals & Power */}
      <div className="bg-[#101520] border border-[#1d2536] rounded-xl p-3.5 shadow-sm">
        <div className="flex items-center justify-between pb-2 mb-2 border-b border-[#1b2332]">
          <h3 className="text-xs font-bold text-white tracking-wide">
            GPU Thermals & Power
          </h3>
          <span className="text-[10px] text-slate-400">Real-time per rack</span>
        </div>

        {/* Thermals Table */}
        <table className="w-full text-left text-[11px] font-mono">
          <thead>
            <tr className="text-slate-400 text-[10px] border-b border-[#18202e]">
              <th className="pb-1.5 font-medium">NODE</th>
              <th className="pb-1.5 font-medium">TEMP (avg/max)</th>
              <th className="pb-1.5 font-medium">POWER</th>
              <th className="pb-1.5 font-medium text-right">UTIL</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#161c28]">
            <tr className="text-slate-300">
              <td className="py-1.5 font-semibold text-slate-200">HGX-A01</td>
              <td className="py-1.5 text-slate-400">61°C / 68°C</td>
              <td className="py-1.5 text-slate-300">5.2 kW</td>
              <td className="py-1.5 text-right text-emerald-400 font-semibold">97%</td>
            </tr>
            <tr className="text-slate-300">
              <td className="py-1.5 font-semibold text-slate-200">HGX-A02</td>
              <td className="py-1.5 text-slate-400">63°C / 71°C</td>
              <td className="py-1.5 text-slate-300">5.3 kW</td>
              <td className="py-1.5 text-right text-emerald-400 font-semibold">98%</td>
            </tr>
            <tr className="text-slate-300">
              <td className="py-1.5 font-semibold text-slate-200">HGX-B01</td>
              <td className="py-1.5 text-slate-400">59°C / 66°C</td>
              <td className="py-1.5 text-slate-300">5.1 kW</td>
              <td className="py-1.5 text-right text-emerald-400 font-semibold">96%</td>
            </tr>
            {/* Highlighted Warning Node */}
            <tr className="text-amber-400 bg-amber-500/5">
              <td className="py-1.5 font-bold text-amber-400">HGX-B02</td>
              <td className="py-1.5 text-amber-300">74°C / 82°C</td>
              <td className="py-1.5 text-amber-300">5.8 kW</td>
              <td className="py-1.5 text-right font-bold text-amber-400">+Thermal</td>
            </tr>
            <tr className="text-slate-300">
              <td className="py-1.5 font-semibold text-slate-200">HGX-C01</td>
              <td className="py-1.5 text-slate-400">65°C / 73°C</td>
              <td className="py-1.5 text-slate-300">5.4 kW</td>
              <td className="py-1.5 text-right text-emerald-400 font-semibold">95%</td>
            </tr>
          </tbody>
        </table>

        {/* Footer: Cluster Power Draw */}
        <div className="mt-3 pt-2.5 border-t border-[#1b2332]">
          <div className="flex justify-between items-center text-[10px] font-mono text-slate-400 mb-1">
            <span className="font-semibold text-slate-400">CLUSTER POWER DRAW</span>
            <span className="text-slate-200 font-bold">21.4 kW / 25.6 kW</span>
          </div>
          <div className="h-1.5 w-full bg-[#171e2c] rounded-full overflow-hidden">
            <div className="h-full bg-cyan-400 rounded-full w-[83%]" />
          </div>
        </div>
      </div>

      {/* 2. Active Fabric Alerts & Anomalies */}
      <div className="bg-[#101520] border border-[#1d2536] rounded-xl p-3.5 shadow-sm">
        <div className="flex items-center justify-between pb-2 mb-2 border-b border-[#1b2332]">
          <h3 className="text-xs font-bold text-white tracking-wide">
            Active Fabric Alerts & Anomalies
          </h3>
          <button
            onClick={onOpenAssistant}
            className="text-[10px] text-cyan-400 hover:text-cyan-300 transition"
          >
            See all
          </button>
        </div>

        {/* 3 Quick Counter Cards */}
        <div className="grid grid-cols-3 gap-2 mb-3">
          <div className="bg-[#141a26] border border-[#1f2738] rounded-lg p-2 text-center">
            <div className="text-base font-extrabold text-white font-mono">2</div>
            <div className="text-[9px] text-slate-400">open now</div>
          </div>
          <div className="bg-[#141a26] border border-[#1f2738] rounded-lg p-2 text-center">
            <div className="text-base font-extrabold text-white font-mono">1</div>
            <div className="text-[9px] text-slate-400">muted</div>
          </div>
          <div className="bg-[#141a26] border border-[#1f2738] rounded-lg p-2 text-center">
            <div className="text-base font-extrabold text-white font-mono">1</div>
            <div className="text-[9px] text-slate-400">Last 5 min</div>
          </div>
        </div>

        {/* Alerts List */}
        <div className="space-y-2.5">
          {/* Alert 1 */}
          <div className="flex items-start gap-2">
            <span className="w-2 h-2 rounded-[2px] bg-rose-500 mt-1 flex-shrink-0" />
            <div className="flex-1">
              <div className="flex items-center justify-between text-[11px] font-mono">
                <span className="font-bold text-slate-200">NODE-HGX-B02</span>
                <span className="text-[10px] text-slate-500">2m ago</span>
              </div>
              <p className="text-[11px] text-slate-400 leading-snug">
                High packet re-transmission rate detected on ib1.port2
              </p>
            </div>
          </div>

          {/* Alert 2 */}
          <div className="flex items-start gap-2">
            <span className="w-2 h-2 rounded-[2px] bg-amber-500 mt-1 flex-shrink-0" />
            <div className="flex-1">
              <div className="flex items-center justify-between text-[11px] font-mono">
                <span className="font-bold text-slate-200">OST-01-MDT</span>
                <span className="text-[10px] text-slate-500">15m ago</span>
              </div>
              <p className="text-[11px] text-slate-400 leading-snug">
                Lustre MDS partition capacity exceeded 90% threshold
              </p>
            </div>
          </div>

          {/* Alert 3 */}
          <div className="flex items-start gap-2">
            <span className="w-2 h-2 rounded-[2px] bg-amber-500 mt-1 flex-shrink-0" />
            <div className="flex-1">
              <div className="flex items-center justify-between text-[11px] font-mono">
                <span className="font-bold text-slate-200">SRV-12-KLM</span>
                <span className="text-[10px] text-slate-500">30m ago</span>
              </div>
              <p className="text-[11px] text-slate-400 leading-snug">
                CPU usage on node SRV-12-KLM has spiked above 85% for the la...
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Rack / Node Health Matrix */}
      <div className="bg-[#101520] border border-[#1d2536] rounded-xl p-3.5 shadow-sm">
        <div className="flex items-center justify-between pb-2 mb-2 border-b border-[#1b2332]">
          <h3 className="text-xs font-bold text-white tracking-wide">
            Rack / Node Health Matrix
          </h3>
          <span className="text-[10px] text-slate-400 font-mono">115 nodes</span>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-3 text-[10px] text-slate-400 mb-2.5">
          <div className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-[2px] bg-emerald-500" />
            <span>Healthy</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-[2px] bg-amber-500" />
            <span>Warning</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-[2px] bg-rose-500" />
            <span>Critical</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-[2px] bg-[#273244]" />
            <span>Offline</span>
          </div>
        </div>

        {/* Grid of 15 x 6 = 90 chips matching screenshot */}
        <div className="grid grid-cols-15 gap-[3px] p-1.5 bg-[#0d111a] rounded-lg border border-[#18202d] mb-2.5">
          {Array.from({ length: 90 }).map((_, idx) => {
            // Replicate the exact pattern from the screenshot:
            // mostly green, with specific warning (yellow/orange), critical (red), and offline (gray)
            let color = 'bg-emerald-500';
            if ([7, 19, 42, 68].includes(idx)) color = 'bg-amber-500';
            else if ([24, 53, 79].includes(idx)) color = 'bg-rose-500';
            else if ([81, 82, 83, 84, 85, 86, 87, 88, 89].includes(idx)) color = 'bg-[#273244]';

            return (
              <div
                key={idx}
                className={`w-[14px] h-[14px] rounded-[2px] ${color} transition hover:scale-125 cursor-pointer shadow-sm`}
                title={`Node #${idx + 1}`}
              />
            );
          })}
        </div>

        {/* Footer Metrics */}
        <div className="flex justify-between items-center text-[10px] text-slate-400 font-mono pt-1">
          <span>99 Healthy · 4 Warning · 3 Critical</span>
          <span className="text-slate-500">9 Offline (maintenance)</span>
        </div>
      </div>
    </div>
  );
};
