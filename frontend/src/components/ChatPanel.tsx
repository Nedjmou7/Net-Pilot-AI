import React, { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Sparkles, BookOpen, Trash2, WandSparkles } from "lucide-react";

export interface MessageItem {
  id: string;
  sender: "user" | "gemma";
  content: string;
  intent?: "build" | "question" | "troubleshoot";
  sources?: string[];
  timestamp: string;
}

interface ChatPanelProps {
  messages: MessageItem[];
  isLoading: boolean;
  onSendMessage: (msg: string) => void;
  onClearChat: () => void;
}

const EXAMPLE_PROMPTS = [
  "Build a network with 3 routers and OSPF",
  "Create 2 VLANs with inter-VLAN routing",
  "Why can't my PC ping the gateway?",
  "Setup 1 router, 1 switch, 2 PCs with DHCP"
];

export const ChatPanel: React.FC<ChatPanelProps> = ({ messages, isLoading, onSendMessage, onClearChat }) => {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput("");
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 border-r border-slate-800">
      {/* Panel Header */}
      <div className="px-4 py-3 border-b border-slate-800 flex items-center justify-between bg-slate-900/60 backdrop-blur">
        <div className="flex items-center space-x-2">
          <div className="p-1 rounded-md bg-sky-500/10 text-sky-400">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-slate-100">Gemma Assistant</h2>
            <p className="text-[11px] text-slate-400">100% Local Packet Tracer AI</p>
          </div>
        </div>
        <button
          onClick={onClearChat}
          disabled={isLoading}
          title="Clear conversation"
          className="flex items-center gap-1.5 rounded-lg border border-slate-700 px-2 py-1.5 text-[11px] text-slate-400 transition-colors hover:border-slate-600 hover:bg-slate-800 hover:text-slate-200 disabled:cursor-not-allowed disabled:opacity-40"
        >
          <Trash2 className="h-3.5 w-3.5" />
          <span>Clear</span>
        </button>
      </div>

      {/* Messages List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="h-full flex flex-col justify-center items-center text-center px-4 py-8">
            <div className="w-12 h-12 rounded-full bg-sky-500/10 text-sky-400 flex items-center justify-center mb-3">
              <Sparkles className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-medium text-slate-200 mb-1">What network do you want to build?</h3>
            <p className="text-xs text-slate-400 mb-6 max-w-xs">
              Describe a topology to generate it instantly, or ask Cisco CCNA troubleshooting questions.
            </p>

            <div className="w-full space-y-2">
              <span className="text-[11px] font-medium uppercase tracking-wider text-slate-500 block mb-1">
                Suggested Prompts
              </span>
              {EXAMPLE_PROMPTS.map((prompt, idx) => (
                <button
                  key={idx}
                  onClick={() => onSendMessage(prompt)}
                  className="w-full text-left text-xs bg-slate-800/60 hover:bg-slate-800 hover:border-sky-500/50 border border-slate-700/60 rounded-lg p-2.5 text-slate-300 transition-all duration-150 flex items-center justify-between group"
                >
                  <span className="truncate">{prompt}</span>
                  <WandSparkles className="h-3.5 w-3.5 text-slate-500 group-hover:text-sky-400" />
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${msg.sender === "user" ? "items-end" : "items-start"}`}
          >
            <div className="flex items-start space-x-2 max-w-[90%]">
              {msg.sender === "gemma" && (
                <div className="w-6 h-6 rounded-md bg-sky-600/20 text-sky-400 flex items-center justify-center shrink-0 mt-0.5">
                  <Bot className="w-3.5 h-3.5" />
                </div>
              )}
              <div
                className={`rounded-2xl px-3.5 py-2.5 text-xs leading-relaxed ${
                  msg.sender === "user"
                    ? "bg-sky-600 text-white rounded-br-sm shadow-md shadow-sky-600/10"
                    : "bg-slate-800/90 text-slate-200 border border-slate-700/80 rounded-bl-sm"
                }`}
              >
                <div className="whitespace-pre-wrap">{msg.content}</div>

                {/* Cited Sources Badge */}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-2.5 pt-2 border-t border-slate-700/60 flex flex-wrap gap-1">
                    <span className="text-[10px] text-slate-400 flex items-center mr-1">
                      <BookOpen className="w-3 h-3 mr-1 text-sky-400" />
                      Sources:
                    </span>
                    {msg.sources.map((src, i) => (
                      <span
                        key={i}
                        className="text-[10px] font-mono bg-slate-900/80 text-sky-300 px-1.5 py-0.5 rounded border border-slate-700/80"
                      >
                        {src}
                      </span>
                    ))}
                  </div>
                )}
              </div>
              {msg.sender === "user" && (
                <div className="w-6 h-6 rounded-md bg-slate-700 text-slate-300 flex items-center justify-center shrink-0 mt-0.5">
                  <User className="w-3.5 h-3.5" />
                </div>
              )}
            </div>
            <span className="text-[9px] text-slate-500 mt-1 px-1">{msg.timestamp}</span>
          </div>
        ))}

        {/* Loading Spinner */}
        {isLoading && (
          <div className="flex items-start space-x-2">
            <div className="w-6 h-6 rounded-md bg-sky-600/20 text-sky-400 flex items-center justify-center shrink-0 mt-0.5">
              <Bot className="w-3.5 h-3.5" />
            </div>
            <div className="bg-slate-800/90 text-slate-300 border border-slate-700/80 rounded-2xl rounded-bl-sm px-4 py-3 flex items-center space-x-2 text-xs">
              <div className="flex space-x-1">
                <div className="w-2 h-2 rounded-full bg-sky-400 animate-bounce" style={{ animationDelay: "0ms" }}></div>
                <div className="w-2 h-2 rounded-full bg-sky-400 animate-bounce" style={{ animationDelay: "150ms" }}></div>
                <div className="w-2 h-2 rounded-full bg-sky-400 animate-bounce" style={{ animationDelay: "300ms" }}></div>
              </div>
              <span className="text-slate-400 font-mono text-[11px] pl-1">Gemma is analyzing network requirements...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Prompt chips when messages exist */}
      {messages.length > 0 && (
        <div className="px-3 py-1.5 border-t border-slate-800/60 flex space-x-1.5 overflow-x-auto bg-slate-950/40">
          {EXAMPLE_PROMPTS.slice(0, 3).map((prompt, idx) => (
            <button
              key={idx}
              onClick={() => onSendMessage(prompt)}
              className="text-[10px] text-slate-400 hover:text-sky-300 bg-slate-800/80 hover:bg-slate-800 px-2.5 py-1 rounded-full whitespace-nowrap border border-slate-700/60 transition-colors"
            >
              {prompt}
            </button>
          ))}
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="p-3 border-t border-slate-800 bg-slate-900/80">
        <div className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Build 3 routers with OSPF... or ask a question"
            disabled={isLoading}
            className="w-full bg-slate-950 text-slate-100 text-xs rounded-xl pl-3.5 pr-10 py-3 border border-slate-700 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 placeholder-slate-500 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-2 p-1.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white disabled:opacity-40 disabled:hover:bg-sky-600 transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
};
