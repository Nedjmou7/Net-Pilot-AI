import {
  Topology, ChatResponse, GenerateResponse, ValidationResult, HealthStatus, Project
} from './types';
import * as mock from './mock';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiClient {
  private useMock: boolean = mock.USE_MOCK;

  setUseMock(flag: boolean) {
    this.useMock = flag;
  }

  async getHealth(): Promise<HealthStatus> {
    if (this.useMock) return mock.mockHealth();
    try {
      const res = await fetch(`${API_BASE}/api/health`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (e) {
      console.warn("Backend /api/health unreachable, using mock data", e);
      return mock.mockHealth();
    }
  }

  async sendMessage(message: string, projectId?: number): Promise<ChatResponse> {
    if (this.useMock) return mock.mockChat(message);
    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, project_id: projectId })
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (e) {
      console.warn("Backend /api/chat error, falling back to mock response", e);
      return mock.mockChat(message);
    }
  }

  async validateTopology(topology: Topology): Promise<ValidationResult> {
    if (this.useMock) return mock.mockValidate(topology);
    try {
      const res = await fetch(`${API_BASE}/api/topology/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(topology)
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (e) {
      console.warn("Backend /api/topology/validate error, fallback to mock", e);
      return mock.mockValidate(topology);
    }
  }

  async generateArtifacts(topology: Topology): Promise<GenerateResponse> {
    if (this.useMock) return mock.mockGenerate(topology);
    try {
      const res = await fetch(`${API_BASE}/api/topology/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topology })
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (e) {
      console.warn("Backend /api/topology/generate error, fallback to mock", e);
      return mock.mockGenerate(topology);
    }
  }

  async getProjects(): Promise<Project[]> {
    if (this.useMock) return mock.mockGetProjects();
    try {
      const res = await fetch(`${API_BASE}/api/projects`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (e) {
      return mock.mockGetProjects();
    }
  }

  async saveProject(name: string, topology: Topology): Promise<Project> {
    const res = await fetch(`${API_BASE}/api/projects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, topology })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  }

  async updateProject(id: number, name: string, topology: Topology): Promise<Project> {
    const res = await fetch(`${API_BASE}/api/projects/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, topology })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  }

  async getProject(id: number): Promise<{ project: Project; messages: any[] }> {
    const res = await fetch(`${API_BASE}/api/projects/${id}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  }

  async deleteProject(id: number): Promise<void> {
    const res = await fetch(`${API_BASE}/api/projects/${id}`, {
      method: 'DELETE'
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
  }

  async pushToPacketTracer(topology: Topology): Promise<{ success: boolean; message: string }> {
    try {
      const res = await fetch(`${API_BASE}/api/mcp/push`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topology })
      });
      return await res.json();
    } catch (e: any) {
      return { success: false, message: e.message || "Failed to reach Packet Tracer bridge" };
    }
  }
}

export const api = new ApiClient();
