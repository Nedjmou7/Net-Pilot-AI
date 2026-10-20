import React, { useState } from 'react';
import { Copy, Check, Download, AlertTriangle, CheckCircle, Terminal, FileCode, ShieldAlert, Send } from 'lucide-react';
import { GenerateResponse, ValidationResult, Topology } from '../api/types';

interface OutputPanelProps {
  generation: GenerateResponse | null;
  validation: ValidationResult | null;
  topology: Topology | null;
  onPushToPacketTracer: () => void;
  isPushing: boolean;
}

export const OutputPanel: React.FC<OutputPanelProps> = ({
  generation,
  validation,
  topology,
  onPushToPacketTracer,
  isPushing
}) => {
  const [activeTab, setActiveTab] = useState<'configs' | 'script' | 'validation'>('configs');
  const [selectedDevice, setSelectedDevice] = useState<string>('');
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  // Set default selected device if configs exist
  React.useEffect(() => {
    if (generation?.cli_configs && Object.keys(generation.cli_configs).length > 0) {
      if (!selectedDevice || !generation.cli_configs[selectedDevice]) {
        setSelectedDevice(Object.keys(generation.cli_configs)[0]);
      }
    }
  }, [generation, selectedDevice]);

  const handleCopy = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const handleDownloadScript = () => {
    if (!generation?.ptbuilder_script) return;
    const blob = new Blob([generation.ptbuilder_script], { type: 'text/javascript' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${topology?.name || 'topology'}_ptbuilder.js`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const errorCount = validation?.errors?.length || 0;
  const warningCount = validation?.warnings?.length || 0;

  return (
    <div className="flex flex-col h-full bg-slate-900 border-l border-slate-800">
      {/* Tab Navigation Header */}
      <div className="h-10 border-b border-slate-800 bg-slate-950/60 px-3 flex items-center justify-between">
        <div className="flex gap-1">
          <button
            onClick={() => setActiveTab('configs')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
              activeTab === 'configs'
                ? 'bg-slate-800 text-cyan-400 border border-slate-700/80 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Terminal className="w-3.5 h-3.5" />
            <span>IOS Configs</span>
          </button>

          <button
            onClick={() => setActiveTab('script')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
              activeTab === 'script'
                ? 'bg-slate-800 text-cyan-400 border border-slate-700/80 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <FileCode className="w-3.5 h-3.5" />
            <span>PTBuilder Script</span>
          </button>

          <button
            onClick={() => setActiveTab('validation')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
              activeTab === 'validation'
                ? 'bg-slate-800 text-cyan-400 border border-slate-700/80 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>Validation</span>
            {errorCount > 0 && (
              <span className="px-1.5 py-0.2 text-[10px] rounded-full bg-rose-500/20 text-rose-400 font-bold border border-rose-500/30">
                {errorCount}
              </span>
            )}
            {errorCount === 0 && warningCount > 0 && (
              <span className="px-1.5 py-0.2 text-[10px] rounded-full bg-amber-500/20 text-amber-400 font-bold border border-amber-500/30">
                {warningCount}
              </span>
            )}
          </button>
        </div>

        {/* Live MCP / Packet Tracer Bridge Push button */}
        <button
          onClick={onPushToPacketTracer}
          disabled={isPushing || !generation}
          className="flex items-center gap-1.5 px-2.5 py-1 text-[11px] bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-lg font-medium transition disabled:opacity-40 shadow-sm shadow-cyan-600/30"
          title="Push generated topology script directly to Cisco Packet Tracer bridge"
        >
          <Send className="w-3 h-3" />
          <span>{isPushing ? 'Pushing...' : 'Live Push'}</span>
        </button>
      </div>

      {/* Tab Contents */}
      <div className="flex-1 overflow-hidden p-3 bg-slate-950 flex flex-col">
        {/* Tab 1: Device IOS CLI Configs */}
        {activeTab === 'configs' && (
          <div className="flex flex-col h-full">
            {generation?.cli_configs && Object.keys(generation.cli_configs).length > 0 ? (
              <>
                {/* Device Selector Sub-Tabs */}
                <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-800">
                  <div className="flex gap-1.5 overflow-x-auto">
                    {Object.keys(generation.cli_configs).map((devId) => (
                      <button
                        key={devId}
                        onClick={() => setSelectedDevice(devId)}
                        className={`px-2.5 py-1 text-xs rounded font-mono font-semibold transition ${
                          selectedDevice === devId
                            ? 'bg-cyan-950 text-cyan-300 border border-cyan-800'
                            : 'text-slate-400 hover:text-slate-200 bg-slate-900'
                        }`}
                      >
                        {devId}
                      </button>
                    ))}
                  </div>

                  <button
                    onClick={() => handleCopy(generation.cli_configs[selectedDevice] || '', selectedDevice)}
                    className="flex items-center gap-1 px-2.5 py-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 rounded border border-slate-700 transition"
                  >
                    {copiedKey === selectedDevice ? (
                      <>
                        <Check className="w-3 h-3 text-emerald-400" />
                        <span className="text-emerald-400">Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3 h-3 text-slate-400" />
                        <span>Copy CLI</span>
                      </>
                    )}
                  </button>
                </div>

                {/* Code Block */}
                <pre className="flex-1 overflow-auto p-3 text-xs font-mono bg-slate-900/90 rounded-xl border border-slate-800 text-slate-200 leading-relaxed select-text">
                  {generation.cli_configs[selectedDevice] || '// No configuration generated for this device'}
                </pre>
              </>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-slate-500 text-xs">
                No CLI configs generated yet.
              </div>
            )}
          </div>
        )}

        {/* Tab 2: PTBuilder Script */}
        {activeTab === 'script' && (
          <div className="flex flex-col h-full">
            <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-800">
              <span className="text-xs text-slate-400 font-mono">PTBuilder Script Runner (JS)</span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleCopy(generation?.ptbuilder_script || '', 'script')}
                  className="flex items-center gap-1 px-2.5 py-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 rounded border border-slate-700 transition"
                >
                  {copiedKey === 'script' ? (
                    <>
                      <Check className="w-3 h-3 text-emerald-400" />
                      <span className="text-emerald-400">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3 h-3 text-slate-400" />
                      <span>Copy Script</span>
                    </>
                  )}
                </button>
                <button
                  onClick={handleDownloadScript}
                  className="flex items-center gap-1 px-2.5 py-1 text-xs bg-cyan-900/40 hover:bg-cyan-800/60 text-cyan-300 rounded border border-cyan-700/50 transition"
                >
                  <Download className="w-3 h-3" />
                  <span>Download .js</span>
                </button>
              </div>
            </div>

            <pre className="flex-1 overflow-auto p-3 text-xs font-mono bg-slate-900/90 rounded-xl border border-slate-800 text-slate-200 leading-relaxed select-text">
              {generation?.ptbuilder_script || '// PTBuilder script will appear here once a topology is created'}
            </pre>
          </div>
        )}

        {/* Tab 3: Validation Panel */}
        {activeTab === 'validation' && (
          <div className="flex-1 overflow-y-auto space-y-3">
            {validation?.is_valid && validation.errors.length === 0 ? (
              <div className="p-3.5 rounded-xl bg-emerald-950/40 border border-emerald-800/50 flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="text-xs font-bold text-emerald-300">Deterministic Validation Passed</h4>
                  <p className="text-xs text-emerald-400/80 mt-1 leading-relaxed">
                    All device IDs are unique, ports match physical models, subnets are valid without collision,
                    and gateways match connected router interfaces.
                  </p>
                </div>
              </div>
            ) : null}

            {/* Error List */}
            {errorCount > 0 && (
              <div className="space-y-1.5">
                <div className="text-[11px] font-bold uppercase tracking-wider text-rose-400 flex items-center gap-1.5">
                  <ShieldAlert className="w-3.5 h-3.5" />
                  <span>Errors Detected ({errorCount})</span>
                </div>
                {validation?.errors.map((err, idx) => (
                  <div
                    key={idx}
                    className="p-2.5 rounded-lg bg-rose-950/40 border border-rose-800/50 text-xs text-rose-300 leading-relaxed flex items-start gap-2"
                  >
                    <span className="font-bold text-rose-400">•</span>
                    <span>{err}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Warning List */}
            {warningCount > 0 && (
              <div className="space-y-1.5">
                <div className="text-[11px] font-bold uppercase tracking-wider text-amber-400 flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>Warnings ({warningCount})</span>
                </div>
                {validation?.warnings.map((warn, idx) => (
                  <div
                    key={idx}
                    className="p-2.5 rounded-lg bg-amber-950/40 border border-amber-800/50 text-xs text-amber-300 leading-relaxed flex items-start gap-2"
                  >
                    <span className="font-bold text-amber-400">•</span>
                    <span>{warn}</span>
                  </div>
                ))}
              </div>
            )}

            {!validation && (
              <div className="h-full flex items-center justify-center text-xs text-slate-500">
                Validation reports will appear here after building a network.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
