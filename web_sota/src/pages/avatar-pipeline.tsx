import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
    CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import {
    User,
    Upload,
    CheckCircle2,
    Zap,
    Scale,
    Activity,
    Smartphone,
    Monitor,
    ShieldCheck
} from "lucide-react";

export default function AvatarPipeline() {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Avatar Pipeline</h2>
                    <p className="text-slate-400">Optimize and deploy VRM avatars to VRChat</p>
                </div>
                <div className="flex gap-3">
                    <Button variant="outline" className="border-slate-800 bg-slate-900/50 hover:bg-slate-800">
                        <Activity className="mr-2 h-4 w-4" />
                        Run Validation
                    </Button>
                    <Button className="bg-emerald-600 hover:bg-emerald-700 text-white shadow-lg shadow-emerald-900/20">
                        <Upload className="mr-2 h-4 w-4" />
                        Deploy to VRChat
                    </Button>
                </div>
            </div>

            <div className="grid gap-6 md:grid-cols-3">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="pb-2">
                        <div className="flex items-center justify-between">
                            <CardTitle className="text-sm font-medium text-slate-400">VRChat Status</CardTitle>
                            <User className="h-4 w-4 text-blue-400" />
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-center gap-2 mb-2">
                            <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                            <span className="text-lg font-bold text-slate-200">Sandra_VR</span>
                        </div>
                        <Badge variant="outline" className="bg-emerald-500/10 text-emerald-500 border-emerald-500/20 text-[10px]">Authenticated</Badge>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="pb-2">
                        <div className="flex items-center justify-between">
                            <CardTitle className="text-sm font-medium text-slate-400">Performance Rank</CardTitle>
                            <Scale className="h-4 w-4 text-yellow-400" />
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-yellow-500">POOR</div>
                        <p className="text-xs text-slate-500 mt-1">Requires optimization for Quest</p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="pb-2">
                        <div className="flex items-center justify-between">
                            <CardTitle className="text-sm font-medium text-slate-400">Target Platforms</CardTitle>
                            <Zap className="h-4 w-4 text-emerald-400" />
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="flex gap-2">
                            <Badge className="bg-blue-600/20 text-blue-400 border-blue-500/30 gap-1.5 py-1">
                                <Monitor className="h-3 w-3" /> PC
                            </Badge>
                            <Badge className="bg-emerald-600/20 text-emerald-400 border-emerald-500/30 gap-1.5 py-1">
                                <Smartphone className="h-3 w-3" /> Android
                            </Badge>
                        </div>
                    </CardContent>
                </Card>
            </div>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <CardTitle className="text-slate-200">Optimization Checklist</CardTitle>
                    <CardDescription className="text-slate-500">Automated performance validation against VRChat SOTA standards</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    <MetricItem
                        label="Polygons"
                        value="68,432 / 70,000"
                        progress={97}
                        status="warning"
                        description="Near limit for PC, strictly excessive for Quest (limit 20k)."
                    />
                    <MetricItem
                        label="Draw Calls (Materials)"
                        value="12 / 16"
                        progress={75}
                        status="optimal"
                        description="Well within limits. Consider texture atlasing to reach Excellent rank."
                    />
                    <MetricItem
                        label="Skinned Mesh Renderers"
                        value="4 / 8"
                        progress={50}
                        status="optimal"
                        description="Minimal overhead detected."
                    />
                    <MetricItem
                        label="VRAM Usage"
                        value="142MB / 150MB"
                        progress={94}
                        status="warning"
                        description="Highly heavy textures detected. Compressed size: 42MB."
                    />
                </CardContent>
            </Card>

            <div className="grid grid-cols-2 gap-6">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-bold text-slate-200 flex items-center gap-2">
                            <ShieldCheck className="h-4 w-4 text-blue-400" />
                            Safety & Content
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                        <div className="flex items-center justify-between text-xs text-slate-400">
                            <span>Dynamic Bones</span>
                            <span className="text-emerald-500">Valid (32/32)</span>
                        </div>
                        <div className="flex items-center justify-between text-xs text-slate-400">
                            <span>Audio Sources</span>
                            <span className="text-emerald-500">None detected</span>
                        </div>
                        <div className="flex items-center justify-between text-xs text-slate-400">
                            <span>Particle Limit</span>
                            <span className="text-emerald-500">420/1000</span>
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="pb-2 text-slate-200">
                        <CardTitle className="text-sm font-bold flex items-center gap-2">
                            <Zap className="h-4 w-4 text-yellow-500" />
                            Auto-Fix Suggestions
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                        <Button variant="outline" size="sm" className="w-full justify-start text-[10px] border-slate-800 bg-slate-900/50 hover:bg-slate-800 gap-2">
                            <CheckCircle2 className="h-3 w-3 text-emerald-500" />
                            Crunch compress 4 textures
                        </Button>
                        <Button variant="outline" size="sm" className="w-full justify-start text-[10px] border-slate-800 bg-slate-900/50 hover:bg-slate-800 gap-2">
                            <CheckCircle2 className="h-3 w-3 text-emerald-500" />
                            Merge sub-meshes (optimization)
                        </Button>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}

function MetricItem({ label, value, progress, status, description }: { label: string, value: string, progress: number, status: 'optimal' | 'warning' | 'critical', description: string }) {
    const getStatusColor = () => {
        switch (status) {
            case 'optimal': return 'bg-emerald-500';
            case 'warning': return 'bg-yellow-500';
            default: return 'bg-red-500';
        }
    };

    return (
        <div className="space-y-2">
            <div className="flex items-center justify-between text-xs font-medium">
                <span className="text-slate-300">{label}</span>
                <span className="font-mono text-slate-500">{value}</span>
            </div>
            <Progress value={progress} className="h-1 bg-slate-800" indicatorClassName={getStatusColor()} />
            <p className="text-[10px] text-slate-500 leading-normal">{description}</p>
        </div>
    );
}
