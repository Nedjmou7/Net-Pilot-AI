import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, BookOpen, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import { ChatResponse } from '../api/types';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  intent?: 'build' | 'question' | 'troubleshoot';
  sources?: string[];
  timestamp: string;
}

interface ChatPanelProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onSendMessage: (message: string) => void;
  onSelectPromptChip: (prompt: string) => void;
}

const EXAMPLE_CHIPS = [
  "Build a network with 3 routers and OSPF",
  "Create 2 VLANs with inter-VLAN routing",
  "Why can't my PC ping the gateway?"
];

export const ChatPanel: React.FC<ChatPanelProps> = ({
  messages,
  isLoading,
  onSendMessage,
  onSelectPromptChip
}) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 border-r border-slate-800">
      {/* Panel Title Bar */}
      <div className="px-4 py-2.5 border-b border-slate-800 bg-slate-900/50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bot className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-bold text-white uppercase tracking-wider">Assistant Chat</span>
        </div>
        <span className="text-[10px] text-cyan-400 font-mono bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/40">
          Gemma 4 Local
        </span>
      </div>

      {/* Suggested Prompt Chips */}
      <div className="p-2 border-b border-slate-800 bg-slate-950/40 flex flex-wrap gap-1.5">
        {EXAMPLE_CHIPS.map((chip, idx) => (
          <button
            key={idx}
            onClick={() => onSelectPromptChip(chip)}
            disabled={isLoading}
            className="text-[11px] text-slate-300 hover:text-cyan-300 bg-slate-800 hover:bg-slate-700/80 px-2.5 py-1 rounded-full border border-slate-700/60 transition text-left truncate max-w-full disabled:opacity-50"
          >
            ⚡ {chip}
          </button>
        ))}
      </div>

      {/* Message History */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-400">
            <div className="w-12 h-12 rounded-2xl bg-cyan-950/40 border border-cyan-800/50 flex items-center justify-center mb-3">
              <Sparkles className="w-6 h-6 text-cyan-400" />
            </div>
            <h3 className="text-sm font-bold text-white mb-1">Welcome to TopoGemma</h3>
            <p className="text-xs text-slate-400 max-w-xs mb-4">
              Ask to build network topologies, generate Packet Tracer scripts, or troubleshoot Cisco CCNA labs 100% locally.
            </p>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
            >
              <div className="flex items-center gap-1.5 mb-1 text-[10px] text-slate-400 font-medium">
                {msg.role === 'user' ? (
                  <>
                    <span>You</span>
                    <User className="w-3 h-3 text-slate-400" />
                  </>
                ) : (
                  <>
                    <Bot className="w-3 h-3 text-cyan-400" />
                    <span className="text-cyan-400">TopoGemma</span>
                    {msg.intent && (
                      <span className="px-1.5 py-0.2 rounded bg-slate-800 text-[9px] uppercase tracking-wider text-slate-400 font-mono">
                        {msg.intent}
                      </span>
                    )}
                  </>
                )}
              </div>

              <div
                className={`max-w-[90%] rounded-2xl p-3 text-xs leading-relaxed whitespace-pre-wrap ${
                  msg.role === 'user'
                    ? 'bg-cyan-600 text-white rounded-br-none shadow-md shadow-cyan-900/30 font-medium'
                    : 'bg-slate-800/90 text-slate-100 rounded-bl-none border border-slate-700/60 shadow-lg'
                }`}
              >
                {msg.content}

                {/* Sources Cited Pill Badges */}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 pt-2.5 border-t border-slate-700/60">
                    <div className="flex items-center gap-1 text-[10px] font-semibold text-cyan-300 mb-1.5">
                      <BookOpen className="w-3 h-3" />
                      <span>Knowledge Sources Consulted:</span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {msg.sources.map((src, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-0.5 rounded-md bg-slate-900/80 border border-slate-700 text-[10px] text-slate-300 font-mono"
                        >
                          {src}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {/* Loading Indicator for Local Model Thinking */}
        {isLoading && (
          <div className="flex flex-col items-start">
            <div className="flex items-center gap-1.5 mb-1 text-[10px] text-cyan-400 font-medium">
              <Bot className="w-3 h-3" />
              <span>TopoGemma Thinking</span>
            </div>
            <div className="bg-slate-800/80 border border-cyan-800/40 rounded-2xl rounded-bl-none p-3 flex items-center gap-2.5 shadow-lg">
              <Loader2 className="w-4 h-4 text-cyan-400 animate-spin" />
              <div className="text-xs text-slate-300">
                <span className="font-semibold text-cyan-300">Evaluating network constraints...</span>
                <p className="text-[10px] text-slate-400">Local Gemma 4 model inference in progress (5-30s)</p>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Box Form */}
      <form onSubmit={handleSubmit} className="p-3 border-t border-slate-800 bg-slate-950/70">
        <div className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type: 'Build a network with 3 routers and OSPF'..."
            disabled={isLoading}
            className="w-full pl-3.5 pr-10 py-2.5 text-xs bg-slate-900 border border-slate-700/80 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-1.5 p-1.5 bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-800 text-white disabled:text-slate-600 rounded-lg transition"
            title="Send Message"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </div>
      </form>
    </div>
  );
};
