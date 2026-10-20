import React, { useState } from "react";
import { Copy, Download, Check, AlertTriangle, XCircle, CheckCircle, Terminal, FileCode, ShieldAlert, Send, Files } from "lucide-react";
import { ValidationResult } from "../types/topology";

interface ArtifactsPanelProps {
  configs: Record<string, string>;
  ptbuilderScript: string;
  validation: ValidationResult;
  onPushToPacketTracer?: () => void;
  isPushing?: boolean;
  pushMessage?: string | null;
}

type TabType = "configs" | "ptbuilder" | "validation";

export const ArtifactsPanel: React.FC<ArtifactsPanelProps> = ({
  configs,
  ptbuilderScript,
  validation,
  onPushToPacketTracer,
  isPushing,
  pushMessage
}) => {
  const [activeTab, setActiveTab] = useState<TabType>("configs");
  const [selectedDevice, setSelectedDevice] = useState<string>("");
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const deviceIds = Object.keys(configs);
  const activeDevice = selectedDevice && configs[selectedDevice] ? selectedDevice : deviceIds[0] || "";

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleDownloadJs = () => {
    if (!ptbuilderScript) return;
    const blob = new Blob([ptbuilderScript], { type: "text/javascript" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "topogemma_build.js";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleCopyAllConfigs = () => {
    const allConfigs = Object.entries(configs)
      .map(([deviceId, config]) => `! ===== ${deviceId} =====\n${config}`)
      .join("\n\n");
    if (!allConfigs) return;
    handleCopy(allConfigs, "all-configs");
  };

  const handleDownloadConfig = () => {
    if (!activeDevice || !configs[activeDevice]) return;
    const blob = new Blob([configs[activeDevice]], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${activeDevice}-ios-config.txt`;
    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);
    URL.revokeObjectURL(url);
  };

  const hasErrors = validation.errors && validation.errors.length > 0;
  const hasWarnings = validation.warnings && validation.warnings.length > 0;

  return (
    <div className="flex flex-col h-full bg-slate-900 border-l border-slate-800">
      {/* Tab Navigation Header */}
      <div className="flex border-b border-slate-800 bg-slate-900/80 px-2 pt-2">
        <button
          onClick={() => setActiveTab("configs")}
          className={`flex items-center space-x-1.5 px-3 py-2 text-xs font-medium rounded-t-lg transition-colors border-t border-x ${
            activeTab === "configs"
              ? "bg-slate-950 text-sky-400 border-slate-800 border-b-transparent"
              : "text-slate-400 hover:text-slate-200 border-transparent"
          }`}
        >
          <Terminal className="w-3.5 h-3.5" />
          <span>IOS Configs</span>
          {deviceIds.length > 0 && (
            <span className="text-[10px] bg-slate-800 text-slate-400 px-1.5 py-0.2 rounded-full">
              {deviceIds.length}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab("ptbuilder")}
          className={`flex items-center space-x-1.5 px-3 py-2 text-xs font-medium rounded-t-lg transition-colors border-t border-x ${
            activeTab === "ptbuilder"
              ? "bg-slate-950 text-sky-400 border-slate-800 border-b-transparent"
              : "text-slate-400 hover:text-slate-200 border-transparent"
          }`}
        >
          <FileCode className="w-3.5 h-3.5" />
          <span>PTBuilder Script</span>
        </button>

        <button
          onClick={() => setActiveTab("validation")}
          className={`flex items-center space-x-1.5 px-3 py-2 text-xs font-medium rounded-t-lg transition-colors border-t border-x ${
            activeTab === "validation"
              ? "bg-slate-950 text-sky-400 border-slate-800 border-b-transparent"
              : "text-slate-400 hover:text-slate-200 border-transparent"
          }`}
        >
          <ShieldAlert className="w-3.5 h-3.5" />
          <span>Validation</span>
          {hasErrors && (
            <span className="text-[9px] bg-red-950 text-red-400 px-1.5 py-0.2 rounded-full font-bold">
              {validation.errors.length}
            </span>
          )}
          {!hasErrors && hasWarnings && (
            <span className="text-[9px] bg-amber-950 text-amber-400 px-1.5 py-0.2 rounded-full font-bold">
              {validation.warnings.length}
            </span>
          )}
          {!hasErrors && !hasWarnings && (
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
          )}
        </button>
      </div>

      {/* Tab 1: Device IOS CLI Configs */}
      {activeTab === "configs" && (
        <div className="flex-1 flex flex-col min-h-0 bg-slate-950">
          {/* Subheader: Device Pills */}
          <div className="px-3 py-2 border-b border-slate-800/80 bg-slate-900/40 flex items-center justify-between">
            <div className="flex space-x-1 overflow-x-auto max-w-[70%]">
              {deviceIds.map((devId) => (
                <button
                  key={devId}
                  onClick={() => setSelectedDevice(devId)}
                  className={`text-xs font-mono px-2.5 py-1 rounded-md transition-colors ${
                    activeDevice === devId
                      ? "bg-sky-600/20 text-sky-300 border border-sky-500/40 font-bold"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-800"
                  }`}
                >
                  {devId}
                </button>
              ))}
            </div>

            {activeDevice && (
              <div className="flex items-center gap-1.5">
                <button
                  onClick={handleDownloadConfig}
                  title="Download this device configuration"
                  className="flex items-center space-x-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-2 py-1 rounded-md border border-slate-700 transition-colors"
                >
                  <Download className="h-3.5 w-3.5 text-slate-400" />
                </button>
                <button
                  onClick={() => handleCopy(configs[activeDevice], activeDevice)}
                  className="flex items-center space-x-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-2.5 py-1 rounded-md border border-slate-700 transition-colors"
                >
                {copiedId === activeDevice ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                    <span className="text-emerald-400">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5 text-slate-400" />
                    <span>Copy Config</span>
                  </>
                )}
                </button>
                <button
                  onClick={handleCopyAllConfigs}
                  title="Copy all device configurations"
                  className="flex items-center space-x-1 text-xs bg-sky-600 hover:bg-sky-500 text-white px-2 py-1 rounded-md transition-colors"
                >
                  <Files className="h-3.5 w-3.5" />
                  <span>{copiedId === "all-configs" ? "Copied all" : "All"}</span>
                </button>
              </div>
            )}
          </div>

          {/* Config Code View */}
          <div className="flex-1 overflow-y-auto p-4 font-mono text-xs text-slate-300 leading-relaxed bg-slate-950 select-text">
            {activeDevice && configs[activeDevice] ? (
              <pre className="whitespace-pre">{configs[activeDevice]}</pre>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-slate-500 italic">
                Generate a topology to preview Cisco IOS CLI device configurations.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 2: PTBuilder Script */}
      {activeTab === "ptbuilder" && (
        <div className="flex-1 flex flex-col min-h-0 bg-slate-950">
          <div className="px-3 py-2 border-b border-slate-800/80 bg-slate-900/40 flex items-center justify-between">
            <span className="text-xs font-mono text-slate-400">topogemma_build.js</span>
            <div className="flex items-center space-x-2">
              <button
                onClick={handleDownloadJs}
                disabled={!ptbuilderScript}
                className="flex items-center space-x-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-2.5 py-1 rounded-md border border-slate-700 transition-colors disabled:opacity-50"
              >
                <Download className="w-3.5 h-3.5 text-slate-400" />
                <span>Download PTBuilder .js</span>
              </button>
              <button
                onClick={() => handleCopy(ptbuilderScript, "ptbuilder")}
                disabled={!ptbuilderScript}
                className="flex items-center space-x-1 text-xs bg-sky-600 hover:bg-sky-500 text-white px-2.5 py-1 rounded-md transition-colors disabled:opacity-50"
              >
                {copiedId === "ptbuilder" ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-white" />
                    <span>Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5 text-white" />
                    <span>Copy Script</span>
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 font-mono text-xs text-emerald-400/90 leading-relaxed bg-slate-950 select-text">
            <div className="mb-4 rounded-lg border border-amber-500/30 bg-amber-950/20 p-3 text-[11px] leading-relaxed text-amber-200">
              This is an external PTBuilder bridge script, not a native Cisco Packet
              Tracer .pkt file. It only runs where the PTBuilder API is installed.
              For standard Packet Tracer, use the IOS Configs tab and paste each
              device configuration into its CLI.
            </div>
            {ptbuilderScript ? (
              <pre className="whitespace-pre">{ptbuilderScript}</pre>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-slate-500 italic">
                No PTBuilder automation script generated yet.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 3: Validation Results */}
      {activeTab === "validation" && (
        <div className="flex-1 overflow-y-auto p-4 bg-slate-950 space-y-4">
          {!hasErrors && !hasWarnings ? (
            <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-500/40 text-emerald-300 flex items-start space-x-3">
              <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-400">
                  Validation Successful (100% Passed)
                </h4>
                <p className="text-xs mt-1 text-emerald-300/80 leading-relaxed">
                  All IP subnets, gateways, port allocations, and routing parameters satisfy Cisco IOS specifications.
                </p>
              </div>
            </div>
          ) : null}

          {hasErrors && (
            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-red-400 flex items-center space-x-1.5">
                <XCircle className="w-4 h-4 text-red-400" />
                <span>Errors ({validation.errors.length})</span>
              </h4>
              {validation.errors.map((err, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-lg bg-red-950/40 border border-red-500/40 text-red-300 text-xs leading-relaxed"
                >
                  {err}
                </div>
              ))}
            </div>
          )}

          {hasWarnings && (
            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center space-x-1.5">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <span>Warnings ({validation.warnings.length})</span>
              </h4>
              {validation.warnings.map((warn, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-lg bg-amber-950/40 border border-amber-500/40 text-amber-300 text-xs leading-relaxed"
                >
                  {warn}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Live Push Banner at Bottom */}
      <div className="p-3 border-t border-slate-800 bg-slate-900/90 flex items-center justify-between">
        <div className="flex flex-col">
          <span className="text-[11px] font-medium text-slate-300">Packet Tracer Bridge</span>
          <span className="text-[10px] text-slate-500">Live script push to Scripting Engine</span>
        </div>
        <button
          onClick={onPushToPacketTracer}
          disabled={isPushing || !ptbuilderScript}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-sky-400 border border-slate-700 text-xs font-medium transition-colors disabled:opacity-40"
        >
          <Send className="w-3.5 h-3.5" />
          <span>{isPushing ? "Pushing..." : "Push to PT"}</span>
        </button>
      </div>

      {pushMessage && (
        <div className="px-3 py-1.5 bg-slate-800 text-[11px] text-slate-300 border-t border-slate-700 italic">
          {pushMessage}
        </div>
      )}
    </div>
  );
};
