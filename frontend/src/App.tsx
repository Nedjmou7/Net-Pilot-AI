import React, { useState, useEffect, useCallback } from 'react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { ChatPanel, ChatMessage } from './components/ChatPanel';
import { TopologyDiagram } from './components/TopologyDiagram';
import { OutputPanel } from './components/OutputPanel';

import { Topology, GenerateResponse, ValidationResult, HealthStatus, Project } from './api/types';
import { api } from './api/client';
import { MOCK_TOPOLOGY } from './api/mock';

export const App: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [projects, setProjects] = useState<Project[]>([]);
  const [activeProjectId, setActiveProjectId] = useState<number | null>(null);
  const [projectName, setProjectName] = useState<string>("Untitled Lab");

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const [topology, setTopology] = useState<Topology | null>(MOCK_TOPOLOGY);
  const [generation, setGeneration] = useState<GenerateResponse | null>(null);
  const [validation, setValidation] = useState<ValidationResult | null>(null);

  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);
  const [isPushing, setIsPushing] = useState(false);

  const showToast = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3500);
  };

  // Poll health and load projects on startup
  const fetchHealth = useCallback(async () => {
    const h = await api.getHealth();
    setHealth(h);
  }, []);

  const fetchProjects = useCallback(async () => {
    try {
      const projs = await api.getProjects();
      setProjects(projs);
    } catch (e) {
      console.warn("Could not fetch projects list", e);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
    fetchProjects();
    const interval = setInterval(fetchHealth, 15000);
    return () => clearInterval(interval);
  }, [fetchHealth, fetchProjects]);

  // Generate artifacts and validate whenever topology changes initially
  const processTopology = useCallback(async (topo: Topology) => {
    try {
      const [genRes, valRes] = await Promise.all([
        api.generateArtifacts(topo),
        api.validateTopology(topo)
      ]);
      setGeneration(genRes);
      setValidation(valRes);
    } catch (e: any) {
      showToast(`Artifact generation error: ${e.message}`, 'error');
    }
  }, []);

  useEffect(() => {
    if (topology) {
      processTopology(topology);
    }
  }, [topology, processTopology]);

  // Send Chat Message
  const handleSendMessage = async (userText: string) => {
    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: userText,
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const res = await api.sendMessage(userText, activeProjectId || undefined);

      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: res.reply,
        intent: res.intent,
        sources: res.sources,
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages((prev) => [...prev, assistantMsg]);

      if (res.topology) {
        setTopology(res.topology);
        setProjectName(res.topology.name || "Generated Topology");
        showToast("New topology rendered and validated!", "success");
      }
    } catch (e: any) {
      showToast(`Message failed: ${e.message}`, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  // Update node position on drag
  const handleUpdateDevicePosition = (deviceId: string, x: number, y: number) => {
    if (!topology) return;
    const updatedDevices = topology.devices.map((d) =>
      d.id === deviceId ? { ...d, x, y } : d
    );
    setTopology({ ...topology, devices: updatedDevices });
  };

  // New Project
  const handleNewProject = () => {
    setActiveProjectId(null);
    setProjectName("New Lab");
    setTopology({
      name: "new-lab",
      devices: [],
      links: [],
      vlans: [],
      ip_plan: [],
      routing: { protocol: "none" },
      services: { dhcp: [], nat: null, acls: [] }
    });
    setGeneration(null);
    setValidation(null);
    setMessages([]);
    setSidebarOpen(false);
    showToast("Started a new empty project.", "info");
  };

  // Save Project
  const handleSaveCurrentProject = async (name: string) => {
    if (!topology) return;
    try {
      const saved = await api.saveProject(name, topology);
      setActiveProjectId(saved.id);
      setProjectName(saved.name);
      await fetchProjects();
      showToast(`Project '${saved.name}' saved to SQLite!`, 'success');
    } catch (e: any) {
      showToast(`Failed to save project: ${e.message}`, 'error');
    }
  };

  // Select Saved Project
  const handleSelectProject = async (proj: Project) => {
    try {
      const data = await api.getProject(proj.id);
      const topoObj: Topology = JSON.parse(data.project.topology_json);
      setActiveProjectId(proj.id);
      setProjectName(data.project.name);
      setTopology(topoObj);

      if (data.messages && data.messages.length > 0) {
        setMessages(
          data.messages.map((m: any) => ({
            id: m.id.toString(),
            role: m.role,
            content: m.content,
            intent: m.intent,
            timestamp: m.created_at
          }))
        );
      }
      setSidebarOpen(false);
      showToast(`Loaded '${proj.name}'`, 'info');
    } catch (e: any) {
      showToast(`Failed to load project: ${e.message}`, 'error');
    }
  };

  // Delete Project
  const handleDeleteProject = async (id: number) => {
    try {
      await api.deleteProject(id);
      if (activeProjectId === id) {
        handleNewProject();
      }
      await fetchProjects();
      showToast("Project deleted.", "info");
    } catch (e: any) {
      showToast(`Failed to delete: ${e.message}`, 'error');
    }
  };

  // Load Template
  const handleLoadTemplate = (tpl: string) => {
    handleSendMessage(`Build a network template: ${tpl}`);
    setSidebarOpen(false);
  };

  // Export Topology JSON
  const handleExportJson = () => {
    if (!topology) return;
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(topology, null, 2));
    const a = document.createElement('a');
    a.href = dataStr;
    a.download = `${projectName.toLowerCase().replace(/\s+/g, '-')}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    showToast("Topology JSON exported!", "success");
  };

  // Live Push to Packet Tracer Bridge
  const handlePushToPacketTracer = async () => {
    if (!topology) return;
    setIsPushing(true);
    try {
      const res = await api.pushToPacketTracer(topology);
      if (res.success) {
        showToast(res.message, "success");
      } else {
        showToast(res.message, "info");
      }
    } catch (e: any) {
      showToast(e.message, "error");
    } finally {
      setIsPushing(false);
    }
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-slate-950 text-slate-100">
      {/* Toast Notification Banner */}
      {toast && (
        <div
          className={`fixed top-4 right-4 z-50 px-4 py-2.5 rounded-xl shadow-2xl text-xs font-semibold backdrop-blur border flex items-center gap-2 animate-in fade-in duration-150 ${
            toast.type === 'success'
              ? 'bg-emerald-950/90 text-emerald-300 border-emerald-800'
              : toast.type === 'error'
              ? 'bg-rose-950/90 text-rose-300 border-rose-800'
              : 'bg-cyan-950/90 text-cyan-300 border-cyan-800'
          }`}
        >
          <span>{toast.message}</span>
        </div>
      )}

      {/* Top Header */}
      <Header
        health={health}
        projectName={projectName}
        onRefreshHealth={fetchHealth}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        onExportJson={handleExportJson}
      />

      {/* Slide-out Project Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        projects={projects}
        activeProjectId={activeProjectId}
        onSelectProject={handleSelectProject}
        onNewProject={handleNewProject}
        onSaveCurrentProject={handleSaveCurrentProject}
        onDeleteProject={handleDeleteProject}
        onLoadTemplate={handleLoadTemplate}
      />

      {/* 3-Panel Main Layout (Responsive 1366x768 ready) */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel: Chat (30% width, min 320px) */}
        <div className="w-[32%] min-w-[310px] max-w-[420px] h-full flex-shrink-0">
          <ChatPanel
            messages={messages}
            isLoading={isLoading}
            onSendMessage={handleSendMessage}
            onSelectPromptChip={(prompt) => handleSendMessage(prompt)}
          />
        </div>

        {/* Center Panel: Interactive React Flow Canvas (38% width) */}
        <div className="flex-1 h-full min-w-[360px] relative">
          <TopologyDiagram
            topology={topology}
            onUpdateDevicePosition={handleUpdateDevicePosition}
          />
        </div>

        {/* Right Panel: Output Tabs (Configs, PTBuilder, Validation) (30% width) */}
        <div className="w-[34%] min-w-[340px] max-w-[460px] h-full flex-shrink-0">
          <OutputPanel
            generation={generation}
            validation={validation}
            topology={topology}
            onPushToPacketTracer={handlePushToPacketTracer}
            isPushing={isPushing}
          />
        </div>
      </div>
    </div>
  );
};

export default App;
