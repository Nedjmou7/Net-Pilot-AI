import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { Router, Server, Laptop, Network } from 'lucide-react';
import { DeviceType } from '../api/types';

interface CustomNodeData {
  id: string;
  label: string;
  type: DeviceType;
  model: string;
  ip?: string;
}

export const NetworkNode = memo(({ data }: { data: CustomNodeData }) => {
  const getIcon = () => {
    switch (data.type) {
      case 'router':
        return <Router className="w-6 h-6 text-cyan-400" />;
      case 'switch':
        return <Network className="w-6 h-6 text-emerald-400" />;
      case 'server':
        return <Server className="w-6 h-6 text-purple-400" />;
      case 'pc':
      default:
        return <Laptop className="w-6 h-6 text-blue-400" />;
    }
  };

  const getBorderColor = () => {
    switch (data.type) {
      case 'router':
        return 'border-cyan-500/50 hover:border-cyan-400 shadow-cyan-950/40';
      case 'switch':
        return 'border-emerald-500/50 hover:border-emerald-400 shadow-emerald-950/40';
      case 'server':
        return 'border-purple-500/50 hover:border-purple-400 shadow-purple-950/40';
      case 'pc':
      default:
        return 'border-blue-500/50 hover:border-blue-400 shadow-blue-950/40';
    }
  };

  return (
    <div className={`px-4 py-3 rounded-xl bg-slate-900/90 backdrop-blur border-2 shadow-lg ${getBorderColor()} transition-all duration-200 min-w-[130px]`}>
      <Handle type="target" position={Position.Top} className="!w-2.5 !h-2.5 !bg-cyan-400 !border-slate-950" />
      <Handle type="source" position={Position.Bottom} className="!w-2.5 !h-2.5 !bg-cyan-400 !border-slate-950" />
      <Handle type="target" position={Position.Left} className="!w-2.5 !h-2.5 !bg-cyan-400 !border-slate-950" />
      <Handle type="source" position={Position.Right} className="!w-2.5 !h-2.5 !bg-cyan-400 !border-slate-950" />

      <div className="flex items-center gap-2.5">
        <div className="p-1.5 rounded-lg bg-slate-800/80 border border-slate-700/50">
          {getIcon()}
        </div>
        <div>
          <div className="text-sm font-bold text-white tracking-wide">{data.label}</div>
          <div className="text-[10px] text-slate-400 font-mono">{data.model}</div>
        </div>
      </div>

      {data.ip && (
        <div className="mt-2 pt-1.5 border-t border-slate-800 text-[11px] font-mono text-cyan-300 truncate">
          {data.ip}
        </div>
      )}
    </div>
  );
});

export const nodeTypes = {
  networkDevice: NetworkNode,
};
