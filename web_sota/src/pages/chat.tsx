import { useCallback, useEffect, useRef, useState } from "react";
import { Bot, Download, Eraser, Send, User } from "lucide-react";

const HISTORY_KEY = "unity3d-mcp-chat-history";
const PERSONALITY_KEY = "unity3d-mcp-chat-personality";
const MAX_HISTORY = 100;

const PERSONALITIES: Record<string, string> = {
	"Research Assistant": "You are a research assistant specializing in Unity 3D and avatar pipelines. Answer concisely with relevant technical details.",
	"Expert Reviewer": "You are a senior Unity developer reviewing projects and assets. Be critical and thorough.",
	"Quick Summarizer": "Keep responses to 2-3 sentences. Focus on key facts.",
	"Custom": "Custom prompt — editable below.",
};

interface Message {
	role: "user" | "assistant";
	content: string;
	ts?: string;
}

function loadHistory(): Message[] {
	try { const raw = localStorage.getItem(HISTORY_KEY); return raw ? JSON.parse(raw) : []; } catch { return []; }
}

function buildSystemPrompt(personalityId: string, customPrompt: string): string {
	const skill = "You have access to a Unity 3D automation server with 50+ tools: editor control, VRM avatars, VRChat upload, World Labs, model import, and motor control.";
	const role = PERSONALITIES[personalityId] || PERSONALITIES["Research Assistant"];
	if (personalityId === "Custom") return customPrompt || skill;
	return `${skill}\n\n---\n\n## Role\n${role}`;
}

export function Chat() {
	const [chat, setChat] = useState<Message[]>(() => loadHistory());
	const [input, setInput] = useState("");
	const [loading, setLoading] = useState(false);
	const [personality, setPersonality] = useState(() => localStorage.getItem(PERSONALITY_KEY) || "Research Assistant");
	const [customPrompt, setCustomPrompt] = useState("");
	const bottomRef = useRef<HTMLDivElement>(null);

	useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [chat]);

	const sendMessage = useCallback(async (prompt: string) => {
		const userMsg: Message = { role: "user", content: prompt, ts: new Date().toISOString() };
		setChat((prev) => { const next = [...prev, userMsg]; localStorage.setItem(HISTORY_KEY, JSON.stringify(next.slice(-MAX_HISTORY))); return next; });
		setLoading(true);
		try {
			const r = await fetch("/api/llm/chat", {
				method: "POST", headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ prompt, system: buildSystemPrompt(personality, customPrompt) }),
			});
			const data = await r.json();
			const reply = data.response || data.error || "No response";
			const assistantMsg: Message = { role: "assistant", content: reply, ts: new Date().toISOString() };
			setChat((prev) => { const next = [...prev, assistantMsg]; localStorage.setItem(HISTORY_KEY, JSON.stringify(next.slice(-MAX_HISTORY))); return next; });
		} catch (e) {
			setChat((prev) => { const next = [...prev, { role: "assistant" as const, content: String(e), ts: new Date().toISOString() }]; localStorage.setItem(HISTORY_KEY, JSON.stringify(next.slice(-MAX_HISTORY))); return next; });
		}
		setLoading(false);
	}, [personality, customPrompt]);

	const handleSend = () => { if (!input.trim()) return; sendMessage(input.trim()); setInput(""); };
	const handleClear = () => { setChat([]); localStorage.removeItem(HISTORY_KEY); };
	const handleExport = () => {
		if (chat.length === 0) return;
		const blob = new Blob([chat.map((m) => `[${m.ts || "no-ts"}] ${m.role}: ${m.content}`).join("\n")], { type: "text/plain" });
		const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = `unity3d-mcp-chat-${new Date().toISOString().slice(0, 10)}.txt`; a.click();
	};

	return (
		<div data-testid="chat-page" className="flex h-[calc(100vh-8rem)] flex-col space-y-4">
			<div className="flex items-center justify-between" data-testid="chat-controls">
				<div>
					<h2 className="text-2xl font-bold tracking-tight text-white">Command Interface</h2>
					<p className="text-slate-400">Natural language robot control (LLM)</p>
				</div>
				<div className="flex items-center gap-3">
					<select data-testid="personality-select" className="bg-slate-800 text-slate-200 border border-slate-700 rounded-lg px-3 py-1.5 text-sm" value={personality} onChange={(e) => { setPersonality(e.target.value); localStorage.setItem(PERSONALITY_KEY, e.target.value); }}>
						{Object.keys(PERSONALITIES).map((p) => <option key={p} value={p}>{p}</option>)}
					</select>
					<button data-testid="chat-export" onClick={handleExport} disabled={chat.length === 0} className="bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-300 text-xs px-3 py-1.5 rounded-lg border border-slate-700 flex items-center gap-1"><Download size={12} /> Export</button>
					<button data-testid="chat-clear" onClick={handleClear} disabled={chat.length === 0} className="bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-300 text-xs px-3 py-1.5 rounded-lg border border-slate-700 flex items-center gap-1"><Eraser size={12} /> Clear</button>
				</div>
			</div>

			{personality === "Custom" && (
				<textarea className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm" rows={2} placeholder="Enter your custom system prompt..." value={customPrompt} onChange={(e) => setCustomPrompt(e.target.value)} />
			)}

			<div data-testid="chat-messages" className="flex-1 overflow-y-auto space-y-4 pr-2">
				{chat.length === 0 && <div className="text-slate-500 text-sm text-center pt-12">Ask about Unity 3D tools, avatars, or pipelines.</div>}
				{chat.map((msg, i) => (
					<div key={i} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}>
						<div className={`flex gap-3 max-w-[80%] ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
							<div className={`h-8 w-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === "user" ? "bg-slate-800 border border-slate-700" : "bg-blue-900/20 border border-blue-800"}`}>
								{msg.role === "user" ? <User className="h-4 w-4 text-slate-400" /> : <Bot className="h-4 w-4 text-blue-400" />}
							</div>
							<div className={`rounded-xl px-4 py-2.5 text-sm leading-relaxed ${msg.role === "user" ? "bg-blue-600/20 text-slate-200" : "bg-slate-900/50 border border-slate-800 text-slate-300"}`}>
								{msg.content}
							</div>
						</div>
					</div>
				))}
				{loading && <div className="text-slate-500 text-sm animate-pulse pl-11">Thinking...</div>}
				<div ref={bottomRef} />
			</div>

			<div className="flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-xl px-4 py-3">
				<input data-testid="chat-input" type="text" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") handleSend(); }} placeholder="Ask about Unity 3D tools..." className="flex-1 bg-transparent text-sm text-slate-200 placeholder-slate-500 outline-none" />
				<button data-testid="chat-send" type="button" onClick={handleSend} disabled={loading || !input.trim()} className="w-9 h-9 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 flex items-center justify-center text-white transition-all"><Send size={14} /></button>
			</div>
		</div>
	);
}
