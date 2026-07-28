import { Bot, Download, Eraser, Send, User } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";

const HISTORY_KEY = "unity3d-mcp-chat-history";
const PERSONALITY_KEY = "unity3d-mcp-chat-personality";
const MAX_HISTORY = 100;

const PERSONALITIES: Record<string, string> = {
  "Research Assistant":
    "You are a research assistant specializing in Unity 3D and avatar pipelines. Answer concisely with relevant technical details.",
  "Expert Reviewer":
    "You are a senior Unity developer reviewing projects and assets. Be critical and thorough.",
  "Quick Summarizer": "Keep responses to 2-3 sentences. Focus on key facts.",
  Custom: "Custom prompt — editable below.",
};

const EXAMPLE_PROMPTS = [
  {
    group: "Editor",
    prompts: [
      "How do I launch the Unity Editor?",
      "Create a new 3D project",
      "Import an FBX model and set up materials",
    ],
  },
  {
    group: "Avatars",
    prompts: [
      "Import a VRM avatar and rig it",
      "Optimize a model for VRChat",
      "Set up avatar animations",
    ],
  },
  {
    group: "Pipeline",
    prompts: [
      "Build and export the project",
      "Upload a VRChat avatar",
      "Generate a game build plan",
    ],
  },
];

interface Message {
  role: "user" | "assistant";
  content: string;
  ts?: string;
}

function loadHistory(): Message[] {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function buildSystemPrompt(
  personalityId: string,
  customPrompt: string,
): string {
  const skill =
    "You have access to a Unity 3D automation server with 50+ tools: editor control, VRM avatars, VRChat upload, World Labs, model import, and motor control.";
  const role =
    PERSONALITIES[personalityId] || PERSONALITIES["Research Assistant"];
  if (personalityId === "Custom") return customPrompt || skill;
  return `${skill}\n\n---\n\n## Role\n${role}`;
}

export function Chat() {
  const [chat, setChat] = useState<Message[]>(() => loadHistory());
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [personality, setPersonality] = useState(
    () => localStorage.getItem(PERSONALITY_KEY) || "Research Assistant",
  );
  const [customPrompt, setCustomPrompt] = useState("");
  const [skillName, setSkillName] = useState<string | null>(null);
  const [providerOk, setProviderOk] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat]);

  // Skill fetch
  useEffect(() => {
    (async () => {
      try {
        const r = await fetch("/api/v1/skills");
        if (r.ok) {
          const data = await r.json();
          const skills = data?.skills ?? [];
          if (skills.length > 0) setSkillName(skills[0].name || skills[0]);
        }
      } catch {
        /* no skills */
      }
    })();
  }, []);

  // Provider detection
  useEffect(() => {
    (async () => {
      try {
        const r = await fetch("http://localhost:11434/api/tags", {
          signal: AbortSignal.timeout(3000),
        });
        setProviderOk(r.ok);
      } catch {
        /* stays optimistic */
      }
    })();
  }, []);

  const sendMessage = useCallback(
    async (text: string) => {
      if (!text.trim() || streaming) return;
      const userMsg: Message = {
        role: "user",
        content: text.trim(),
        ts: new Date().toISOString(),
      };
      const updated = [...chat, userMsg].slice(-MAX_HISTORY);
      setChat(updated);
      setStreaming(true);

      try {
        const r = await fetch("/api/llm/chat/stream", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            prompt: text.trim(),
            system: buildSystemPrompt(personality, customPrompt),
            messages: chat
              .slice(-20)
              .map((m) => ({ role: m.role, content: m.content })),
          }),
        });
        if (!r.ok || !r.body) throw new Error(`HTTP ${r.status}`);

        const partial: Message = {
          role: "assistant",
          content: "",
          ts: new Date().toISOString(),
        };
        setChat((prev) => [...prev, partial]);

        const reader = r.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";
          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;
            const data = line.slice(6).trim();
            if (data === "[DONE]") break;
            try {
              const parsed = JSON.parse(data);
              if (parsed.c) {
                partial.content += parsed.c;
                setChat((prev) => {
                  const c = [...prev];
                  c[c.length - 1] = { ...partial };
                  return c;
                });
              }
              if (parsed.error) throw new Error(parsed.error);
            } catch {
              /* skip */
            }
          }
        }
        const final = [...chat, userMsg, { ...partial }].slice(-MAX_HISTORY);
        setChat(final);
        localStorage.setItem(HISTORY_KEY, JSON.stringify(final));
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        const final = [
          ...updated,
          {
            role: "assistant" as const,
            content: `Error: ${msg}`,
            ts: new Date().toISOString(),
          },
        ].slice(-MAX_HISTORY);
        setChat(final);
        localStorage.setItem(HISTORY_KEY, JSON.stringify(final));
      }
      setStreaming(false);
    },
    [input, chat, streaming, personality, customPrompt],
  );

  const handleSend = () => {
    if (!input.trim()) return;
    sendMessage(input.trim());
    setInput("");
  };
  const handleClear = () => {
    setChat([]);
    localStorage.removeItem(HISTORY_KEY);
  };
  const handleExport = () => {
    if (chat.length === 0) return;
    const lines = chat.map(
      (m) =>
        `[${m.ts || "no-ts"}] ${m.role === "user" ? "You" : "AI"}: ${m.content}`,
    );
    const blob = new Blob([lines.join("\n\n---\n\n")], { type: "text/plain" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `unity3d-mcp-chat-${new Date().toISOString().slice(0, 10)}.txt`;
    a.click();
  };

  return (
    <div
      data-testid="chat-page"
      className="flex h-[calc(100vh-8rem)] flex-col space-y-4"
    >
      <div
        className="flex items-center justify-between"
        data-testid="chat-controls"
      >
        <div className="flex items-center gap-3">
          <h2 className="text-2xl font-bold tracking-tight text-white">
            Command Interface
          </h2>
          {skillName && (
            <span className="text-[10px] text-zinc-500 bg-zinc-800 px-1.5 py-0.5 rounded font-mono">
              skill:{skillName}
            </span>
          )}
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs text-zinc-500">
            <div
              className={`w-1.5 h-1.5 rounded-full ${providerOk ? "bg-green-500" : "bg-red-500"}`}
            />
            <span>{providerOk ? "Ollama" : "offline"}</span>
          </div>
          <select
            data-testid="personality-select"
            className="bg-slate-800 text-slate-200 border border-slate-700 rounded-lg px-3 py-1.5 text-sm"
            value={personality}
            onChange={(e) => {
              setPersonality(e.target.value);
              localStorage.setItem(PERSONALITY_KEY, e.target.value);
            }}
          >
            {Object.keys(PERSONALITIES).map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
          <button
            data-testid="chat-export"
            onClick={handleExport}
            disabled={chat.length === 0}
            className="bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-300 text-xs px-3 py-1.5 rounded-lg border border-slate-700 flex items-center gap-1"
          >
            <Download size={12} /> Export
          </button>
          <button
            data-testid="chat-clear"
            onClick={handleClear}
            disabled={chat.length === 0}
            className="bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-300 text-xs px-3 py-1.5 rounded-lg border border-slate-700 flex items-center gap-1"
          >
            <Eraser size={12} /> Clear
          </button>
        </div>
      </div>

      {personality === "Custom" && (
        <textarea
          className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm"
          rows={2}
          placeholder="Enter your custom system prompt..."
          value={customPrompt}
          onChange={(e) => setCustomPrompt(e.target.value)}
        />
      )}

      <div
        data-testid="chat-messages"
        className="flex-1 overflow-y-auto space-y-4 pr-2"
      >
        {chat.length === 0 && (
          <div className="text-slate-500 text-sm text-center pt-8">
            <Bot className="w-12 h-12 mx-auto mb-3 opacity-20" />
            <p>Ask about Unity 3D tools, avatars, or pipelines.</p>
            <p className="text-xs text-slate-600 mt-1">
              Personality: {personality}
              {skillName && ` | skill: ${skillName}`}
            </p>
            <div
              data-testid="example-prompts"
              className="mt-6 max-w-lg mx-auto space-y-3"
            >
              {EXAMPLE_PROMPTS.map((group) => (
                <div key={group.group}>
                  <p className="text-[10px] uppercase tracking-wider text-slate-600 text-left mb-1.5 px-1">
                    {group.group}
                  </p>
                  <div className="flex flex-wrap gap-1.5 justify-center">
                    {group.prompts.map((p) => (
                      <button
                        key={p}
                        onClick={() => setInput(p)}
                        className="text-xs px-2.5 py-1.5 rounded-lg border border-slate-700 bg-slate-800/50 hover:bg-slate-700/50 text-slate-400 hover:text-slate-200 transition-colors text-left"
                      >
                        {p}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        {chat.map((msg, i) => (
          <div
            key={i}
            className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}
          >
            <div
              className={`flex gap-3 max-w-[80%] ${msg.role === "user" ? "flex-row-reverse" : ""}`}
            >
              <div
                className={`h-8 w-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === "user" ? "bg-slate-800 border border-slate-700" : "bg-blue-900/20 border border-blue-800"}`}
              >
                {msg.role === "user" ? (
                  <User className="h-4 w-4 text-slate-400" />
                ) : (
                  <Bot className="h-4 w-4 text-blue-400" />
                )}
              </div>
              <div
                className={`rounded-xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap ${msg.role === "user" ? "bg-blue-600/20 text-slate-200" : "bg-slate-900/50 border border-slate-800 text-slate-300"}`}
              >
                {msg.content ||
                  (i === chat.length - 1 && streaming ? (
                    <span className="animate-pulse">...</span>
                  ) : (
                    ""
                  ))}
              </div>
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-xl px-4 py-3">
        <input
          data-testid="chat-input"
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          placeholder="Ask about Unity 3D tools..."
          disabled={streaming}
          className="flex-1 bg-transparent text-sm text-slate-200 placeholder-slate-500 outline-none disabled:opacity-50"
        />
        <button
          data-testid="chat-send"
          type="button"
          onClick={handleSend}
          disabled={streaming || !input.trim()}
          className="w-9 h-9 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 flex items-center justify-center text-white transition-all"
        >
          <Send size={14} />
        </button>
      </div>
    </div>
  );
}
