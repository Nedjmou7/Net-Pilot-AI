import {
  Topology, ChatResponse, ValidationResult, GenerateResponse,
  ProjectItem, HealthResponse
} from "../types/topology";
import {
  mockChat, mockValidate, mockGenerate, mockProjects, mockHealth
} from "./mock";
import { fetchWithTimeout } from "./request";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
export let USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

export function setUseMock(val: boolean) {
  USE_MOCK = val;
}

export async function checkHealth(): Promise<HealthResponse> {
  if (USE_MOCK) return mockHealth();
  try {
    const res = await fetch(`${API_BASE_URL}/api/health`);
    if (!res.ok) throw new Error("Health check failed");
    return await res.json();
  } catch (err) {
    console.warn("Backend unreachable, switching to mock health:", err);
    return mockHealth();
  }
}

export async function sendChatMessage(message: string, projectId?: number): Promise<ChatResponse> {
  if (USE_MOCK) return mockChat(message);
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, project_id: projectId })
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `Server error (${res.status})`);
    }
    return await res.json();
  } catch (err) {
    const reason = err instanceof Error ? err.message : "The local Gemma service could not be reached.";
    throw new Error(
      `${reason} Confirm that the backend is running and Ollama has the configured Gemma model.`
    );
  }
}

export async function validateTopology(topology: Topology): Promise<ValidationResult> {
  if (USE_MOCK) return mockValidate(topology);
  try {
    const res = await fetch(`${API_BASE_URL}/api/topology/validate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topology })
    });
    if (!res.ok) throw new Error("Validation request failed");
    return await res.json();
  } catch (err) {
    return mockValidate(topology);
  }
}

export async function generateArtifacts(topology: Topology): Promise<GenerateResponse> {
  if (USE_MOCK) return mockGenerate(topology);
  try {
    const res = await fetch(`${API_BASE_URL}/api/topology/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topology })
    });
    if (!res.ok) throw new Error("Artifact generation failed");
    return await res.json();
  } catch (err) {
    return mockGenerate(topology);
  }
}

export async function fetchProjects(): Promise<ProjectItem[]> {
  if (USE_MOCK) return mockProjects();
  try {
    const res = await fetch(`${API_BASE_URL}/api/projects`);
    if (!res.ok) throw new Error("Could not load projects");
    return await res.json();
  } catch (err) {
    return mockProjects();
  }
}

export async function saveProject(name: string, topology: Topology): Promise<{ id: number; name: string }> {
  if (USE_MOCK) return { id: Date.now(), name };
  try {
    const res = await fetch(`${API_BASE_URL}/api/projects`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, topology })
    });
    if (!res.ok) throw new Error("Failed to save project");
    return await res.json();
  } catch (err) {
    return { id: Date.now(), name };
  }
}

export async function fetchProject(id: number): Promise<ProjectItem | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/projects/${id}`);
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    return null;
  }
}

export async function pushToPacketTracer(topology: Topology): Promise<{ success: boolean; message: string }> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/packet-tracer/push`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topology })
    });
    return await res.json();
  } catch (err) {
    return {
      success: false,
      message: "Packet Tracer MCP bridge is not active. Use the Copy or Download button to paste manually."
    };
  }
}
