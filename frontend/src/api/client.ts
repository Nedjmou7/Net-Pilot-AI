import {
  Topology, ChatResponse, GenerateResponse, ValidationResult, HealthStatus, Project
} from './types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

class ApiClient {
  async getHealth(): Promise<HealthStatus> {
    return request<HealthStatus>('/api/health');
  }

  async sendMessage(message: string, projectId?: number): Promise<ChatResponse> {
    return request<ChatResponse>('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message, project_id: projectId })
    });
  }

  async validateTopology(topology: Topology): Promise<ValidationResult> {
    return request<ValidationResult>('/api/topology/validate', {
      method: 'POST',
      body: JSON.stringify({ topology })
    });
  }

  async generateArtifacts(topology: Topology): Promise<GenerateResponse> {
    return request<GenerateResponse>('/api/topology/generate', {
      method: 'POST',
      body: JSON.stringify({ topology })
    });
  }

  async getProjects(): Promise<Project[]> {
    return request<Project[]>('/api/projects');
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

  async pushToPacketTracer(topology: Topology): Promise<{ success: boolean; message: string; bundle_path?: string; packet_tracer_started?: boolean }> {
    return request<{ success: boolean; message: string; bundle_path?: string; packet_tracer_started?: boolean }>('/api/packet-tracer/push', {
      method: 'POST',
      body: JSON.stringify({ topology })
    });
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(init.headers || {}) }
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`HTTP ${response.status}: ${detail}`);
  }
  return response.json() as Promise<T>;
}

export const api = new ApiClient();
