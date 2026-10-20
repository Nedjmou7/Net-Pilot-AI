import React, { useState } from 'react';
import { Plus, Folder, Trash2, Save, X, Network, BookOpen, Layers } from 'lucide-react';
import { Project, Topology } from '../api/types';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  projects: Project[];
  activeProjectId: number | null;
  onSelectProject: (proj: Project) => void;
  onNewProject: () => void;
  onSaveCurrentProject: (name: string) => void;
  onDeleteProject: (id: number) => void;
  onLoadTemplate: (templateName: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onClose,
  projects,
  activeProjectId,
  onSelectProject,
  onNewProject,
  onSaveCurrentProject,
  onDeleteProject,
  onLoadTemplate
}) => {
  const [saveName, setSaveName] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  if (!isOpen) return null;

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    if (!saveName.trim()) return;
    onSaveCurrentProject(saveName.trim());
    setSaveName('');
    setIsSaving(false);
  };

  return (
    <div className="fixed inset-y-0 left-0 w-72 bg-slate-900/95 backdrop-blur-md border-r border-slate-800 z-30 flex flex-col shadow-2xl animate-in slide-in-from-left duration-200">
      {/* Sidebar Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Folder className="w-5 h-5 text-cyan-400" />
          <h2 className="text-sm font-bold text-white">Project Workspace</h2>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800 transition"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Action Buttons */}
      <div className="p-3 grid grid-cols-2 gap-2 border-b border-slate-800">
        <button
          onClick={onNewProject}
          className="flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-medium transition shadow-lg shadow-cyan-600/20"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>New</span>
        </button>
        <button
          onClick={() => setIsSaving(true)}
          className="flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition"
        >
          <Save className="w-3.5 h-3.5" />
          <span>Save As</span>
        </button>
      </div>

      {/* Save Project Inline Dialog */}
      {isSaving && (
        <form onSubmit={handleSave} className="p-3 bg-slate-950/80 border-b border-slate-800">
          <label className="text-[11px] font-semibold text-slate-400 block mb-1">Project Name</label>
          <div className="flex gap-2">
            <input
              type="text"
              value={saveName}
              onChange={(e) => setSaveName(e.target.value)}
              placeholder="e.g. Campus OSPF Lab"
              className="flex-1 px-2.5 py-1 text-xs bg-slate-800 border border-slate-700 rounded text-white focus:outline-none focus:border-cyan-500"
              autoFocus
            />
            <button
              type="submit"
              className="px-2.5 py-1 bg-cyan-600 hover:bg-cyan-500 text-white text-xs rounded font-medium"
            >
              OK
            </button>
          </div>
        </form>
      )}

      {/* Saved Projects List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-1">
        <div className="text-[10px] uppercase font-bold tracking-wider text-slate-400 px-2 py-1">
          Saved Labs ({projects.length})
        </div>

        {projects.length === 0 ? (
          <div className="p-4 text-center text-xs text-slate-400">
            No saved projects yet. Build a network and save it!
          </div>
        ) : (
          projects.map((proj) => (
            <div
              key={proj.id}
              className={`group flex items-center justify-between p-2 rounded-lg text-xs cursor-pointer transition ${
                activeProjectId === proj.id
                  ? 'bg-cyan-950/50 text-cyan-300 border border-cyan-800/60'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`}
              onClick={() => onSelectProject(proj)}
            >
              <div className="flex items-center gap-2 truncate">
                <Network className="w-3.5 h-3.5 text-slate-400 group-hover:text-cyan-400 flex-shrink-0" />
                <span className="truncate font-medium">{proj.name}</span>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteProject(proj.id);
                }}
                className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-rose-400 transition"
                title="Delete project"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))
        )}

        {/* Starter Labs */}
        <div className="pt-4 text-[10px] uppercase font-bold tracking-wider text-slate-400 px-2 py-1">
          Quick Templates
        </div>
        <button
          onClick={() => onLoadTemplate("3-router-ospf")}
          className="w-full text-left p-2 rounded-lg text-xs text-slate-300 hover:bg-slate-800 hover:text-cyan-300 transition flex items-center gap-2"
        >
          <Layers className="w-3.5 h-3.5 text-cyan-400" />
          <span>3-Router OSPF Backbone</span>
        </button>
        <button
          onClick={() => onLoadTemplate("intervlan-dhcp")}
          className="w-full text-left p-2 rounded-lg text-xs text-slate-300 hover:bg-slate-800 hover:text-cyan-300 transition flex items-center gap-2"
        >
          <Layers className="w-3.5 h-3.5 text-emerald-400" />
          <span>Inter-VLAN Routing & DHCP</span>
        </button>
        <button
          onClick={() => onLoadTemplate("small-office")}
          className="w-full text-left p-2 rounded-lg text-xs text-slate-300 hover:bg-slate-800 hover:text-cyan-300 transition flex items-center gap-2"
        >
          <Layers className="w-3.5 h-3.5 text-purple-400" />
          <span>Small Office (1R, 1SW, 2PC)</span>
        </button>
      </div>

      <div className="p-3 border-t border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
        <span>TopoGemma v1.0.0</span>
        <span className="text-cyan-500 font-mono">SQLite Local</span>
      </div>
    </div>
  );
};
