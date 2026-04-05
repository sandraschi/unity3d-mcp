import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
    Package,
    Download,
    Trash2,
    RefreshCw,
    ExternalLink,
    ShieldCheck,
    History,
    Search,
    Box
} from "lucide-react";

export default function PluginManager() {
    return (
        <div className="space-y-6 text-slate-200">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Plugin & Package Manager</h2>
                    <p className="text-slate-400">Manage Unity Package Manager (UPM) and custom MCP extensions</p>
                </div>
                <Button className="bg-blue-600 hover:bg-blue-700 text-white">
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Check for Updates
                </Button>
            </div>

            <div className="grid gap-6 md:grid-cols-4">
                <StatCard label="Installed Packages" value="42" icon={<Package className="h-4 w-4 text-blue-400" />} />
                <StatCard label="Custom Plugins" value="12" icon={<Box className="h-4 w-4 text-emerald-400" />} />
                <StatCard label="Pending Updates" value="3" icon={<Download className="h-4 w-4 text-yellow-400" />} />
                <StatCard label="Security Checks" value="Passed" icon={<ShieldCheck className="h-4 w-4 text-emerald-500" />} />
            </div>

            <div className="grid grid-cols-12 gap-6">
                <div className="col-span-8">
                    <Card className="border-slate-800 bg-slate-950/50">
                        <CardHeader className="p-4 border-b border-slate-800 flex flex-row items-center justify-between bg-slate-900/30">
                            <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-400">Active Packages</CardTitle>
                            <div className="relative">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3 w-3 text-slate-500" />
                                <input
                                    placeholder="Filter packages..."
                                    className="bg-slate-900 border border-slate-800 rounded px-8 py-1.5 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-blue-500"
                                />
                            </div>
                        </CardHeader>
                        <CardContent className="p-0">
                            <PackageItem
                                name="com.unity.vrm"
                                version="0.108.2"
                                publisher="VRM Consortium"
                                status="up-to-date"
                            />
                            <PackageItem
                                name="com.vrchat.avatars"
                                version="3.6.1"
                                publisher="VRChat Inc."
                                status="update-available"
                                newVersion="3.7.0"
                            />
                            <PackageItem
                                name="com.google.gemini"
                                version="1.0.0-beta"
                                publisher="Google DeepMind"
                                status="beta"
                                description="Advanced AI bridge for Unity Editor."
                            />
                            <PackageItem
                                name="mcp-unity-bridge"
                                version="2.14.3"
                                publisher="Sandra Schipal"
                                status="up-to-date"
                                description="SOTA standard bridge for agentic orchestration."
                            />
                        </CardContent>
                    </Card>
                </div>

                <div className="col-span-4 space-y-6">
                    <Card className="border-slate-800 bg-slate-950/50">
                        <CardHeader className="p-4 border-b border-slate-800">
                            <CardTitle className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                                <History className="h-3.5 w-3.5" />
                                Recent Operations
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="p-4 space-y-4">
                            <HistoryItem
                                type="install"
                                label="com.unity.vrm"
                                time="15m ago"
                            />
                            <HistoryItem
                                type="update"
                                label="mcp-unity-bridge"
                                time="2h ago"
                            />
                            <HistoryItem
                                type="remove"
                                label="legacy-input-system"
                                time="Yesterday"
                            />
                        </CardContent>
                    </Card>

                    <Card className="border-slate-800 bg-blue-600/10 border-blue-500/20">
                        <CardContent className="p-4 text-center space-y-3">
                            <Box className="h-8 w-8 text-blue-400 mx-auto" />
                            <div className="space-y-1">
                                <h4 className="text-sm font-bold text-slate-200">Export All Extensions</h4>
                                <p className="text-[10px] text-slate-400 leading-relaxed">Create a portable setup for remote deployment</p>
                            </div>
                            <Button size="sm" className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold h-8 text-[10px]">
                                CREATE BUNDLE
                            </Button>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}

function StatCard({ label, value, icon }: { label: string, value: string, icon: React.ReactNode }) {
    return (
        <Card className="border-slate-800 bg-slate-950/50">
            <CardContent className="p-4">
                <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">{label}</span>
                    {icon}
                </div>
                <div className="text-2xl font-bold text-slate-200">{value}</div>
            </CardContent>
        </Card>
    );
}

function PackageItem({ name, version, publisher, status, newVersion, description }: any) {
    return (
        <div className="p-4 hover:bg-slate-900 border-b border-slate-900 transition-colors flex items-center justify-between">
            <div className="space-y-1">
                <div className="flex items-center gap-3">
                    <h4 className="text-sm font-bold font-mono text-slate-200">{name}</h4>
                    <span className="text-[10px] font-medium text-slate-500">v{version}</span>
                    <Badge variant="outline" className={`text-[10px] h-4 border-slate-800 ${status === 'update-available' ? 'bg-yellow-500/10 text-yellow-500' : 'bg-slate-800 text-slate-400'}`}>
                        {status.replace('-', ' ')}
                    </Badge>
                </div>
                <div className="flex items-center gap-2 text-[10px] text-slate-500">
                    <span>{publisher}</span>
                    {description && (
                        <>
                            <span>•</span>
                            <span>{description}</span>
                        </>
                    )}
                </div>
            </div>
            <div className="flex gap-2">
                {status === 'update-available' && (
                    <Button size="sm" className="h-7 text-[10px] bg-emerald-600 hover:bg-emerald-700 text-white">
                        UPDATE TO {newVersion}
                    </Button>
                )}
                <Button variant="ghost" size="icon" className="h-7 w-7 text-slate-500">
                    <ExternalLink className="h-3.5 w-3.5" />
                </Button>
                <Button variant="ghost" size="icon" className="h-7 w-7 hover:bg-red-900/20 hover:text-red-500">
                    <Trash2 className="h-3.5 w-3.5" />
                </Button>
            </div>
        </div>
    );
}

function HistoryItem({ type, label, time }: any) {
    const getColors = () => {
        switch (type) {
            case 'install': return 'text-emerald-500';
            case 'update': return 'text-blue-500';
            default: return 'text-red-500';
        }
    };

    return (
        <div className="flex items-center justify-between text-[11px]">
            <div className="flex items-center gap-2">
                <div className={`w-1 h-3 rounded-full ${getColors()} bg-current`} />
                <span className="font-medium text-slate-300 capitalize">{type}:</span>
                <span className="text-slate-500 font-mono truncate max-w-[120px]">{label}</span>
            </div>
            <span className="text-slate-600">{time}</span>
        </div>
    );
}
