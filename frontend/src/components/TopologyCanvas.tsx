import React, { useMemo, useCallback } from "react";
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
  ConnectionLineType,
  NodeChange,
  applyNodeChanges
} from "reactflow";
import NetworkNode, { NetworkNodeData } from "./NetworkNode";
import { Topology } from "../types/topology";

interface TopologyCanvasProps {
  topology: Topology | null;
  onUpdateCoordinates?: (deviceId: string, x: number, y: number) => void;
}

const nodeTypes = {
  networkDevice: NetworkNode
};

export const TopologyCanvas: React.FC<TopologyCanvasProps> = ({ topology, onUpdateCoordinates }) => {
  // Convert topology.devices to React Flow Nodes
  const initialNodes: Node<NetworkNodeData>[] = useMemo(() => {
    if (!topology || !topology.devices) return [];

    const ipMap: Record<string, string[]> = {};
    for (const item of topology.ip_plan || []) {
      if (!ipMap[item.device]) ipMap[item.device] = [];
      ipMap[item.device].push(`${item.interface}: ${item.ip}`);
    }

    return topology.devices.map((dev) => ({
      id: dev.id,
      type: "networkDevice",
      position: { x: dev.x, y: dev.y },
      data: {
        id: dev.id,
        type: dev.type,
        model: dev.model,
        ips: ipMap[dev.id] || []
      }
    }));
  }, [topology]);

  // Convert topology.links to React Flow Edges
  const initialEdges: Edge[] = useMemo(() => {
    if (!topology || !topology.links) return [];

    return topology.links.map((link, idx) => {
      const isCrossover = link.cable === "cross";
      const edgeId = `edge-${link.a}-${link.b}-${idx}`;

      return {
        id: edgeId,
        source: link.a,
        target: link.b,
        animated: isCrossover,
        style: {
          stroke: isCrossover ? "#f59e0b" : "#38bdf8",
          strokeWidth: 2,
          strokeDasharray: isCrossover ? "5 5" : undefined
        },
        label: `${link.a_port} ↔ ${link.b_port}`,
        labelStyle: { fill: "#94a3b8", fontSize: 10, fontFamily: "monospace", fontWeight: 600 },
        labelBgStyle: { fill: "#0f172a", fillOpacity: 0.85, stroke: "#334155", strokeWidth: 1 },
        labelBgPadding: [6, 3] as [number, number],
        labelBgBorderRadius: 4,
        markerEnd: {
          type: MarkerType.ArrowClosed,
          width: 12,
          height: 12,
          color: isCrossover ? "#f59e0b" : "#38bdf8"
        }
      };
    });
  }, [topology]);

  const [nodes, setNodes] = useNodesState(initialNodes);
  const [edges, setEdges] = useEdgesState(initialEdges);

  // Sync state when topology changes
  React.useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  // Handle node drag end to update parent topology
  const onNodeDragStop = useCallback(
    (_: any, node: Node) => {
      if (onUpdateCoordinates) {
        onUpdateCoordinates(node.id, Math.round(node.position.x), Math.round(node.position.y));
      }
    },
    [onUpdateCoordinates]
  );

  const onNodesChangeInternal = useCallback(
    (changes: NodeChange[]) => {
      setNodes((nds) => applyNodeChanges(changes, nds));
    },
    [setNodes]
  );

  if (!topology || !topology.devices || topology.devices.length === 0) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center bg-slate-950 text-slate-400 p-8 text-center border-x border-slate-800">
        <div className="w-16 h-16 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center mb-4 text-sky-400 shadow-xl shadow-sky-500/5">
          <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
          </svg>
        </div>
        <h3 className="text-base font-semibold text-slate-200 mb-1">Interactive Topology Canvas</h3>
        <p className="text-sm max-w-sm text-slate-500">
          Ask Gemma to build a network in the chat or select a template to visualize devices, interfaces, and cabling in real-time.
        </p>
      </div>
    );
  }

  return (
    <div className="w-full h-full bg-slate-950 relative border-x border-slate-800/80">
      {/* Top Banner showing Topology Name and Stats */}
      <div className="absolute top-3 left-4 z-10 flex items-center space-x-2 bg-slate-900/90 backdrop-blur border border-slate-800 px-3 py-1.5 rounded-lg shadow-lg">
        <span className="w-2 h-2 rounded-full bg-sky-400 animate-pulse"></span>
        <span className="text-xs font-mono font-bold text-slate-200">{topology.name}</span>
        <span className="text-[11px] text-slate-400 border-l border-slate-700 pl-2">
          {topology.devices.length} Devices · {topology.links.length} Links
        </span>
        {topology.routing?.protocol !== "none" && (
          <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-sky-950 text-sky-400 border border-sky-800">
            {topology.routing.protocol}
          </span>
        )}
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChangeInternal}
        onNodeDragStop={onNodeDragStop}
        connectionLineType={ConnectionLineType.SmoothStep}
        fitView
        attributionPosition="bottom-right"
        className="bg-slate-950"
      >
        <Background color="#1e293b" gap={20} size={1} />
        <Controls className="!bg-slate-900 !border-slate-800 !text-slate-200 !shadow-xl [&>button]:!bg-slate-900 [&>button]:!border-slate-800 [&>button:hover]:!bg-slate-800 [&>button]:!fill-slate-300" />
        <MiniMap
          nodeColor={(n) => {
            const d = n.data as NetworkNodeData;
            if (d.type === "router") return "#0284c7";
            if (d.type === "switch") return "#0d9488";
            if (d.type === "server") return "#d97706";
            return "#4f46e5";
          }}
          className="!bg-slate-900/90 !border-slate-800 !rounded-lg"
          maskColor="rgba(15, 23, 42, 0.7)"
        />
      </ReactFlow>
    </div>
  );
};
