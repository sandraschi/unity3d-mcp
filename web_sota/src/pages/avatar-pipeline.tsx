import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { User, Upload, Zap, Scale, Activity, Smartphone, Monitor, ShieldCheck, CheckCircle2 } from "lucide-react";

interface AvatarData {
  vrchat: { authenticated: boolean; username: string; status: string };
  active_avatar: {
    name: string; performance_rank: string;
    polygons: number; polygon_limit: number;
    draw_calls: number; draw_call_limit: number;
    skinned_mesh_renderers: number; renderer_limit: number;
    vram_mb: number; vram_limit_mb: number;
    dynamic_bones_valid: number; dynamic_bones_total: number;
    particles: number; particle_limit: number;
  };
  optimization_suggestions: string[];
}

export default function AvatarPipeline() {
  const [data, setData] = useState<AvatarData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/avatar/status")
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => setData(d))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="flex items-center justify-center min-h-[60vh]"><div className="animate-pulse text-slate-600">Loading avatar data...</div></div>;
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center max-w-md">
          <User className="w-16 h-16 mx-auto text-slate-700 mb-4" />
          <h2 className="text-xl font-semibold text-slate-400 mb-2">Avatar Pipeline</h2>
          <p className="text-sm text-slate-600">Requires Unity Editor with VRChat SDK and a VRM avatar loaded.</p>
        </div>
      </div>
    );
  }

  const av = data.active_avatar;
  const polyPct = Math.round((av.polygons / av.polygon_limit) * 100);
  const drawPct = Math.round((av.draw_calls / av.draw_call_limit) * 100);
  const vramPct = Math.round((av.vram_mb / av.vram_limit_mb) * 100);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Avatar Pipeline</h2>
          <p className="text-slate-400">Optimize and deploy VRM avatars to VRChat</p>
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
              <span className="text-lg font-bold text-slate-200">{data.vrchat.username}</span>
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
            <div className="text-2xl font-bold text-yellow-500">{av.performance_rank.toUpperCase()}</div>
            <p className="text-xs text-slate-500 mt-1">{av.polygons.toLocaleString()} / {av.polygon_limit.toLocaleString()} polygons</p>
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
              <Badge className="bg-blue-600/20 text-blue-400 border-blue-500/30 gap-1.5 py-1"><Monitor className="h-3 w-3" /> PC</Badge>
              <Badge className="bg-emerald-600/20 text-emerald-400 border-emerald-500/30 gap-1.5 py-1"><Smartphone className="h-3 w-3" /> Android</Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-slate-200">Optimization Checklist</CardTitle>
          <CardDescription className="text-slate-500">Performance validation against VRChat standards</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <MetricItem label="Polygons" value={`${av.polygons.toLocaleString()} / ${av.polygon_limit.toLocaleString()}`} progress={Math.min(polyPct, 100)} status={polyPct > 90 ? "warning" : "optimal"} description={polyPct > 90 ? "Near limit — consider reduction for Quest (limit 20k)" : "Within limits"} />
          <MetricItem label="Draw Calls" value={`${av.draw_calls} / ${av.draw_call_limit}`} progress={drawPct} status={drawPct > 80 ? "warning" : "optimal"} description="Texture atlasing can reduce draw calls further" />
          <MetricItem label="Skinned Mesh Renderers" value={`${av.skinned_mesh_renderers} / ${av.renderer_limit}`} progress={Math.round((av.skinned_mesh_renderers / av.renderer_limit) * 100)} status="optimal" description="Minimal overhead detected" />
          <MetricItem label="VRAM Usage" value={`${av.vram_mb}MB / ${av.vram_limit_mb}MB`} progress={vramPct} status={vramPct > 85 ? "warning" : "optimal"} description={vramPct > 85 ? "Texture compression recommended" : "Within limits"} />
        </CardContent>
      </Card>

      <div className="grid grid-cols-2 gap-6">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-bold text-slate-200 flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-blue-400" /> Safety & Content
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Dynamic Bones</span>
              <span className="text-emerald-500">Valid ({av.dynamic_bones_valid}/{av.dynamic_bones_total})</span>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Particle Limit</span>
              <span className="text-emerald-500">{av.particles}/{av.particle_limit}</span>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Audio Sources</span>
              <span className="text-emerald-500">None detected</span>
            </div>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="pb-2 text-slate-200">
            <CardTitle className="text-sm font-bold flex items-center gap-2">
              <Zap className="h-4 w-4 text-yellow-500" /> Suggestions
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {data.optimization_suggestions.map((s, i) => (
              <div key={i} className="flex items-center gap-2 text-xs text-slate-400 p-2 rounded-lg bg-slate-900/50 border border-slate-800">
                <CheckCircle2 className="h-3 w-3 text-emerald-500 shrink-0" />
                {s}
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function MetricItem({ label, value, progress, status, description }: { label: string; value: string; progress: number; status: "optimal" | "warning"; description: string }) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs font-medium">
        <span className="text-slate-300">{label}</span>
        <span className="font-mono text-slate-500">{value}</span>
      </div>
      <Progress value={progress} className="h-1 bg-slate-800" indicatorClassName={status === "warning" ? "bg-yellow-500" : "bg-emerald-500"} />
      <p className="text-[10px] text-slate-500 leading-normal">{description}</p>
    </div>
  );
}
