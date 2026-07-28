import { useEffect, useState } from 'react';
import { LayoutGrid } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface AppEntry {
  name: string;
  description: string;
  icon: string;
  url: string;
  status: string;
}

export function Apps() {
  const [apps, setApps] = useState<AppEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/apps")
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => setApps(d?.apps || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="flex items-center justify-center min-h-[40vh]"><div className="animate-pulse text-slate-600">Loading apps...</div></div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">App Hub</h1>
          <p className="text-slate-400">Discover and manage Unity-linked applications.</p>
        </div>
      </div>

      {apps.length === 0 ? (
        <div className="text-center py-16 border border-dashed border-slate-800 rounded-xl">
          <LayoutGrid className="w-12 h-12 mx-auto text-slate-700 mb-4" />
          <h3 className="text-lg font-semibold text-slate-400 mb-2">No Apps Connected</h3>
          <p className="text-sm text-slate-600 max-w-md mx-auto">
            Connect Unity Editor or other tools via the MCP bridge to see them here.
          </p>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {apps.map((app) => (
            <Card key={app.name} className="border-slate-800 bg-slate-950/50 hover:border-slate-700 transition-colors">
              <CardHeader className="flex flex-row items-center gap-4 pb-2 text-white">
                <div className="rounded-lg bg-emerald-500/10 p-2">
                  <LayoutGrid className="h-6 w-6 text-emerald-500" />
                </div>
                <CardTitle className="text-lg">{app.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-400">{app.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
