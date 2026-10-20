import React, { useCallback, useMemo } from 'react';
import ReactFlow, {
  Node, Edge, Background, BackgroundVariant, useNodesState, useEdgesState,
  useReactFlow, ReactFlowProvider, Connection, OnSelectionChangeParams
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Topology, DeviceType, Link } from '../api/types';
import { nodeTypes } from './CustomNodes';
import { Bot, LayoutGrid, Minus, Network, Plus, Radio, Scan, Trash2, Waypoints } from 'lucide-react';

interface TopologyDiagramProps {
  topology: Topology | null;
  onUpdateDevicePosition: (deviceId: string, x: number, y: number) => void;
  onAddDevice: (type: DeviceType, model: string) => void;
  onAddConnection: (sourceId: string, targetId: string, cable: Link['cable']) => string | null;
  onDeleteDevices: (ids: string[]) => void;
  onDeleteConnection: (sourceId: string, targetId: string) => void;
  onSelectionChange: (ids: string[]) => void;
  connectionMode: boolean;
  onSetConnectionMode: (enabled: boolean) => void;
}

const interfaceName = (name: string) => name.replace('GigabitEthernet', 'G').replace('FastEthernet', 'Fa').replace('Serial', 'S');
const linkHandles = (topology: Topology | null, a: string, b: string) => {
  const source = topology?.devices.find((device) => device.id === a);
  const target = topology?.devices.find((device) => device.id === b);
  const dx = (target?.x ?? 0) - (source?.x ?? 0);
  const dy = (target?.y ?? 0) - (source?.y ?? 0);
  if (Math.abs(dx) >= Math.abs(dy)) return dx >= 0 ? ['source-right', 'target-left'] : ['source-left', 'target-right'];
  return dy >= 0 ? ['source-bottom', 'target-top'] : ['source-top', 'target-bottom'];
};

const FlowCanvas: React.FC<TopologyDiagramProps> = ({ topology, onUpdateDevicePosition, onAddDevice, onAddConnection, onDeleteDevices, onDeleteConnection, onSelectionChange, connectionMode, onSetConnectionMode }) => {
  const { zoomIn, zoomOut, fitView } = useReactFlow();
  const [category, setCategory] = React.useState<'network' | 'end' | 'components' | 'connections' | 'multiuser'>('network');
  const [group, setGroup] = React.useState('Routers');
  const [cable, setCable] = React.useState<Link['cable']>('auto');
  const nodes = useMemo<Node[]>(() => (topology?.devices ?? []).map((device) => ({
    id: device.id,
    type: 'networkDevice',
    position: { x: device.x, y: device.y },
    data: { id: device.id, label: device.id.toUpperCase(), type: device.type, model: device.model }
  })), [topology]);
  const edges = useMemo<Edge[]>(() => (topology?.links ?? []).map((link, index) => {
    const [sourceHandle, targetHandle] = linkHandles(topology, link.a, link.b);
    return {
    id: `link-${link.a}-${link.b}-${index}`,
    source: link.a,
    target: link.b,
    sourceHandle,
    targetHandle,
    label: `${interfaceName(link.a_port)} ↔ ${interfaceName(link.b_port)}`,
    labelStyle: { fill: '#425968', fontSize: 9, fontFamily: 'Arial, sans-serif', fontWeight: 600 },
    labelBgStyle: { fill: '#f8fafc', fillOpacity: 0.96 },
    labelBgPadding: [5, 2] as [number, number],
    labelBgBorderRadius: 3,
    style: {
      stroke: link.cable === 'crossover' ? '#aa7851' : link.cable === 'fiber' ? '#8970a7' : link.cable === 'serial' ? '#b46b6b' : '#536d7c',
      strokeWidth: link.cable === 'fiber' ? 3 : 2.5,
      strokeDasharray: link.cable === 'crossover' ? '5 3' : undefined
    }
  };}), [topology]);

  const [flowNodes, setNodes, onNodesChange] = useNodesState(nodes);
  const [flowEdges, setEdges, onEdgesChange] = useEdgesState(edges);
  React.useEffect(() => setNodes(nodes), [nodes, setNodes]);
  React.useEffect(() => setEdges(edges), [edges, setEdges]);

  const handleNodeDragStop = useCallback((_: React.MouseEvent, node: Node) => {
    onUpdateDevicePosition(node.id, Math.round(node.position.x), Math.round(node.position.y));
  }, [onUpdateDevicePosition]);

  const handleConnect = useCallback((connection: Connection) => {
    if (!connection.source || !connection.target) return;
    const error = onAddConnection(connection.source, connection.target, cable);
    if (error) return;
  }, [cable, onAddConnection]);

  const handleDeleteEdges = useCallback((deleted: Edge[]) => {
    deleted.forEach((edge) => { if (edge.source && edge.target) onDeleteConnection(edge.source, edge.target); });
  }, [onDeleteConnection]);

  const selectedIds = flowNodes.filter((node) => node.selected).map((node) => node.id);
  const deviceGroups = category === 'network' ? ['Routers', 'Switches', 'Hubs', 'Wireless', 'Security', 'WAN'] : ['End Devices', 'Home Devices'];
  const models: { type: DeviceType; model: string; label: string }[] = category === 'network' && group === 'Routers'
    ? [['router','2911','Cisco 2911 Router'],['router','1941','Cisco 1941 Router'],['router','4321','Cisco 4321 Router'],['router','2901','Cisco 2901 Router']].map(([type,model,label]) => ({ type: type as DeviceType, model, label }))
    : category === 'network' && group === 'Switches'
    ? [['switch','2960-24TT','Cisco 2960-24TT'],['switch','3560-24PS','Cisco 3560-24PS'],['switch','3650-24PS','Cisco 3650-24PS']].map(([type,model,label]) => ({ type: type as DeviceType, model, label }))
    : category === 'end' && group === 'End Devices'
    ? [['pc','PC-PT','PC-PT'],['pc','Laptop-PT','Laptop-PT'],['server','Server-PT','Server-PT']].map(([type,model,label]) => ({ type: type as DeviceType, model, label }))
    : category === 'end'
    ? [['pc','Home-PC-PT','Home PC'],['server','Printer-PT','Printer-PT'],['server','TV-PT','TV-PT']].map(([type,model,label]) => ({ type: type as DeviceType, model, label }))
    : [];

  const addSelection = () => {
    if (!selectedIds.length) return;
    onDeleteDevices(selectedIds);
  };

  return <div className="topology-panel h-full w-full overflow-hidden rounded-lg border border-slate-200 bg-white flex flex-col">
    <div className="pt-canvas-heading"><div><strong>Logical workspace</strong><span>{topology?.devices.length ?? 0} devices · {topology?.links.length ?? 0} connections</span></div><div className="pt-canvas-legend"><span><i className="router-legend" />Router / endpoint</span><span><i className="switch-legend" />Switch</span><span><i className="cable-legend" />Cable</span></div><button className="pt-delete-selected" title="Delete selected devices" disabled={!selectedIds.length} onClick={addSelection}><Trash2 className="h-3.5 w-3.5" />Delete selected</button></div>
    <div className={`relative min-h-0 flex-1 ${connectionMode ? 'connection-active' : ''}`}>
      <ReactFlow nodes={flowNodes} edges={flowEdges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} onNodeDragStop={handleNodeDragStop} onConnect={handleConnect} onNodesDelete={(deleted) => onDeleteDevices(deleted.map((node) => node.id))} onEdgesDelete={handleDeleteEdges} onSelectionChange={({ nodes: selected }: OnSelectionChangeParams) => onSelectionChange(selected.map((node) => node.id))} nodesConnectable={connectionMode} nodeTypes={nodeTypes} fitView fitViewOptions={{ padding: 0.16 }} minZoom={0.2} maxZoom={2} className="pt-reactflow" proOptions={{ hideAttribution: true }}>
        <Background color="#d5dfe5" gap={22} size={1} variant={BackgroundVariant.Dots} />
      </ReactFlow>
      {connectionMode && <div className="pt-connection-hint">Drag from one device port to another to add a cable</div>}
      <div className="pt-zoom-controls"><button onClick={() => zoomOut()} aria-label="Zoom out"><Minus className="h-3.5 w-3.5" /></button><span>Zoom</span><button onClick={() => zoomIn()} aria-label="Zoom in"><Plus className="h-3.5 w-3.5" /></button><button onClick={() => fitView({ padding: 0.16, duration: 220 })} aria-label="Fit all devices"><Scan className="h-3.5 w-3.5" /></button></div>
    </div>
    <div className="pt-device-panel"><div className="pt-device-categories">
      <button className={category === 'network' ? 'selected' : ''} onClick={() => { setCategory('network'); setGroup('Routers'); onSetConnectionMode(false); }}><Network />Network Devices</button>
      <button className={category === 'end' ? 'selected' : ''} onClick={() => { setCategory('end'); setGroup('End Devices'); onSetConnectionMode(false); }}><Bot />End Devices</button>
      <button className={category === 'components' ? 'selected' : ''} onClick={() => { setCategory('components'); onSetConnectionMode(false); }}><LayoutGrid />Components</button>
      <button className={category === 'connections' ? 'selected' : ''} onClick={() => { setCategory('connections'); onSetConnectionMode(true); }}><Waypoints />Connections</button>
      <button className={category === 'multiuser' ? 'selected' : ''} onClick={() => { setCategory('multiuser'); onSetConnectionMode(false); }}><Radio />Multiuser</button>
    </div>
      {category === 'network' || category === 'end' ? <div className="pt-device-models"><div className="pt-model-groups">{deviceGroups.map((name) => <button key={name} className={group === name ? 'selected' : ''} onClick={() => setGroup(name)}>{name}</button>)}</div><div className="pt-model-list">{models.length ? models.map(({ type, model, label }) => <button key={model} className="pt-model-card" onClick={() => onAddDevice(type, model)} title={`Add ${label}`}><span className={`mini-device ${type}`}><i /><i /><i /><i /></span><span>{label}</span></button>) : <div className="pt-palette-note">{group} models are not available in this lab builder yet.</div>}</div></div>
      : category === 'connections' ? <div className="pt-cable-list">{([['auto','Automatically Choose Connection'],['straight','Copper Straight-Through'],['crossover','Copper Cross-Over'],['fiber','Fiber'],['serial','Serial DCE'] ] as [Link['cable'],string][]).map(([kind,label]) => <button key={kind} className={cable === kind ? 'selected' : ''} onClick={() => { setCable(kind); onSetConnectionMode(true); }}><span className={`cable-swatch ${kind}`} />{label}</button>)}<span className="pt-palette-note">Choose a cable, then drag between device ports.</span></div>
      : <div className="pt-palette-note category-note">{category === 'components' ? 'No additional component models are available in this topology.' : 'Multiuser connections require an active Packet Tracer session.'}</div>}
      <div className="pt-device-status"><span>{category === 'connections' ? `Cable: ${cable}` : category === 'network' || category === 'end' ? 'Click a device to add it to the workspace' : 'Packet Tracer workspace'}</span><span>{topology?.devices.length ?? 0} devices on canvas</span></div>
    </div>
  </div>;
};

export const TopologyDiagram: React.FC<TopologyDiagramProps> = (props) => <ReactFlowProvider><FlowCanvas {...props} /></ReactFlowProvider>;
