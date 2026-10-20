import React from "react";
import { Folder, Plus, Save, Layers, BookOpen, ChevronRight, HardDrive } from "lucide-react";
import { ProjectItem, Topology } from "../types/topology";
import { SAMPLE_OSPF_TOPOLOGY } from "../api/mock";

interface SidebarProps {
  projects: ProjectItem[];
  currentProjectId: number | null;
  onSelectProject: (id: number) => void;
  onNewProject: () => void;
  onSaveProject: () => void;
  onLoadTemplate: (template: Topology) => void;
}

const TEMPLATES = [
  {
    name: "3-Router OSPF Backbone",
    desc: "3x 2911 Routers, Area 0, Dual LANs",
    topology: SAMPLE_OSPF_TOPOLOGY
  },
  {
    name: "Inter-VLAN (ROAS)",
    desc: "VLAN 10/20 Subinterfaces dot1Q",
    topology: {
      name: "inter-vlan-router-on-a-stick",
      devices: [
        { id: "R1", type: "router" as const, model: "2911", x: 350, y: 120 },
        { id: "SW1", type: "switch" as const, model: "2960-24TT", x: 350, y: 270 },
        { id: "PC1", type: "pc" as const, model: "PC-PT", x: 200, y: 420 },
        { id: "PC2", type: "pc" as const, model: "PC-PT", x: 500, y: 420 }
      ],
      links: [
        { a: "R1", a_port: "GigabitEthernet0/0", b: "SW1", b_port: "GigabitEthernet0/1", cable: "straight" as const },
        { a: "SW1", a_port: "FastEthernet0/1", b: "PC1", b_port: "FastEthernet0", cable: "straight" as const },
        { a: "SW1", a_port: "FastEthernet0/2", b: "PC2", b_port: "FastEthernet0", cable: "straight" as const }
      ],
      vlans: [
        { id: 10, name: "SALES" },
        { id: 20, name: "ENGINEERING" }
      ],
      ip_plan: [
        { device: "R1", interface: "GigabitEthernet0/0.10", ip: "192.168.10.1", mask: "255.255.255.0", gateway: null },
        { device: "R1", interface: "GigabitEthernet0/0.20", ip: "192.168.20.1", mask: "255.255.255.0", gateway: null },
        { device: "PC1", interface: "FastEthernet0", ip: "192.168.10.10", mask: "255.255.255.0", gateway: "192.168.10.1" },
        { device: "PC2", interface: "FastEthernet0", ip: "192.168.20.10", mask: "255.255.255.0", gateway: "192.168.20.1" }
      ],
      routing: { protocol: "none" as const },
      services: {
        dhcp: [
          { pool_name: "SALES_POOL", network: "192.168.10.0", mask: "255.255.255.0", default_router: "192.168.10.1", dns_server: "1.1.1.1" },
          { pool_name: "ENG_POOL", network: "192.168.20.0", mask: "255.255.255.0", default_router: "192.168.20.1", dns_server: "1.1.1.1" }
        ],
        nat: null,
        acls: []
      }
    }
  }
];

export const Sidebar: React.FC<SidebarProps> = ({
  projects,
  currentProjectId,
  onSelectProject,
  onNewProject,
  onSaveProject,
  onLoadTemplate
}) => {
  return (
    <div className="w-64 h-full bg-slate-900 border-r border-slate-800 flex flex-col justify-between shrink-0 select-none">
      <div className="flex flex-col h-full overflow-hidden">
        {/* Actions Header */}
        <div className="p-3 border-b border-slate-800 space-y-2">
          <button
            onClick={onNewProject}
            className="w-full flex items-center justify-center space-x-2 px-3 py-2 rounded-xl bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold shadow-lg shadow-sky-600/10 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>New Topology</span>
          </button>

          <button
            onClick={onSaveProject}
            className="w-full flex items-center justify-center space-x-2 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold transition-all"
          >
            <Save className="w-4 h-4 text-sky-400" />
            <span>Save Project</span>
          </button>
        </div>

        {/* Saved Projects Section */}
        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-4">
          <div>
            <div className="flex items-center justify-between text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-2 px-1">
              <span className="flex items-center space-x-1.5">
                <Folder className="w-3.5 h-3.5" />
                <span>Saved Labs ({projects.length})</span>
              </span>
            </div>

            {projects.length === 0 ? (
              <div className="text-[11px] text-slate-500 px-2 py-3 italic bg-slate-950/40 rounded-lg text-center">
                No saved labs yet
              </div>
            ) : (
              <div className="space-y-1">
                {projects.map((proj) => (
                  <button
                    key={proj.id}
                    onClick={() => onSelectProject(proj.id)}
                    className={`w-full text-left px-2.5 py-2 rounded-lg text-xs flex items-center justify-between transition-colors ${
                      currentProjectId === proj.id
                        ? "bg-sky-950/80 text-sky-300 border border-sky-600/40 font-medium"
                        : "text-slate-300 hover:bg-slate-800/80"
                    }`}
                  >
                    <span className="truncate pr-2">{proj.name}</span>
                    <ChevronRight className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Quick CCNA Lab Templates */}
          <div>
            <div className="flex items-center justify-between text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-2 px-1">
              <span className="flex items-center space-x-1.5">
                <Layers className="w-3.5 h-3.5" />
                <span>Lab Templates</span>
              </span>
            </div>

            <div className="space-y-1.5">
              {TEMPLATES.map((tmpl, idx) => (
                <button
                  key={idx}
                  onClick={() => onLoadTemplate(tmpl.topology)}
                  className="w-full text-left p-2.5 rounded-lg bg-slate-950/50 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-xs text-slate-300 transition-all group"
                >
                  <div className="font-medium text-slate-200 group-hover:text-sky-400">
                    {tmpl.name}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-0.5 truncate">{tmpl.desc}</div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Footer Info */}
      <div className="p-3 border-t border-slate-800 bg-slate-950/60 flex items-center space-x-2 text-[11px] text-slate-500">
        <HardDrive className="w-3.5 h-3.5 text-slate-400" />
        <span>100% Offline · Local SQLite & ChromaDB</span>
      </div>
    </div>
  );
};
