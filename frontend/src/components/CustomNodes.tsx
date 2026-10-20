import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { DeviceType } from '../api/types';

interface CustomNodeData {
  id: string;
  label: string;
  type: DeviceType;
  model: string;
  ip?: string;
  selected?: boolean;
  portsCount?: string;
  bandwidth?: string;
  badge?: string;
}

const RouterIcon = () => <svg viewBox="0 0 100 64" aria-hidden="true">
  <ellipse cx="50" cy="18" rx="35" ry="12" fill="#d7edf7" stroke="#526b7c" strokeWidth="2" />
  <path d="M15 18v23c0 7 16 12 35 12s35-5 35-12V18" fill="#a8d5e7" stroke="#526b7c" strokeWidth="2" />
  <path d="M15 31c0 7 16 12 35 12s35-5 35-12" fill="none" stroke="#7795a5" strokeWidth="1.5" />
  <path d="m37 23-8-5 8-5m-8 5h18m16 5 8-5-8-5m8 5H53" fill="none" stroke="#1877a8" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
  <circle cx="39" cy="47" r="2" fill="#4baf63" /><circle cx="47" cy="47" r="2" fill="#4baf63" /><circle cx="55" cy="47" r="2" fill="#e8ad3c" />
</svg>;

const SwitchIcon = () => <svg viewBox="0 0 100 64" aria-hidden="true">
  <path d="m19 15 62 0 9 8v29H19z" fill="#d8e4eb" stroke="#4e6574" strokeWidth="2" />
  <path d="m19 15 9-8h62l-9 8z" fill="#eef4f7" stroke="#4e6574" strokeWidth="2" />
  <path d="M28 7v8m62-8v8" stroke="#718996" strokeWidth="1.5" />
  <path d="M27 25h5v4h-5zm10 0h5v4h-5zm10 0h5v4h-5zm10 0h5v4h-5zm10 0h5v4h-5zm10 0h5v4h-5zM27 34h5v4h-5zm10 0h5v4h-5zm10 0h5v4h-5zm10 0h5v4h-5zm10 0h5v4h-5zm10 0h5v4h-5z" fill="#647b89" />
  <circle cx="79" cy="46" r="2" fill="#55ab69" /><circle cx="71" cy="46" r="2" fill="#55ab69" />
</svg>;

const PcIcon = () => <svg viewBox="0 0 100 76" aria-hidden="true">
  <rect x="14" y="7" width="57" height="43" rx="3" fill="#e5edf2" stroke="#506978" strokeWidth="2" />
  <rect x="19" y="12" width="47" height="32" rx="1" fill="#bfe2ef" stroke="#7595a3" strokeWidth="1.5" />
  <path d="M38 50v8m10-8v8m-18 2h35" fill="none" stroke="#506978" strokeWidth="3" strokeLinecap="round" />
  <rect x="76" y="27" width="14" height="37" rx="2" fill="#d5e0e7" stroke="#506978" strokeWidth="2" />
  <circle cx="83" cy="34" r="1.8" fill="#4fa964" /><path d="M80 41h6m-6 5h6m-6 5h6" stroke="#7c919c" strokeWidth="1.5" />
</svg>;

const ServerIcon = () => <svg viewBox="0 0 76 76" aria-hidden="true">
  <rect x="17" y="6" width="42" height="64" rx="3" fill="#d9e4eb" stroke="#506978" strokeWidth="2" />
  {[14, 29, 44, 59].map((y) => <g key={y}><rect x="22" y={y} width="32" height="10" rx="1" fill="#eef4f7" stroke="#92a4ae" /><circle cx="28" cy={y + 5} r="1.7" fill="#54a969" /><path d={`M34 ${y + 4}h15`} stroke="#8396a1" strokeWidth="1.5" /></g>)}
</svg>;

const DeviceGlyph: React.FC<{ type: DeviceType }> = ({ type }) => {
  if (type === 'router') return <RouterIcon />;
  if (type === 'switch') return <SwitchIcon />;
  if (type === 'server') return <ServerIcon />;
  return <PcIcon />;
};

const deviceName: Record<DeviceType, string> = { router: 'Router', switch: 'Switch', pc: 'PC-PT', server: 'Server' };

export const NetworkNode = memo(({ data }: { data: CustomNodeData }) => (
  <div className={`pt-device-node ${data.selected ? 'chosen' : ''}`}>
    <Handle id="target-top" type="target" position={Position.Top} className="pt-node-handle" />
    <Handle id="source-top" type="source" position={Position.Top} className="pt-node-handle" />
    <Handle id="source-bottom" type="source" position={Position.Bottom} className="pt-node-handle" />
    <Handle id="target-bottom" type="target" position={Position.Bottom} className="pt-node-handle" />
    <Handle id="target-left" type="target" position={Position.Left} className="pt-node-handle" />
    <Handle id="source-left" type="source" position={Position.Left} className="pt-node-handle" />
    <Handle id="source-right" type="source" position={Position.Right} className="pt-node-handle" />
    <Handle id="target-right" type="target" position={Position.Right} className="pt-node-handle" />
    <div className="pt-device-glyph"><DeviceGlyph type={data.type} /></div>
    <div className="pt-device-label">{data.label}</div>
    <div className="pt-device-model">{data.model || deviceName[data.type]}</div>
  </div>
));

export const nodeTypes = { networkDevice: NetworkNode };
