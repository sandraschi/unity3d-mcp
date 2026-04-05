import { Activity, Cpu, HardDrive, Network } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function Status() {
    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-white">System Status</h1>
                <p className="text-slate-400">Real-time health monitoring for Unity3D-MCP.</p>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">CPU Usage</CardTitle>
                        <Cpu className="h-4 w-4 text-blue-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">24.1%</div>
                        <p className="text-xs text-slate-500">Unity Editor active</p>
                    </CardContent>
                </Card>
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">Bridge Latency</CardTitle>
                        <Network className="h-4 w-4 text-emerald-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">15ms</div>
                        <p className="text-xs text-slate-500">FastMCP Sync</p>
                    </CardContent>
                </Card>
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">Project Assets</CardTitle>
                        <HardDrive className="h-4 w-4 text-orange-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">4.2TB</div>
                        <p className="text-xs text-slate-500">Asset database size</p>
                    </CardContent>
                </Card>
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">Uptime</CardTitle>
                        <Activity className="h-4 w-4 text-purple-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">100%</div>
                        <p className="text-xs text-slate-500">Continuous operation</p>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
