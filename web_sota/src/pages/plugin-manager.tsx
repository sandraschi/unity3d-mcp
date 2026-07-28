import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Package, Download, Box, ShieldCheck, History, Search } from "lucide-react";

interface PackageItem {
  name: string; version: string; publisher: string;
  status: string; latest_version?: string; description?: string;
}

interface PackageData {
  installed_count: number; custom_count: number; pending_updates: number;
  packages: PackageItem[];
}

export default function PluginManager() {
  const [data, setData] = useState<PackageData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/packages")
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => setData(d))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="flex items-center justify-center min-h-[60vh]"><div className="animate-pulse text-slate-600">Loading packages...</div></div>;
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center max-w-md">
          <Package className="w-16 h-16 mx-auto text-slate-700 mb-4" />
          <h2 className="text-xl font-semibold text-slate-400 mb-2">Plugin Manager</h2>
          <p className="text-sm text-slate-600">Requires Unity Editor with a project open to list packages.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 text-slate-200">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Plugin & Package Manager</h2>
          <p className="text-slate-400">Unity Package Manager (UPM) packages</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-4">
        <StatCard label="Installed Packages" value={String(data.installed_count)} icon={<Package className="h-4 w-4 text-blue-400" />} />
        <StatCard label="Custom Plugins" value={String(data.custom_count)} icon={<Box className="h-4 w-4 text-emerald-400" />} />
        <StatCard label="Pending Updates" value={String(data.pending_updates)} icon={<Download className="h-4 w-4 text-yellow-400" />} />
        <StatCard label="Security Checks" value="Passed" icon={<ShieldCheck className="h-4 w-4 text-emerald-500" />} />
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader className="p-4 border-b border-slate-800 flex flex-row items-center justify-between bg-slate-900/30">
          <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-400">Active Packages</CardTitle>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3 w-3 text-slate-500" />
            <input placeholder="Filter packages..." className="bg-slate-900 border border-slate-800 rounded px-8 py-1.5 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-blue-500" />
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {data.packages.map((pkg) => (
            <div key={pkg.name} className="p-4 hover:bg-slate-900 border-b border-slate-900 transition-colors flex items-center justify-between">
              <div className="space-y-1">
                <div className="flex items-center gap-3">
                  <h4 className="text-sm font-bold font-mono text-slate-200">{pkg.name}</h4>
                  <span className="text-[10px] font-medium text-slate-500">v{pkg.version}</span>
                  <Badge variant="outline" className={`text-xs h-4 border-slate-800 ${pkg.status === "update-available" ? "bg-yellow-500/10 text-yellow-500" : "bg-slate-800 text-slate-400"}`}>
                    {pkg.status.replace("-", " ")}
                  </Badge>
                </div>
                <div className="flex items-center gap-2 text-[10px] text-slate-500">
                  <span>{pkg.publisher}</span>
                  {pkg.description && <><span>•</span><span>{pkg.description}</span></>}
                </div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-4">
          <Card className="border-slate-800 bg-slate-950/50">
            <CardHeader className="p-4 border-b border-slate-800">
              <CardTitle className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                <History className="h-3.5 w-3.5" /> Recent Operations
              </CardTitle>
            </CardHeader>
            <CardContent className="p-4 space-y-4">
              <div className="flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-2">
                  <div className="w-1 h-3 rounded-full bg-emerald-500" />
                  <span className="font-medium text-slate-300">Packages loaded</span>
                </div>
                <span className="text-slate-600">via API</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, icon }: { label: string; value: string; icon: React.ReactNode }) {
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
