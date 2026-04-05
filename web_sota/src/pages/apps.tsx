import { LayoutGrid, Plus, Search } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export function Apps() {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white">App Hub</h1>
                    <p className="text-slate-400">Discover and manage Unity-linked applications.</p>
                </div>
                <Button className="bg-blue-600 hover:bg-blue-700">
                    <Plus className="mr-2 h-4 w-4" />
                    Connect App
                </Button>
            </div>

            <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                <Input
                    placeholder="Search tools and plugins..."
                    className="pl-10 border-slate-800 bg-slate-950/50 text-slate-200"
                />
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                <Card className="border-slate-800 bg-slate-950/50 hover:border-slate-700 transition-colors">
                    <CardHeader className="flex flex-row items-center gap-4 pb-2 text-white">
                        <div className="rounded-lg bg-emerald-500/10 p-2">
                            <LayoutGrid className="h-6 w-6 text-emerald-500" />
                        </div>
                        <CardTitle className="text-lg">Scene Architect</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-slate-400">Automated scene construction and layout tools.</p>
                        <div className="mt-4 flex gap-2">
                            <Button variant="secondary" size="sm" className="bg-slate-800 text-slate-200 hover:bg-slate-700">Open</Button>
                            <Button variant="ghost" size="sm" className="text-slate-400 hover:text-white">Config</Button>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
