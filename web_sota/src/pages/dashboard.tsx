import { Activity, Box, Cpu, HardDrive, Layers } from "lucide-react";
import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface HealthData {
  status: string;
  server: string;
  version: string;
  uptime_seconds?: number;
  tool_count?: number;
}

interface StatusData {
  uptime_seconds: number;
  tool_count: number;
  unity_editor: {
    running: boolean;
    processes: { pid: number; name: string }[];
  };
}

export function Dashboard() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [status, setStatus] = useState<StatusData | null>(null);

  useEffect(() => {
    fetch("/api/v1/health")
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => setHealth(d))
      .catch(() => {});
    fetch("/api/v1/status")
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => setStatus(d))
      .catch(() => {});
  }, []);

  return (
    <div className="space-y-6" data-testid="dashboard">
      <div className="flex items-center justify-between">
        <div>
          <h2
            className="text-2xl font-bold tracking-tight text-white"
            data-testid="dashboard-title"
          >
            Unity3D Dashboard
          </h2>
          <p className="text-slate-400">
            Engine telemetry and scene lifecycle status
          </p>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-slate-500">
          <span
            data-testid="backend-dot"
            className={`w-2 h-2 rounded-full ${health ? "bg-green-500" : "bg-gray-500"} animate-pulse`}
          />
          <span>{health ? "Connected" : "Connecting..."}</span>
        </div>
      </div>

      <div
        className="grid gap-4 md:grid-cols-2 lg:grid-cols-5"
        data-testid="kpi-grid"
      >
        <Card
          className="border-slate-800 bg-slate-950/50"
          data-testid="kpi-server"
        >
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              Server
            </CardTitle>
            <Activity className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {health ? `v${health.version}` : "..."}
            </div>
            <p className="text-xs text-slate-400">
              {health?.status || "Loading..."}
            </p>
          </CardContent>
        </Card>
        <Card
          className="border-slate-800 bg-slate-950/50"
          data-testid="kpi-tools"
        >
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              Tools
            </CardTitle>
            <Box className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {health?.tool_count ?? "..."}
            </div>
            <p className="text-xs text-slate-400">registered MCP tools</p>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              Active Scenes
            </CardTitle>
            <Layers className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {status?.unity_editor?.running ? "1" : "0"}
            </div>
            <p className="text-xs text-slate-400">
              {status?.unity_editor?.running
                ? "Editor connected"
                : "Editor not running"}
            </p>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              Unity Processes
            </CardTitle>
            <Cpu className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {status?.unity_editor?.processes?.length ?? "—"}
            </div>
            <p className="text-xs text-slate-400">
              {status?.unity_editor?.running
                ? "Editor active"
                : "No Editor process"}
            </p>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              Uptime
            </CardTitle>
            <HardDrive className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {status
                ? `${Math.floor((status.uptime_seconds || 0) / 60)}m`
                : "..."}
            </div>
            <p className="text-xs text-slate-400">Server running</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4 border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white">Console Output</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[200px] font-mono text-xs p-4 overflow-y-auto border border-slate-800 rounded-md bg-slate-900/50 text-slate-400 space-y-1">
              <p className="text-blue-400">
                [info] Server started at port 10831
              </p>
              <p className="text-blue-400">
                [info]{" "}
                {health
                  ? `${health.tool_count} MCP tools registered`
                  : "Loading tools..."}
              </p>
              <p className="text-emerald-400">[success] HTTP API available</p>
              {status?.unity_editor?.running ? (
                <p className="text-emerald-400">
                  [success] Unity Editor detected (
                  {status.unity_editor.processes.length} process
                  {status.unity_editor.processes.length !== 1 ? "es" : ""})
                </p>
              ) : (
                <p className="text-yellow-400">
                  [warn] Unity Editor not detected — start the Editor for scene
                  features
                </p>
              )}
              <div className="animate-pulse inline-block h-2 w-1 bg-slate-500 ml-1" />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
