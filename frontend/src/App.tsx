import React, { useCallback, useEffect, useState } from 'react';
import {
  Bot, Check, ChevronDown, Code2, Copy, Download, FileCode2, LayoutGrid,
  Network, PanelLeftClose, PanelLeftOpen, Radio, Send, ShieldCheck, Terminal, Trash2, Waypoints, X
} from 'lucide-react';
import { ChatPanel, ChatMessage } from './components/ChatPanel';
import { TopologyDiagram } from './components/TopologyDiagram';
import { WorkspaceSidebar } from './components/WorkspaceSidebar';
import { Topology, GenerateResponse, ValidationResult, HealthStatus, Project, DeviceType, Link } from './api/types';
import { api } from './api/client';
import { MOCK_TOPOLOGY } from './api/mock';

type WorkspaceTab = 'chat' | 'configs' | 'script' | 'topology';

const asChatMessages = (items: any[]): ChatMessage[] => items.map((item, index) => ({
  id: String(item.id ?? index),
  role: item.role === 'user' ? 'user' : 'assistant',
  content: String(item.content ?? ''),
  intent: item.intent,
  sources: item.sources ?? [],
  timestamp: item.created_at ? new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''
}));

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<WorkspaceTab>('chat');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [activeProject, setActiveProject] = useState<Project | null>(null);
  const [topology, setTopology] = useState<Topology | null>(MOCK_TOPOLOGY);
  const [generation, setGeneration] = useState<GenerateResponse | null>(null);
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isPushing, setIsPushing] = useState(false);
  const [selectedDevice, setSelectedDevice] = useState('');
  const [copied, setCopied] = useState(false);
  const [dialog, setDialog] = useState<'settings' | 'help' | null>(null);
  const [selectedDeviceIds, setSelectedDeviceIds] = useState<string[]>([]);
  const [connectionMode, setConnectionMode] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);

  const showToast = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    setToast({ message, type });
    window.setTimeout(() => setToast(null), 3500);
  };

  const refreshProjects = useCallback(async () => {
    try { setProjects(await api.getProjects()); } catch { /* Keep the workspace available when history is offline. */ }
  }, []);

  useEffect(() => {
    let mounted = true;
    const fetchStatus = async () => {
      try { const status = await api.getHealth(); if (mounted) setHealth(status); } catch { /* status indicator stays in its ready state */ }
    };
    fetchStatus();
    refreshProjects();
    const interval = window.setInterval(fetchStatus, 20000);
    return () => { mounted = false; window.clearInterval(interval); };
  }, [refreshProjects]);

  const processTopology = useCallback(async (nextTopology: Topology) => {
    try {
      const [artifacts, result] = await Promise.all([
        api.generateArtifacts(nextTopology),
        api.validateTopology(nextTopology)
      ]);
      setGeneration(artifacts);
      setValidation(result);
      const firstDevice = Object.keys(artifacts.cli_configs)[0];
      if (firstDevice) setSelectedDevice(firstDevice);
    } catch (error) { console.warn('Could not prepare network artifacts', error); }
  }, []);

  useEffect(() => { if (topology) processTopology(topology); }, [topology, processTopology]);

  const activeProjectId = activeProject?.id;
  const activeProjectName = activeProject?.name;
  useEffect(() => {
    if (!activeProjectId || !activeProjectName || !topology) return;
    const timeout = window.setTimeout(async () => {
      try {
        const updated = await api.updateProject(activeProjectId, activeProjectName, topology);
        setActiveProject(updated);
        setProjects((current) => [updated, ...current.filter((project) => project.id !== updated.id)]);
      } catch (error) { console.warn('Could not update saved lab topology', error); }
    }, 700);
    return () => window.clearTimeout(timeout);
  }, [activeProjectId, activeProjectName, topology]);

  const handleNewChat = () => {
    setActiveProject(null);
    setMessages([]);
    setTopology(MOCK_TOPOLOGY);
    setActiveTab('chat');
  };

  const handleSelectProject = async (project: Project) => {
    try {
      const saved = await api.getProject(project.id);
      const restored = JSON.parse(saved.project.topology_json) as Topology;
      setActiveProject(saved.project);
      setTopology(restored);
      setMessages(asChatMessages(saved.messages ?? []));
      setActiveTab('chat');
    } catch (error: any) { showToast(`Could not open lab: ${error.message}`, 'error'); }
  };

  const handleDeleteProject = async (project: Project) => {
    try {
      await api.deleteProject(project.id);
      setProjects((current) => current.filter((item) => item.id !== project.id));
      if (activeProject?.id === project.id) handleNewChat();
      showToast('Lab removed from history', 'success');
    } catch (error: any) { showToast(`Could not remove lab: ${error.message}`, 'error'); }
  };

  const handleSendMessage = async (userText: string) => {
    const prompt = userText.trim();
    if (!prompt || isLoading) return;
    const userMessage: ChatMessage = {
      id: `${Date.now()}`,
      role: 'user',
      content: prompt,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages((current) => [...current, userMessage]);
    setIsLoading(true);

    try {
      let projectId = activeProject?.id;
      if (!projectId && topology) {
        try {
          const title = prompt.length > 42 ? `${prompt.slice(0, 42).trim()}…` : prompt;
          const created = await api.saveProject(title, topology);
          setActiveProject(created);
          setProjects((current) => [created, ...current]);
          projectId = created.id;
        } catch (error) { console.warn('Could not save lab history', error); }
      }

      const response = await api.sendMessage(prompt, projectId);
      const assistantMessage: ChatMessage = {
        id: `${Date.now()}-assistant`, role: 'assistant', content: response.reply,
        intent: response.intent, sources: response.sources, timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((current) => [...current, assistantMessage]);
      if (response.topology) {
        setTopology(response.topology);
        setValidation(response.validation);
      }
    } catch (error: any) {
      showToast(`Agent error: ${error.message}`, 'error');
    } finally { setIsLoading(false); }
  };

  const handleUpdateDevicePosition = (deviceId: string, x: number, y: number) => {
    if (!topology) return;
    setTopology({ ...topology, devices: topology.devices.map((device) => device.id === deviceId ? { ...device, x, y } : device) });
  };

  const handleAddDevice = (type: DeviceType, model: string) => {
    if (!topology) return;
    const prefixes: Record<DeviceType, string> = { router: 'R', switch: 'SW', pc: 'PC', server: 'Server' };
    const prefix = prefixes[type];
    const used = topology.devices.map((device) => device.id);
    let index = 1;
    while (used.includes(`${prefix}${index}`)) index += 1;
    const positionIndex = topology.devices.length;
    const device = { id: `${prefix}${index}`, type, model, x: 120 + (positionIndex % 4) * 170, y: 90 + Math.floor(positionIndex / 4) * 140 };
    setTopology({ ...topology, devices: [...topology.devices, device] });
    showToast(`${device.id} added to the topology`, 'success');
  };

  const handleAddConnection = (sourceId: string, targetId: string, cable: Link['cable']) => {
    const reject = (message: string) => { showToast(message, 'error'); return message; };
    if (!topology || sourceId === targetId) return reject('Choose two different devices.');
    const exists = topology.links.some((link) => (link.a === sourceId && link.b === targetId) || (link.a === targetId && link.b === sourceId));
    if (exists) return reject('Those devices are already connected.');
    const source = topology.devices.find((device) => device.id === sourceId);
    const target = topology.devices.find((device) => device.id === targetId);
    if (!source || !target) return reject('A selected device is no longer in this topology.');
    const usedPort = (deviceId: string, type: DeviceType) => topology.links.filter((link) => link.a === deviceId || link.b === deviceId).length;
    const portFor = (deviceId: string, type: DeviceType) => {
      const used = usedPort(deviceId, type);
      if (type === 'pc' || type === 'server') return used ? null : 'FastEthernet0';
      return type === 'router' ? `GigabitEthernet0/${used}` : `FastEthernet0/${used + 1}`;
    };
    const sourcePort = portFor(sourceId, source.type);
    const targetPort = portFor(targetId, target.type);
    if (!sourcePort || !targetPort) return reject('That endpoint has no free network port.');
    const link: Link = { a: sourceId, a_port: sourcePort, b: targetId, b_port: targetPort, cable };
    setTopology({ ...topology, links: [...topology.links, link] });
    showToast(`${sourceId} connected to ${targetId}`, 'success');
    return null;
  };

  const handleDeleteDevices = (ids: string[]) => {
    if (!topology || !ids.length) return;
    setTopology({ ...topology, devices: topology.devices.filter((device) => !ids.includes(device.id)), links: topology.links.filter((link) => !ids.includes(link.a) && !ids.includes(link.b)) });
    showToast(`${ids.length} device${ids.length === 1 ? '' : 's'} removed`, 'info');
  };

  const handleDeleteConnection = (sourceId: string, targetId: string) => {
    if (!topology) return;
    setTopology({ ...topology, links: topology.links.filter((link) => !((link.a === sourceId && link.b === targetId) || (link.a === targetId && link.b === sourceId))) });
  };

  const handleSetConnectionMode = (enabled: boolean) => setConnectionMode(enabled);

  const handleExportJson = () => {
    if (!topology) return;
    const link = document.createElement('a');
    link.href = `data:text/json;charset=utf-8,${encodeURIComponent(JSON.stringify(topology, null, 2))}`;
    link.download = `${topology.name || 'packet-tracer-lab'}.json`;
    link.click();
  };

  const handlePushToPacketTracer = async () => {
    if (!topology) return;
    setIsPushing(true);
    try { const response = await api.pushToPacketTracer(topology); showToast(response.message, response.success ? 'success' : 'info'); }
    catch (error: any) { showToast(error.message, 'error'); }
    finally { setIsPushing(false); }
  };

  const handleCopy = async (text: string) => {
    try { await navigator.clipboard.writeText(text); setCopied(true); window.setTimeout(() => setCopied(false), 1600); }
    catch { showToast('Clipboard access is unavailable', 'error'); }
  };

  const handleDownloadScript = () => {
    if (!generation?.ptbuilder_script) return;
    const blob = new Blob([generation.ptbuilder_script], { type: 'text/javascript' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a'); link.href = url; link.download = `${topology?.name || 'packet-tracer-lab'}_ptbuilder.js`; link.click(); URL.revokeObjectURL(url);
  };

  const navItems: { id: WorkspaceTab; label: string; icon: React.ElementType }[] = [
    { id: 'chat', label: 'Chat', icon: Bot },
    { id: 'configs', label: 'IOS Config', icon: Terminal },
    { id: 'script', label: 'PTBuilder', icon: FileCode2 },
    { id: 'topology', label: 'Topology', icon: Waypoints }
  ];
  const configDevices = Object.keys(generation?.cli_configs ?? {});
  const activeConfig = selectedDevice || configDevices[0] || '';
  const agentOnline = health?.ollama?.ollama_connected ?? false;

  return (
    <div className={`agent-app ${sidebarOpen ? '' : 'sidebar-closed'}`}>
      {toast && <div className={`workspace-toast ${toast.type}`}>{toast.message}</div>}
      <WorkspaceSidebar
        projects={projects}
        activeProjectId={activeProject?.id ?? null}
        onNewChat={handleNewChat}
        onSelectProject={handleSelectProject}
        onDeleteProject={handleDeleteProject}
        onOpenSettings={() => setDialog('settings')}
        onOpenHelp={() => setDialog('help')}
      />

      <main className="agent-main">
        <header className="agent-topbar">
          <div className="agent-topbar-leading">
            <button className="sidebar-toggle" onClick={() => setSidebarOpen((open) => !open)} aria-label={sidebarOpen ? 'Close left sidebar' : 'Open left sidebar'} aria-expanded={sidebarOpen} aria-controls="workspace-sidebar" title={sidebarOpen ? 'Close sidebar' : 'Open sidebar'}>
              {sidebarOpen ? <PanelLeftClose className="h-[18px] w-[18px]" /> : <PanelLeftOpen className="h-[18px] w-[18px]" />}
            </button>
            <div className="flex min-w-0 items-center gap-2 text-xs text-slate-500">
            <span>Workspace</span><span className="text-slate-300">/</span>
            <span className="truncate font-medium text-slate-700">{activeProject?.name || 'New network lab'}</span>
            {activeProject && <span className="hidden sm:inline-flex rounded-full bg-slate-100 px-2 py-0.5 text-[10px]">Saved</span>}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className={`agent-top-status ${agentOnline ? 'connected' : ''}`}><span />{agentOnline ? 'Agent online' : 'Agent ready'}</span>
            <button className="topbar-menu" aria-label="Workspace info" title="Workspace info" onClick={() => setDialog('settings')}><LayoutGrid className="h-4 w-4" /><ChevronDown className="h-3 w-3" /></button>
          </div>
        </header>

        <nav className="workspace-tabs" aria-label="Lab workspace">
          {navItems.map(({ id, label, icon: Icon }) => <button key={id} onClick={() => setActiveTab(id)} className={`workspace-tab ${activeTab === id ? 'active' : ''}`}>
            <Icon className="h-4 w-4" /><span>{label}</span>
            {id === 'configs' && validation && <span className={`tab-indicator ${validation.is_valid ? 'valid' : 'invalid'}`} />}
          </button>)}
          <div className="workspace-tab-spacer" />
          <button onClick={handleExportJson} className="workspace-export"><Download className="h-3.5 w-3.5" /><span>Export lab</span></button>
        </nav>

        <section className={`workspace-content ${activeTab === 'topology' ? 'topology-content' : ''}`}>
          {activeTab === 'chat' && <div className="chat-workspace">
            <div className="chat-welcome-strip"><span className="welcome-icon"><Bot className="h-5 w-5" /></span><div><div className="font-semibold text-slate-800">Your network design agent</div><div className="text-xs text-slate-500">Describe a Cisco lab. I’ll build the topology and prepare IOS configurations and a PTBuilder script.</div></div><span className="hidden lg:inline-flex welcome-tag"><Radio className="h-3 w-3" />PACKET TRACER READY</span></div>
            <ChatPanel messages={messages} isLoading={isLoading} onSendMessage={handleSendMessage} onSelectPromptChip={handleSendMessage} />
          </div>}

          {activeTab === 'configs' && <div className="artifact-workspace">
            <div className="artifact-heading"><div className="artifact-heading-icon"><Terminal className="h-5 w-5" /></div><div><h1>IOS configuration</h1><p>Device configurations generated from the current network topology.</p></div><span className={`validation-pill ${validation?.is_valid ? 'valid' : 'pending'}`}><ShieldCheck className="h-3.5 w-3.5" />{validation?.is_valid ? 'Topology validated' : 'Review validation'}</span></div>
            {configDevices.length ? <><div className="artifact-toolbar"><div className="device-tabs">{configDevices.map((device) => <button key={device} onClick={() => setSelectedDevice(device)} className={device === activeConfig ? 'active' : ''}>{device}</button>)}</div><button className="artifact-action" onClick={() => handleCopy(generation?.cli_configs[activeConfig] ?? '')}>{copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}{copied ? 'Copied' : 'Copy config'}</button></div><pre className="code-view"><div className="code-caption"><span className="code-light" /><span className="code-light" /><span className="code-light" />{activeConfig} · Cisco IOS CLI</div><code>{generation?.cli_configs[activeConfig]}</code></pre></> : <div className="artifact-empty"><Terminal className="h-8 w-8" /><strong>No IOS configuration yet</strong><span>Ask the agent to design a network topology first.</span><button onClick={() => setActiveTab('chat')}>Start a chat</button></div>}
          </div>}

          {activeTab === 'script' && <div className="artifact-workspace">
            <div className="artifact-heading"><div className="artifact-heading-icon"><Code2 className="h-5 w-5" /></div><div><h1>PTBuilder script</h1><p>Use the generated script to recreate this lab in Cisco Packet Tracer.</p></div><span className="ptbuilder-badge"><Network className="h-3.5 w-3.5" />PTBUILDER</span></div>
            {generation?.ptbuilder_script ? <><div className="artifact-toolbar"><span className="text-xs text-slate-500">JavaScript · {topology?.name || 'Network lab'}</span><div className="flex gap-2"><button className="artifact-action" onClick={() => handleCopy(generation.ptbuilder_script)}>{copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}{copied ? 'Copied' : 'Copy'}</button><button className="artifact-action primary" onClick={handleDownloadScript}><Download className="h-3.5 w-3.5" />Download .js</button><button className="artifact-action push" onClick={handlePushToPacketTracer} disabled={isPushing}><Send className="h-3.5 w-3.5" />{isPushing ? 'Sending…' : 'Send to Packet Tracer'}</button></div></div><pre className="code-view script-code"><div className="code-caption"><span className="code-light" /><span className="code-light" /><span className="code-light" />{topology?.name || 'network-lab'}_ptbuilder.js</div><code>{generation.ptbuilder_script}</code></pre></> : <div className="artifact-empty"><FileCode2 className="h-8 w-8" /><strong>No PTBuilder script yet</strong><span>Ask the agent to build a lab to generate a Packet Tracer script.</span><button onClick={() => setActiveTab('chat')}>Start a chat</button></div>}
          </div>}

          {activeTab === 'topology' && <div className="topology-workspace">
            <div className="topology-summary"><div><h1>{topology?.name || 'Network topology'}</h1><p>Packet Tracer logical workspace <span>·</span> {topology?.devices.length ?? 0} devices <span>·</span> {topology?.links.length ?? 0} connections</p></div><div className="topology-summary-actions"><span className={`validation-pill ${validation?.is_valid ? 'valid' : 'pending'}`}><ShieldCheck className="h-3.5 w-3.5" />{validation?.is_valid ? 'Valid topology' : 'Validation pending'}</span><button className="artifact-action push" onClick={handlePushToPacketTracer} disabled={isPushing}><Send className="h-3.5 w-3.5" />{isPushing ? 'Sending…' : 'Open in Packet Tracer'}</button></div></div>
            <div className="packet-tracer-window"><div className="pt-app-menubar"><div className="pt-app-brand"><Network className="h-4 w-4" /><span>Cisco Packet Tracer</span></div><div className="pt-menubar-items"><span>File</span><span>Edit</span><span>Options</span><span>View</span><span>Tools</span><span>Extensions</span><span>Window</span><span>Help</span></div><span className="pt-lab-title">{topology?.name || 'Network lab'}</span></div><div className="pt-toolbar"><button className={`pt-tool ${connectionMode ? '' : 'active'}`} title="Select and move devices" onClick={() => handleSetConnectionMode(false)}><Network /></button><button className={`pt-tool ${connectionMode ? 'active' : ''}`} title="Connect devices" onClick={() => handleSetConnectionMode(!connectionMode)}><Waypoints /></button><span className="pt-toolbar-divider" /><button className="pt-tool" title="Delete selected devices" disabled={!selectedDeviceIds.length} onClick={() => handleDeleteDevices(selectedDeviceIds)}><Trash2 /></button><span className="pt-toolbar-divider" /><button className="pt-tool" title="Export topology JSON" onClick={handleExportJson}><Download /></button><span className="pt-toolbar-hint">Logical workspace</span><span className="pt-realtime"><span />Realtime</span><span className="pt-simulation">Simulation</span></div>
              <div className="pt-canvas-wrap"><div className="pt-canvas-rail"><span className="pt-rail-active"><Network /></span><span><Waypoints /></span><span><LayoutGrid /></span><span><ShieldCheck /></span></div><div className="pt-topology-canvas"><TopologyDiagram topology={topology} onUpdateDevicePosition={handleUpdateDevicePosition} onAddDevice={handleAddDevice} onAddConnection={handleAddConnection} onDeleteDevices={handleDeleteDevices} onDeleteConnection={handleDeleteConnection} onSelectionChange={setSelectedDeviceIds} connectionMode={connectionMode} onSetConnectionMode={handleSetConnectionMode} /></div></div>
            </div>
          </div>}
        </section>

        <footer className="workspace-footer"><span><span className="footer-dot" />Local AI workspace</span><span><Network className="h-3.5 w-3.5" />Cisco Packet Tracer lab assistant</span></footer>
      </main>
      {dialog && <div className="workspace-dialog-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) setDialog(null); }}><section className="workspace-dialog" role="dialog" aria-modal="true" aria-labelledby="workspace-dialog-title"><button className="workspace-dialog-close" onClick={() => setDialog(null)} aria-label="Close dialog"><X className="h-4 w-4" /></button><div className="workspace-dialog-icon">{dialog === 'help' ? <ShieldCheck className="h-5 w-5" /> : <LayoutGrid className="h-5 w-5" />}</div><h2 id="workspace-dialog-title">{dialog === 'help' ? 'Using NetPilot AI' : 'Workspace info'}</h2>{dialog === 'help' ? <div className="dialog-copy"><p>Describe the network you want in <strong>Chat</strong>. The agent can create a topology and prepare device configurations.</p><p>Review each device under <strong>IOS Config</strong>, export a <strong>PTBuilder</strong> script, or arrange devices and cables in <strong>Topology</strong>.</p><p>Use the history list to reopen a saved lab. Drag devices to arrange them, or use the device palette to add network equipment.</p></div> : <div className="dialog-copy"><p><strong>Theme</strong><span>Light workspace</span></p><p><strong>Agent</strong><span>{agentOnline ? 'Connected' : 'Ready'} · {health?.ollama?.model ?? 'Local network assistant'}</span></p><p><strong>Current lab</strong><span>{activeProject?.name || 'Unsaved network lab'}</span></p></div>}<button className="dialog-done" onClick={() => setDialog(null)}>Done</button></section></div>}
    </div>
  );
};

export default App;
