import React from 'react';
import { Bot, CircleHelp, Clock3, MessageSquarePlus, Network, Settings2, Trash2 } from 'lucide-react';
import { Project } from '../api/types';

interface WorkspaceSidebarProps {
  projects: Project[];
  activeProjectId: number | null;
  onNewChat: () => void;
  onSelectProject: (project: Project) => void;
  onDeleteProject: (project: Project) => void;
  onOpenSettings: () => void;
  onOpenHelp: () => void;
}

export const WorkspaceSidebar: React.FC<WorkspaceSidebarProps> = ({
  projects, activeProjectId, onNewChat, onSelectProject, onDeleteProject, onOpenSettings, onOpenHelp
}) => (
  <aside className="workspace-sidebar" id="workspace-sidebar">
    <div className="workspace-brand">
      <div className="workspace-brand-icon"><Network className="h-[18px] w-[18px]" /></div>
      <div><div className="font-bold tracking-tight">NetPilot <span>AI</span></div><div className="text-[10px] text-slate-500">PACKET TRACER STUDIO</div></div>
    </div>

    <button className="new-chat-button" onClick={onNewChat}><MessageSquarePlus className="h-4 w-4" />New chat</button>

    <div className="history-heading"><Clock3 className="h-3.5 w-3.5" />RECENT LABS</div>
    <div className="history-list">
      {projects.length ? projects.map((project) => (
        <div className={`history-entry ${activeProjectId === project.id ? 'selected' : ''}`} key={project.id}>
          <button className="history-open" onClick={() => onSelectProject(project)} title={project.name}>
            <Network className="h-3.5 w-3.5 shrink-0" /><span>{project.name}</span>
          </button>
          <button className="history-delete" onClick={() => onDeleteProject(project)} aria-label={`Delete ${project.name}`} title="Delete lab">
            <Trash2 className="h-3.5 w-3.5" />
          </button>
        </div>
      )) : <p className="empty-history">Your recent labs will appear here.</p>}
    </div>

    <div className="sidebar-bottom">
      <div className="sidebar-agent-card"><span className="agent-avatar"><Bot className="h-4 w-4" /></span><div className="min-w-0"><div className="text-xs font-semibold text-slate-700">Network agent</div><div className="truncate text-[10px] text-slate-500">Cisco labs · IOS · PTBuilder</div></div><span className="agent-presence" /></div>
      <button className="sidebar-utility" onClick={onOpenSettings}><Settings2 className="h-4 w-4" />Workspace info</button>
      <button className="sidebar-utility" onClick={onOpenHelp}><CircleHelp className="h-4 w-4" />Help</button>
      <div className="sidebar-footnote">AI generated configurations should be reviewed before deployment.</div>
    </div>
  </aside>
);
