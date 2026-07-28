import { useEffect, useState } from 'react';
import { Activity, Cpu, HardDrive, Network, Server } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface StatusData {
  uptime_seconds: number;
  tool_count: number;
  unity_editor: {
    running: boolean;
    processes: { pid: number; name: string; running_seconds: number }[];
    installed_versions: string[];
    project_configured: boolean;
  };
  system: { platform: string; python_version: string };
}

export function Status() {
  const [data, setData] = useState<StatusData | null>(null);

  useEffect(() => {
    fetch('/api/v1/status').then(r => r.ok ? r.json() : null).then(d => setData(d)).catch(() => {});
  }, []);

  const editor = data?.unity_editor;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">System Status</h1>
        <p className="text-slate-400">Health monitoring for Unity3D-MCP.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">CPU Usage</CardTitle>
            <Cpu className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{editor?.running ? "Active" : "Idle"}</div>
            <p className="text-xs text-slate-500">{editor?.running ? `${editor.processes.length} Unity process${editor.processes.length !== 1 ? "es" : ""}` : "Unity Editor not running"}</p>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Bridge Status</CardTitle>
            <Network className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{data ? "Online" : "..."}</div>
            <p className="text-xs text-slate-500">FastMCP :10831</p>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">MCP Tools</CardTitle>
            <HardDrive className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{data?.tool_count ?? "..."}</div>
            <p className="text-xs text-slate-500">Registered tools</p>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Uptime</CardTitle>
            <Activity className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {data ? `${Math.floor((data.uptime_seconds || 0) / 60)}m ${(data.uptime_seconds || 0) % 60}s` : "..."}
            </div>
            <p className="text-xs text-slate-500">Server online</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader><CardTitle className="text-white flex items-center gap-2"><Server className="h-4 w-4" /> Unity Editor</CardTitle></CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex justify-between"><span className="text-slate-400">Running</span><span className={editor?.running ? "text-emerald-400" : "text-slate-500"}>{editor?.running ? "Yes" : "No"}</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Processes</span><span className="text-slate-200">{editor?.processes?.length ?? "—"}</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Installed Versions</span><span className="text-slate-200">{editor?.installed_versions?.join(", ") || "None detected"}</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Project Configured</span><span className={editor?.project_configured ? "text-emerald-400" : "text-slate-500"}>{editor?.project_configured ? "Yes" : "No"}</span></div>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader><CardTitle className="text-white flex items-center gap-2"><Cpu className="h-4 w-4" /> System</CardTitle></CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex justify-between"><span className="text-slate-400">Platform</span><span className="text-slate-200">{data?.system?.platform || "..."}</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Python</span><span className="text-slate-200">{data?.system?.python_version || "..."}</span></div>
            <div className="flex justify-between"><span className="text-slate-400">API</span><span className="text-slate-200">FastAPI /docs</span></div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
