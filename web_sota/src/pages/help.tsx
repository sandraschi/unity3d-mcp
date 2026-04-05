import { Book, Terminal } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function Help() {
    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-white">Help & Documentation</h1>
                <p className="text-slate-400">Resources for the Unity3D MCP integration.</p>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center gap-4 text-white">
                        <Book className="h-5 w-5 text-blue-500" />
                        <CardTitle>API Documentation</CardTitle>
                    </CardHeader>
                    <CardContent className="text-slate-400 text-sm">
                        Detailed reference for bridge scripts and C# side components.
                    </CardContent>
                </Card>
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center gap-4 text-white">
                        <Terminal className="h-5 w-5 text-emerald-500" />
                        <CardTitle>Console Commands</CardTitle>
                    </CardHeader>
                    <CardContent className="text-slate-400 text-sm">
                        Standardized commands for scene manipulation and asset management.
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
