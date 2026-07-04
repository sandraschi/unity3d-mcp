import { useEffect, useState } from "react";
import { Activity, Box, Cpu, HardDrive, Layers } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface HealthData {
	status: string;
	server: string;
	version: string;
	uptime_seconds?: number;
	tool_count?: number;
}

export function Dashboard() {
	const [health, setHealth] = useState<HealthData | null>(null);

	useEffect(() => {
		fetch("/api/v1/health")
			.then((r) => r.ok ? r.json() : null)
			.then((d) => setHealth(d))
			.catch(() => {});
	}, []);

	return (
		<div className="space-y-6" data-testid="dashboard">
			<div className="flex items-center justify-between">
				<div>
					<h2 className="text-2xl font-bold tracking-tight text-white" data-testid="dashboard-title">Unity3D Dashboard</h2>
					<p className="text-slate-400">Engine telemetry and scene lifecycle status</p>
				</div>
				<div className="flex items-center gap-1.5 text-xs text-slate-500">
					<span id="backend-dot" data-testid="backend-dot" className={`w-2 h-2 rounded-full ${health ? "bg-green-500" : "bg-gray-500"} animate-pulse`} />
					<span>{health ? "Connected" : "Connecting..."}</span>
				</div>
			</div>

			<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5" data-testid="kpi-grid">
				<Card className="border-slate-800 bg-slate-950/50" data-testid="kpi-server">
					<CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
						<CardTitle className="text-sm font-medium text-slate-200">Server</CardTitle>
						<Activity className="h-4 w-4 text-emerald-500" />
					</CardHeader>
					<CardContent>
						<div className="text-2xl font-bold text-white">{health ? `v${health.version}` : "..."}</div>
						<p className="text-xs text-slate-400">{health?.status || "Loading..."}</p>
					</CardContent>
				</Card>
				<Card className="border-slate-800 bg-slate-950/50" data-testid="kpi-tools">
					<CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
						<CardTitle className="text-sm font-medium text-slate-200">Tools</CardTitle>
						<Box className="h-4 w-4 text-blue-500" />
					</CardHeader>
					<CardContent>
						<div className="text-2xl font-bold text-white">{health?.tool_count ?? "..."}</div>
						<p className="text-xs text-slate-400">registered MCP tools</p>
					</CardContent>
				</Card>
				<Card className="border-slate-800 bg-slate-950/50">
					<CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
						<CardTitle className="text-sm font-medium text-slate-200">Active Scenes</CardTitle>
						<Layers className="h-4 w-4 text-emerald-500" />
					</CardHeader>
					<CardContent>
						<div className="text-2xl font-bold text-white">4</div>
						<p className="text-xs text-slate-400">2 Loaded | 2 Background</p>
					</CardContent>
				</Card>
				<Card className="border-slate-800 bg-slate-950/50">
					<CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
						<CardTitle className="text-sm font-medium text-slate-200">VRAM Usage</CardTitle>
						<Cpu className="h-4 w-4 text-purple-500" />
					</CardHeader>
					<CardContent>
						<div className="text-2xl font-bold text-white">2.4GB</div>
						<p className="text-xs text-slate-400">Of 24GB available</p>
					</CardContent>
				</Card>
				<Card className="border-slate-800 bg-slate-950/50">
					<CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
						<CardTitle className="text-sm font-medium text-slate-200">Bridge Port</CardTitle>
						<HardDrive className="h-4 w-4 text-orange-500" />
					</CardHeader>
					<CardContent>
						<div className="text-2xl font-bold text-white">10831</div>
						<p className="text-xs text-slate-400">Editor Bridge Active</p>
					</CardContent>
				</Card>
			</div>

			<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
				<Card className="col-span-4 border-slate-800 bg-slate-950/50">
					<CardHeader><CardTitle className="text-white">Console Output</CardTitle></CardHeader>
					<CardContent>
						<div className="h-[200px] font-mono text-xs p-4 overflow-y-auto border border-slate-800 rounded-md bg-slate-900/50 text-slate-400 space-y-1">
							<p className="text-blue-400">[info] Unity Editor connected via MCP</p>
							<p>[debug] Scanning hierarchy for GameObjects...</p>
							<p>[info] Found 12,452 vertices in current frustum</p>
							<p className="text-emerald-400">[success] Asset bundle synchronization complete</p>
							<div className="animate-pulse inline-block h-2 w-1 bg-slate-500 ml-1" />
						</div>
					</CardContent>
				</Card>
				<Card className="col-span-3 border-slate-800 bg-slate-950/50">
					<CardHeader><CardTitle className="text-white">Active Worlds</CardTitle></CardHeader>
					<CardContent>
						<div className="space-y-4">
							<div className="flex items-center">
								<Box className="h-4 w-4 text-blue-400 mr-2" />
								<div className="ml-2 space-y-1">
									<p className="text-sm font-medium leading-none text-white">Stroheckgasse_Living</p>
									<p className="text-xs text-slate-400">Active Scene • High Quality</p>
								</div>
							</div>
							<div className="flex items-center">
								<Box className="h-4 w-4 text-slate-600 mr-2" />
								<div className="ml-2 space-y-1">
									<p className="text-sm font-medium leading-none text-white text-opacity-50">Lobby_Virtual</p>
									<p className="text-xs text-slate-500">Unloaded • Ready for bake</p>
								</div>
							</div>
						</div>
					</CardContent>
				</Card>
			</div>
		</div>
	);
}
