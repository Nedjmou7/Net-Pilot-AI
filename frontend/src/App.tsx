import React, { useState, useEffect, useCallback } from "react";
import { Header } from "./components/Header";
import { Sidebar } from "./components/Sidebar";
import { ChatPanel, MessageItem } from "./components/ChatPanel";
import { TopologyCanvas } from "./components/TopologyCanvas";
import { ArtifactsPanel } from "./components/ArtifactsPanel";
import {
  Topology, ValidationResult, HealthResponse, ProjectItem
} from "./types/topology";
import {
  checkHealth, sendChatMessage, generateArtifacts, validateTopology,
  fetchProjects, saveProject, fetchProject, pushToPacketTracer,
  USE_MOCK, setUseMock
} from "./api/client";
import { SAMPLE_OSPF_TOPOLOGY } from "./api/mock";

export const App: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [useMockState, setUseMockState] = useState<boolean>(USE_MOCK);

  const [projects, setProjects] = useState<ProjectItem[]>([]);
  const [currentProjectId, setCurrentProjectId] = useState<number | null>(null);

  const [topology, setTopology] = useState<Topology | null>(SAMPLE_OSPF_TOPOLOGY);
  const [configs, setConfigs] = useState<Record<string, string>>({});
  const [ptbuilderScript, setPtbuilderScript] = useState<string>("");
  const [validation, setValidation] = useState<ValidationResult>({ errors: [], warnings: [] });

  const [messages, setMessages] = useState<MessageItem[]>([
    {
      id: "welcome-1",
      sender: "gemma",
      content: "Welcome to TopoGemma / Net-Pilot AI! Type a network request (e.g. 'Build 3 routers with OSPF and 2 VLANs') or ask any Cisco CCNA question.",
      timestamp: "Just now"
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [isAssistantVisible, setIsAssistantVisible] = useState(true);
  const [isPushing, setIsPushing] = useState(false);
  const [pushMessage, setPushMessage] = useState<string | null>(null);

  // Initial setup: health & projects
  const refreshHealth = useCallback(async () => {
    const res = await checkHealth();
    setHealth(res);
  }, []);

  const loadProjects = useCallback(async () => {
    const projs = await fetchProjects();
    setProjects(projs);
  }, []);

  // Update artifacts (configs + script) whenever topology changes
  const updateArtifacts = useCallback(async (topo: Topology) => {
    try {
      const art = await generateArtifacts(topo);
      setConfigs(art.cli_configs || {});
      setPtbuilderScript(art.ptbuilder_script || "");
      const val = await validateTopology(topo);
      setValidation(val);
    } catch (err) {
      console.error("Artifact generation error:", err);
    }
  }, []);

  useEffect(() => {
    refreshHealth();
    loadProjects();
    if (topology) {
      updateArtifacts(topology);
    }
  }, [refreshHealth, loadProjects, updateArtifacts]);

  // Handle Send Chat
  const handleSendMessage = async (msg: string) => {
    const userMsg: MessageItem = {
      id: `user-${Date.now()}`,
      sender: "user",
      content: msg,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const resp = await sendChatMessage(msg, currentProjectId || undefined);

      const gemmaMsg: MessageItem = {
        id: `gemma-${Date.now()}`,
        sender: "gemma",
        content: resp.reply,
        intent: resp.intent,
        sources: resp.sources,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      };
      setMessages((prev) => [...prev, gemmaMsg]);

      // If topology returned, update canvas and regenerate artifacts
      if (resp.topology) {
        setTopology(resp.topology);
        setValidation(resp.validation || { errors: [], warnings: [] });
        await updateArtifacts(resp.topology);
      }
    } catch (err: any) {
      const errorMsg: MessageItem = {
        id: `err-${Date.now()}`,
        sender: "gemma",
        content: `Error: ${err.message || "Failed to process request."}`,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  // Node position drag handler
  const handleUpdateCoordinates = (deviceId: string, x: number, y: number) => {
    if (!topology) return;
    const updatedDevices = topology.devices.map((d) =>
      d.id === deviceId ? { ...d, x, y } : d
    );
    const updatedTopo = { ...topology, devices: updatedDevices };
    setTopology(updatedTopo);
    // Refresh generated script positions
    updateArtifacts(updatedTopo);
  };

  // New Project
  const handleNewProject = () => {
    setCurrentProjectId(null);
    setTopology({
      name: "new-network",
      devices: [],
      links: [],
      vlans: [],
      ip_plan: [],
      routing: { protocol: "none" },
      services: { dhcp: [], nat: null, acls: [] }
    });
    setConfigs({});
    setPtbuilderScript("");
    setValidation({ errors: [], warnings: [] });
    setMessages([
      {
        id: `msg-${Date.now()}`,
        sender: "gemma",
        content: "Started a fresh project. What network would you like to build?",
        timestamp: "Just now"
      }
    ]);
  };

  const handleClearChat = () => {
    setMessages([
      {
        id: `msg-${Date.now()}`,
        sender: "gemma",
        content: "Chat cleared. Describe a network to build, or ask a Cisco networking question.",
        timestamp: "Just now"
      }
    ]);
  };

  // Save Project
  const handleSaveProject = async () => {
    if (!topology) return;
    const name = topology.name || `Project ${new Date().toLocaleDateString()}`;
    const res = await saveProject(name, topology);
    if (res?.id) {
      setCurrentProjectId(res.id);
      loadProjects();
    }
  };

  // Select Saved Project
  const handleSelectProject = async (id: number) => {
    setCurrentProjectId(id);
    const proj = await fetchProject(id);
    if (proj?.topology) {
      setTopology(proj.topology);
      updateArtifacts(proj.topology);
      if (proj.messages && proj.messages.length > 0) {
        setMessages(
          proj.messages.map((m) => ({
            id: `db-${m.id}`,
            sender: m.role === "user" ? "user" : "gemma",
            content: m.content,
            intent: m.intent as any,
            timestamp: m.created_at
          }))
        );
      }
    }
  };

  // Load Template
  const handleLoadTemplate = (tmpl: Topology) => {
    setTopology(tmpl);
    updateArtifacts(tmpl);
  };

  // Push to Packet Tracer
  const handlePushToPacketTracer = async () => {
    if (!topology) return;
    setIsPushing(true);
    setPushMessage(null);
    try {
      const res = await pushToPacketTracer(topology);
      setPushMessage(res.message);
    } catch (err: any) {
      setPushMessage(`Push failed: ${err.message}`);
    } finally {
      setIsPushing(false);
      setTimeout(() => setPushMessage(null), 5000);
    }
  };

  // Toggle Mock Mode
  const handleToggleMock = () => {
    const nextVal = !useMockState;
    setUseMockState(nextVal);
    setUseMock(nextVal);
    refreshHealth();
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* Top Header */}
      <Header
        health={health}
        onRefreshHealth={refreshHealth}
        useMock={useMockState}
        onToggleMock={handleToggleMock}
        isAssistantVisible={isAssistantVisible}
        onToggleAssistant={() => setIsAssistantVisible((visible) => !visible)}
      />

      {/* Main Workspace Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Leftmost Sidebar */}
        <Sidebar
          projects={projects}
          currentProjectId={currentProjectId}
          onSelectProject={handleSelectProject}
          onNewProject={handleNewProject}
          onSaveProject={handleSaveProject}
          onLoadTemplate={handleLoadTemplate}
        />

        {/* 3-Panel Central Workspace */}
        <div className="flex flex-1 overflow-hidden">
          {/* Panel 1: Chat (Left - 30% width) */}
          {isAssistantVisible && (
          <div className="w-[30%] min-w-[320px] max-w-[420px] h-full flex flex-col shrink-0">
            <ChatPanel
              messages={messages}
              isLoading={isLoading}
              onSendMessage={handleSendMessage}
              onClearChat={handleClearChat}
            />
          </div>
          )}

          {/* Panel 2: Interactive Topology Diagram (Center - 40% width) */}
          <div className="flex-1 h-full relative overflow-hidden">
            <TopologyCanvas
              topology={topology}
              onUpdateCoordinates={handleUpdateCoordinates}
            />
          </div>

          {/* Panel 3: Generated Artifacts & Validation (Right - 30% width) */}
          <div className="w-[32%] min-w-[340px] max-w-[450px] h-full flex flex-col shrink-0">
            <ArtifactsPanel
              configs={configs}
              ptbuilderScript={ptbuilderScript}
              validation={validation}
              onPushToPacketTracer={handlePushToPacketTracer}
              isPushing={isPushing}
              pushMessage={pushMessage}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
