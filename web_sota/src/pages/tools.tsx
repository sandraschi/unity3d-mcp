import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Wrench, Terminal } from 'lucide-react';

interface Tool {
    name: string;
    description: string;
    parameters: any[];
}

export function Tools() {
    const [tools, setTools] = useState<Tool[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchTools();
    }, []);

    const fetchTools = async () => {
        try {
            setLoading(true);
            const response = await fetch('http://localhost:10787/api/v1/tools/');
            if (!response.ok) throw new Error('Failed to fetch tools');
            const data = await response.json();
            setTools(data);
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-8 space-y-8">
            {error && (
                <div className="bg-destructive/15 text-destructive p-3 rounded-lg text-sm">
                    {error}
                </div>
            )}
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight">Tools Hub</h2>
                    <p className="text-slate-400">Unity3D MCP inventory</p>
                </div>
                <Button variant="outline" onClick={fetchTools} disabled={loading} className="border-slate-800 bg-slate-900/50">
                    <Wrench className="mr-2 h-4 w-4" />
                    Refresh
                </Button>
            </div>

            <div className="grid gap-6">
                {tools.map((tool) => (
                    <Card key={tool.name} className="border-slate-800 bg-slate-950/50">
                        <CardHeader>
                            <div className="flex items-center gap-3">
                                <Terminal className="h-5 w-5 text-blue-500" />
                                <CardTitle>{tool.name}</CardTitle>
                                <Badge variant="secondary">Tool</Badge>
                            </div>
                            <CardDescription className="text-slate-400">{tool.description}</CardDescription>
                        </CardHeader>
                    </Card>
                ))}
            </div>
        </div>
    );
}
