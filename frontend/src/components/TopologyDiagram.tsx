import React, { useMemo, useCallback } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  BackgroundVariant,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType
} from 'reactflow';
import 'reactflow/dist/style.css';

import { Topology } from '../api/types';
import { nodeTypes } from './CustomNodes';

interface TopologyDiagramProps {
  topology: Topology | null;
  onUpdateDevicePosition: (deviceId: string, x: number, y: number) => void;
}

export const TopologyDiagram: React.FC<TopologyDiagramProps> = ({
  topology,
  onUpdateDevicePosition
}) => {
  // Convert topology.devices to React Flow Nodes
  const initialNodes: Node[] = useMemo(() => {
    if (!topology || !topology.devices) return [];

    const ipMap = new Map<string, string>();
    topology.ip_plan?.forEach((ip) => {
      if (!ipMap.has(ip.device)) {
        ipMap.set(ip.device, `${ip.ip}`);
      }
    });

    return topology.devices.map((dev) => ({
      id: dev.id,
      type: 'networkDevice',
      position: { x: dev.x, y: dev.y },
      data: {
        id: dev.id,
        label: dev.id,
        type: dev.type,
        model: dev.model,
        ip: ipMap.get(dev.id)
      }
    }));
  }, [topology]);

  // Convert topology.links to React Flow Edges
  const initialEdges: Edge[] = useMemo(() => {
    if (!topology || !topology.links) return [];

    return topology.links.map((link, idx) => {
      // Shorten port labels for display
      const shortA = link.a_port.replace("GigabitEthernet", "Gi").replace("FastEthernet", "Fa").replace("Serial", "Se");
      const shortB = link.b_port.replace("GigabitEthernet", "Gi").replace("FastEthernet", "Fa").replace("Serial", "Se");

      const isCrossover = link.cable === 'crossover';
      const isSerial = link.cable === 'serial';

      let strokeColor = '#06b6d4'; // cyan for straight
      if (isCrossover) strokeColor = '#f59e0b'; // amber for crossover
      if (isSerial) strokeColor = '#ef4444'; // red for serial

      return {
        id: `link-${link.a}-${link.b}-${idx}`,
        source: link.a,
        target: link.b,
        animated: true,
        style: {
          stroke: strokeColor,
          strokeWidth: 2,
          strokeDasharray: isCrossover ? '5 5' : undefined
        },
        label: `${shortA} ↔ ${shortB}`,
        labelStyle: { fill: '#cbd5e1', fontSize: 10, fontFamily: 'monospace' },
        labelBgStyle: { fill: '#0f172a', fillOpacity: 0.85 },
        labelBgPadding: [4, 2] as [number, number],
        labelBgBorderRadius: 4,
        markerEnd: {
          type: MarkerType.ArrowClosed,
          width: 12,
          height: 12,
          color: strokeColor
        }
      };
    });
  }, [topology]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Sync state when topology prop changes
  React.useEffect(() => {
    setNodes(initialNodes);
  }, [initialNodes, setNodes]);

  React.useEffect(() => {
    setEdges(initialEdges);
  }, [initialEdges, setEdges]);

  const handleNodeDragStop = useCallback(
    (_: React.MouseEvent, node: Node) => {
      onUpdateDevicePosition(node.id, Math.round(node.position.x), Math.round(node.position.y));
    },
    [onUpdateDevicePosition]
  );

  return (
    <div className="w-full h-full relative bg-slate-950 flex flex-col">
      {/* Top Diagram Toolbar */}
      <div className="h-9 px-4 border-b border-slate-800 bg-slate-900/40 flex items-center justify-between text-xs text-slate-400">
        <div className="flex items-center gap-3">
          <span className="font-semibold text-slate-200">Interactive Canvas</span>
          <span className="text-[11px] text-slate-500">
            {topology?.devices?.length || 0} Devices, {topology?.links?.length || 0} Links
          </span>
        </div>
        <div className="flex items-center gap-4 text-[11px]">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-0.5 bg-cyan-400 rounded-full" />
            <span>Straight</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-0.5 border-t border-dashed border-amber-400" />
            <span>Crossover</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-0.5 bg-rose-500 rounded-full" />
            <span>Serial</span>
          </div>
        </div>
      </div>

      {/* React Flow Viewport */}
      <div className="flex-1 w-full h-full relative">
        {!topology || topology.devices.length === 0 ? (
          <div className="w-full h-full flex flex-col items-center justify-center text-slate-500 text-xs gap-2">
            <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
              Interactive Canvas Ready
            </div>
            <p>Send a prompt to generate or load a topology.</p>
          </div>
        ) : (
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeDragStop={handleNodeDragStop}
            nodeTypes={nodeTypes}
            fitView
            fitViewOptions={{ padding: 0.2 }}
            minZoom={0.2}
            maxZoom={2.0}
            className="bg-slate-950"
          >
            <Background color="#1e293b" gap={20} size={1} variant={BackgroundVariant.Dots} />
            <Controls className="!bg-slate-900 !border-slate-800 !text-slate-300 !fill-slate-300 [&>button]:!border-slate-800 hover:[&>button]:!bg-slate-800" />
            <MiniMap
              nodeColor={(n) => {
                if (n.data?.type === 'router') return '#06b6d4';
                if (n.data?.type === 'switch') return '#10b981';
                if (n.data?.type === 'server') return '#a855f7';
                return '#3b82f6';
              }}
              maskColor="rgba(15, 23, 42, 0.7)"
              className="!bg-slate-900 !border-slate-800 rounded-lg overflow-hidden"
            />
          </ReactFlow>
        )}
      </div>
    </div>
  );
};
