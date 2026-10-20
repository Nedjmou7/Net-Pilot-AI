import React, { useState } from 'react';
import {
  X, Bot, Terminal, FileCode, ShieldAlert, Send, Copy, Check, Download,
  Sparkles, Loader2, BookOpen, Layers
} from 'lucide-react';
import { GenerateResponse, ValidationResult, Topology } from '../api/types';
import { ChatMessage } from './ChatPanel';

interface ConsoleAndAssistantModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialTab?: 'chat' | 'configs' | 'script' | 'validation';
  messages: ChatMessage[];
  isLoading: boolean;
  onSendMessage: (msg: string) => void;
  generation: GenerateResponse | null;
  validation: ValidationResult | null;
  topology: Topology | null;
  onPushToPacketTracer: () => void;
  isPushing: boolean;
}

export const ConsoleAndAssistantModal: React.FC<ConsoleAndAssistantModalProps> = ({
  isOpen,
  onClose,
  initialTab = 'chat',
  messages,
  isLoading,
  onSendMessage,
  generation,
  validation,
  topology,
  onPushToPacketTracer,
  isPushing
}) => {
  const [activeTab, setActiveTab] = useState<'chat' | 'configs' | 'script' | 'validation'>(initialTab);
  const [input, setInput] = useState('');
  const [selectedDevice, setSelectedDevice] = useState<string>('');
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  React.useEffect(() => {
    setActiveTab(initialTab);
  }, [initialTab]);

  React.useEffect(() => {
    if (generation?.cli_configs && Object.keys(generation.cli_configs).length > 0) {
      if (!selectedDevice || !generation.cli_configs[selectedDevice]) {
        setSelectedDevice(Object.keys(generation.cli_configs)[0]);
      }
    }
  }, [generation, selectedDevice]);

  if (!isOpen) return null;

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleCopy = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const handleDownloadScript = (extension: 'js' | 'pts') => {
    if (!generation?.ptbuilder_script) return;
    const blob = new Blob([generation.ptbuilder_script], { type: 'text/javascript' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${topology?.name || 'topology'}_ptbuilder.${extension}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const errorCount = validation?.errors?.length || 0;
  const warningCount = validation?.warnings?.length || 0;

  return (
    <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="console-modal w-full max-w-4xl h-[min(640px,92vh)] bg-white border border-slate-200 rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-150">
        {/* Modal Header */}
        <div className="h-12 px-5 bg-[#0a0d14] border-b border-[#1b2230] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
            <h2 className="text-sm font-bold text-white font-mono tracking-wide">
              CLUST â€¢ SYSTEM CONSOLE & AI COPILOT
            </h2>
          </div>

          {/* Navigation Tabs */}
          <div className="console-tabs flex items-center gap-1 bg-slate-50 p-1 rounded-lg border border-slate-200">
            <button
              onClick={() => setActiveTab('chat')}
              className={`flex items-center gap-1.5 px-3 py-1 text-xs rounded-md font-medium transition ${
                activeTab === 'chat'
                  ? 'bg-cyan-500 text-black font-semibold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Bot className="w-3.5 h-3.5" />
              <span>Gemma Copilot</span>
            </button>

            <button
              onClick={() => setActiveTab('configs')}
              className={`flex items-center gap-1.5 px-3 py-1 text-xs rounded-md font-medium transition ${
                activeTab === 'configs'
                  ? 'bg-cyan-500 text-black font-semibold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Terminal className="w-3.5 h-3.5" />
              <span>IOS Configs</span>
            </button>

            <button
              onClick={() => setActiveTab('script')}
              className={`flex items-center gap-1.5 px-3 py-1 text-xs rounded-md font-medium transition ${
                activeTab === 'script'
                  ? 'bg-cyan-500 text-black font-semibold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <FileCode className="w-3.5 h-3.5" />
              <span>PTBuilder Script</span>
            </button>

            <button
              onClick={() => setActiveTab('validation')}
              className={`flex items-center gap-1.5 px-3 py-1 text-xs rounded-md font-medium transition ${
                activeTab === 'validation'
                  ? 'bg-cyan-500 text-black font-semibold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <ShieldAlert className="w-3.5 h-3.5" />
              <span>Validation ({errorCount})</span>
            </button>
          </div>

          <button
            onClick={onClose}
            className="p-1 rounded text-slate-400 hover:text-white hover:bg-[#1a2232] transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-hidden p-4 bg-[#0a0d14] flex flex-col">
          {/* TAB 1: AI COPILOT CHAT */}
          {activeTab === 'chat' && (
            <div className="flex flex-col h-full">
              {/* Quick Prompt Chips */}
              <div className="flex flex-wrap gap-1.5 mb-3">
                {[
                  "Build a network with 3 routers and OSPF",
                  "Create 2 VLANs with inter-VLAN routing",
                  "Why can't my PC ping the gateway?"
                ].map((chip, idx) => (
                  <button
                    key={idx}
                    onClick={() => onSendMessage(chip)}
                    disabled={isLoading}
                    className="text-[11px] text-slate-300 hover:text-cyan-300 bg-[#141a26] hover:bg-[#1b2332] px-3 py-1 rounded-full border border-[#212a3d] transition disabled:opacity-50"
                  >
                    âš¡ {chip}
                  </button>
                ))}
              </div>

              {/* Chat Message History */}
              <div className="flex-1 overflow-y-auto space-y-3.5 pr-2 mb-3">
                {messages.length === 0 ? (
                  <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-400">
                    <Sparkles className="w-8 h-8 text-cyan-400 mb-2" />
                    <p className="text-xs max-w-sm">
                      Type your Cisco architecture request. Gemma 4 will output topology JSON and generate deterministic configs.
                    </p>
                  </div>
                ) : (
                  messages.map((m) => (
                    <div
                      key={m.id}
                      className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'}`}
                    >
                      <div className="text-[10px] text-slate-500 font-mono mb-1">
                        {m.role === 'user' ? 'YOU' : 'GEMMA 4'}
                      </div>
                      <div
                        className={`max-w-[85%] rounded-xl p-3 text-xs leading-relaxed ${
                          m.role === 'user'
                            ? 'bg-cyan-500 text-black font-semibold'
                            : 'bg-[#141924] border border-[#1e2638] text-slate-200'
                        }`}
                      >
                        {m.content}
                        {m.sources && m.sources.length > 0 && (
                          <div className="mt-2.5 pt-2 border-t border-[#232c40] text-[10px] text-cyan-400 font-mono">
                            Sources: {m.sources.join(', ')}
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}

                {isLoading && (
                  <div className="flex items-center gap-2 p-3 bg-[#141924] border border-[#1e2638] rounded-xl text-xs text-cyan-400">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Gemma is reasoning locally...</span>
                  </div>
                )}
              </div>

              {/* Input Box */}
              <form onSubmit={handleSend} className="relative flex items-center">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask TopoGemma: 'Build 3 routers with OSPF'..."
                  disabled={isLoading}
                  className="w-full pl-3.5 pr-10 py-2.5 text-xs bg-[#111622] border border-[#1f2738] rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                />
                <button
                  type="submit"
                  disabled={!input.trim() || isLoading}
                  className="absolute right-1.5 p-1.5 bg-cyan-400 hover:bg-cyan-300 disabled:bg-[#1a2130] text-black rounded-lg transition"
                >
                  <Send className="w-3.5 h-3.5" />
                </button>
              </form>
            </div>
          )}

          {/* TAB 2: IOS CONFIGS */}
          {activeTab === 'configs' && (
            <div className="flex flex-col h-full">
              {generation?.cli_configs && Object.keys(generation.cli_configs).length > 0 ? (
                <>
                  <div className="flex items-center justify-between pb-2 mb-2 border-b border-[#1b2230]">
                    <div className="flex gap-1.5">
                      {Object.keys(generation.cli_configs).map((devId) => (
                        <button
                          key={devId}
                          onClick={() => setSelectedDevice(devId)}
                          className={`px-3 py-1 text-xs rounded font-mono font-bold transition ${
                            selectedDevice === devId
                              ? 'bg-cyan-400 text-black'
                              : 'text-slate-400 bg-[#141924] hover:text-white'
                          }`}
                        >
                          {devId}
                        </button>
                      ))}
                    </div>

                    <button
                      onClick={() => handleCopy(generation.cli_configs[selectedDevice] || '', selectedDevice)}
                      className="flex items-center gap-1.5 px-3 py-1 text-xs bg-[#161d2d] hover:bg-[#1d273d] text-slate-200 rounded border border-[#232e47] transition"
                    >
                      {copiedKey === selectedDevice ? (
                        <>
                          <Check className="w-3.5 h-3.5 text-emerald-400" />
                          <span className="text-emerald-400">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3.5 h-3.5 text-slate-400" />
                          <span>Copy CLI</span>
                        </>
                      )}
                    </button>
                  </div>

                  <pre className="flex-1 overflow-auto p-3 text-xs font-mono bg-[#0c1017] rounded-xl border border-[#1b2230] text-slate-300 leading-relaxed select-text">
                    {generation.cli_configs[selectedDevice]}
                  </pre>
                </>
              ) : (
                <div className="flex-1 flex items-center justify-center text-xs text-slate-500">
                  No CLI configs generated yet.
                </div>
              )}
            </div>
          )}

          {/* TAB 3: PTBUILDER SCRIPT */}
          {activeTab === 'script' && (
            <div className="flex flex-col h-full">
              <div className="flex items-center justify-between pb-2 mb-2 border-b border-[#1b2230]">
                <span className="text-xs text-slate-400 font-mono">Packet Tracer JavaScript Runner</span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleCopy(generation?.ptbuilder_script || '', 'script')}
                    className="flex items-center gap-1.5 px-3 py-1 text-xs bg-[#161d2d] hover:bg-[#1d273d] text-slate-200 rounded border border-[#232e47] transition"
                  >
                    {copiedKey === 'script' ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                        <span className="text-emerald-400">Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5 text-slate-400" />
                        <span>Copy Script</span>
                      </>
                    )}
                  </button>
                  <button
                    onClick={() => handleDownloadScript('js')}
                    className="flex items-center gap-1.5 px-3 py-1 text-xs bg-cyan-950/80 hover:bg-cyan-900/80 text-cyan-300 rounded border border-cyan-700/50 transition"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download .js</span>
                  </button>
                  <button
                    onClick={() => handleDownloadScript('pts')}
                    className="flex items-center gap-1.5 px-3 py-1 text-xs bg-cyan-950/80 hover:bg-cyan-900/80 text-cyan-300 rounded border border-cyan-700/50 transition"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download .pts</span>
                  </button>
                  <button
                    onClick={onPushToPacketTracer}
                    disabled={isPushing}
                    className="flex items-center gap-1.5 px-3 py-1 text-xs bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded font-medium transition"
                  >
                    <Send className="w-3.5 h-3.5" />
                    <span>{isPushing ? 'Pushing...' : 'Live MCP Push'}</span>
                  </button>
                </div>
              </div>

              <pre className="flex-1 overflow-auto p-3 text-xs font-mono bg-[#0c1017] rounded-xl border border-[#1b2230] text-slate-300 leading-relaxed select-text">
                {generation?.ptbuilder_script || '// PTBuilder script will appear here'}
              </pre>
            </div>
          )}

          {/* TAB 4: VALIDATION REPORT */}
          {activeTab === 'validation' && (
            <div className="flex-1 overflow-y-auto space-y-3">
              {validation?.is_valid && (
                <div className="p-3.5 rounded-xl bg-emerald-950/40 border border-emerald-800/50 text-xs text-emerald-300">
                  <h4 className="font-bold">All Deterministic Rules Passed</h4>
                  <p className="mt-1 text-emerald-400/80">
                    No duplicate device IDs, valid interface ports per model, no overlapping subnets, and gateways match router interfaces.
                  </p>
                </div>
              )}

              {errorCount > 0 && (
                <div className="space-y-1.5">
                  <div className="text-xs font-bold text-rose-400 uppercase font-mono">Errors ({errorCount})</div>
                  {validation?.errors.map((err, i) => (
                    <div key={i} className="p-2.5 rounded bg-rose-950/40 border border-rose-800/50 text-xs text-rose-300">
                      â€¢ {err}
                    </div>
                  ))}
                </div>
              )}

              {warningCount > 0 && (
                <div className="space-y-1.5">
                  <div className="text-xs font-bold text-amber-400 uppercase font-mono">Warnings ({warningCount})</div>
                  {validation?.warnings.map((w, i) => (
                    <div key={i} className="p-2.5 rounded bg-amber-950/40 border border-amber-800/50 text-xs text-amber-300">
                      â€¢ {w}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
