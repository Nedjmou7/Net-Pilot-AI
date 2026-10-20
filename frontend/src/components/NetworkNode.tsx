import React, { memo } from "react";
import { Handle, Position, NodeProps } from "reactflow";
import { Router as RouterIcon, Network, Monitor, Server as ServerIcon } from "lucide-react";
import { DeviceType } from "../types/topology";

export interface NetworkNodeData {
  id: string;
  type: DeviceType;
  model: string;
  ips: string[];
}

const NetworkNode: React.FC<NodeProps<NetworkNodeData>> = ({ data, selected }) => {
  const { id, type, model, ips } = data;

  // Icon and theme per device type
  const getDeviceVisuals = () => {
    switch (type) {
      case "router":
        return {
          icon: <RouterIcon className="w-6 h-6 text-sky-400" />,
          borderColor: "border-sky-500",
          bgColor: "bg-sky-950/60",
          glowColor: "shadow-sky-500/30",
          tagBg: "bg-sky-900/60 text-sky-300"
        };
      case "switch":
        return {
          icon: <Network className="w-6 h-6 text-teal-400" />,
          borderColor: "border-teal-500",
          bgColor: "bg-teal-950/60",
          glowColor: "shadow-teal-500/30",
          tagBg: "bg-teal-900/60 text-teal-300"
        };
      case "server":
        return {
          icon: <ServerIcon className="w-6 h-6 text-amber-400" />,
          borderColor: "border-amber-500",
          bgColor: "bg-amber-950/60",
          glowColor: "shadow-amber-500/30",
          tagBg: "bg-amber-900/60 text-amber-300"
        };
      case "pc":
      default:
        return {
          icon: <Monitor className="w-6 h-6 text-indigo-400" />,
          borderColor: "border-indigo-500",
          bgColor: "bg-indigo-950/60",
          glowColor: "shadow-indigo-500/30",
          tagBg: "bg-indigo-900/60 text-indigo-300"
        };
    }
  };

  const visuals = getDeviceVisuals();

  return (
    <div
      className={`relative px-4 py-3 rounded-xl border-2 backdrop-blur-md transition-all duration-200 min-w-[140px] shadow-lg ${visuals.borderColor} ${visuals.bgColor} ${selected ? `ring-2 ring-white ${visuals.glowColor}` : "hover:border-slate-300"}`}
    >
      {/* 4 Multi-directional handles */}
      <Handle type="target" position={Position.Top} id="top" className="!bg-slate-400 !w-2 !h-2" />
      <Handle type="source" position={Position.Bottom} id="bottom" className="!bg-slate-400 !w-2 !h-2" />
      <Handle type="target" position={Position.Left} id="left" className="!bg-slate-400 !w-2 !h-2" />
      <Handle type="source" position={Position.Right} id="right" className="!bg-slate-400 !w-2 !h-2" />

      {/* Node Header */}
      <div className="flex items-center space-x-2.5">
        <div className="p-1.5 rounded-lg bg-slate-900/80 border border-slate-700/60 shadow-inner">
          {visuals.icon}
        </div>
        <div>
          <div className="font-bold text-slate-100 text-sm tracking-wide">{id}</div>
          <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${visuals.tagBg}`}>
            {model}
          </span>
        </div>
      </div>

      {/* IP Badges */}
      {ips && ips.length > 0 && (
        <div className="mt-2.5 pt-2 border-t border-slate-700/50 space-y-1">
          {ips.slice(0, 3).map((ip, idx) => (
            <div key={idx} className="text-[10px] font-mono text-slate-300 flex items-center justify-between">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block mr-1"></span>
              <span className="truncate">{ip}</span>
            </div>
          ))}
          {ips.length > 3 && (
            <div className="text-[9px] text-slate-400 italic">+{ips.length - 3} more subnets</div>
          )}
        </div>
      )}
    </div>
  );
};

export default memo(NetworkNode);
