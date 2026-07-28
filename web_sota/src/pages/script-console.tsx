import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FileCode, History, Terminal, BookOpen } from "lucide-react";

interface ScriptData {
  available: boolean;
  snippets: { name: string; language: string }[];
  recent_executions: { method: string; args: string; timestamp: string }[];
}

export default function ScriptConsole() {
  const [data, setData] = useState<ScriptData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/editor/scripts")
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => setData(d))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-8rem)]">
        <div className="animate-pulse text-slate-600">Loading scripts...</div>
      </div>
    );
  }

  if (!data || !data.available) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-8rem)]">
        <div className="text-center max-w-md">
          <FileCode className="w-16 h-16 mx-auto text-slate-700 mb-4" />
          <h2 className="text-xl font-semibold text-slate-400 mb-2">Script Console</h2>
          <p className="text-sm text-slate-600">
            The script console requires a Unity Editor connection.
            Launch the Editor with the MCP bridge installed to access scripting tools.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-12 gap-6 h-[calc(100vh-8rem)]">
      <div className="col-span-3 flex flex-col gap-6">
        <Card className="flex-1 border-slate-800 bg-slate-950/50 overflow-hidden flex flex-col">
          <CardHeader className="p-4 border-b border-slate-800">
            <CardTitle className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <BookOpen className="h-3.5 w-3.5 text-blue-400" />
              Snippet Library
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0 overflow-auto">
            {data.snippets.map((s) => (
              <div key={s.name} className="flex items-center gap-3 px-4 py-3 hover:bg-slate-900 border-b border-slate-900/50 transition-colors">
                <FileCode className="h-3.5 w-3.5 text-slate-500" />
                <div>
                  <div className="text-xs font-medium text-slate-300">{s.name}</div>
                  <div className="text-[9px] text-slate-500 font-mono">{s.language}</div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
        <Card className="h-48 border-slate-800 bg-slate-950/50 flex flex-col">
          <CardHeader className="p-4 border-b border-slate-800">
            <CardTitle className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <History className="h-3.5 w-3.5 text-yellow-500" />
              Run History
            </CardTitle>
          </CardHeader>
          <CardContent className="p-2 space-y-1 overflow-auto font-mono text-[9px]">
            {data.recent_executions.map((ex, i) => (
              <div key={i} className="p-2 rounded hover:bg-white/5 text-slate-400">
                <span className="text-emerald-500">{ex.method}</span>{ex.args} — {ex.timestamp}
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
      <div className="col-span-9 flex flex-col gap-6">
        <Card className="flex-1 border-slate-800 bg-slate-950/50 flex flex-col">
          <CardHeader className="flex flex-row items-center justify-between py-2 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="bg-blue-500/10 text-blue-400 border-blue-500/20 text-[10px] h-5">Editor Script</Badge>
              <span className="text-xs font-mono text-slate-300">Script_01.cs</span>
            </div>
          </CardHeader>
          <CardContent className="flex-1 p-0 overflow-hidden">
            <div className="h-full bg-black/40 p-4 font-mono text-sm leading-relaxed text-blue-400/90 whitespace-pre">
{`using UnityEditor;
using UnityEngine;

public class MCPBridge {
    [MenuItem("MCP/Run")]
    public static void Run() {
        Debug.Log("Unity Editor connected via MCP bridge");
    }
}`}
            </div>
          </CardContent>
        </Card>
        <Card className="h-48 border-slate-800 bg-slate-950/50 flex flex-col overflow-hidden">
          <CardHeader className="flex flex-row items-center justify-between py-2 border-b border-slate-800 bg-slate-900/50">
            <div className="flex items-center gap-2">
              <Terminal className="h-3.5 w-3.5 text-emerald-500" />
              <span className="text-[10px] font-bold uppercase text-slate-400">Console Output</span>
            </div>
          </CardHeader>
          <CardContent className="p-3 font-mono text-[11px] space-y-1 overflow-auto">
            <div className="flex gap-2 text-slate-500">
              <span className="text-slate-600">[info]</span>
              <span className="text-blue-500">INFO:</span> MCP bridge connected
            </div>
            <div className="flex gap-2 text-slate-500">
              <span className="text-slate-600">[info]</span>
              <span className="text-emerald-500">SUCCESS:</span> {data.snippets.length} scripts available
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
