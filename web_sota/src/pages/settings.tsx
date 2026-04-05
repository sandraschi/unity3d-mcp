import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input"; // We'll need to create this or use standard input
import { Label } from "@/components/ui/label"; // We'll need to create this or use standard label

export function Settings() {
    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">Settings</h2>
                <p className="text-slate-400">Manage connections and preferences</p>
            </div>

            <div className="grid gap-6">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">ROS Bridge Configuration</CardTitle>
                        <CardDescription className="text-slate-400">Connection details for the ROS Websocket Bridge</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid gap-2">
                            <Label className="text-slate-300">WebSocket URL</Label>
                            <Input
                                className="bg-slate-900 border-slate-800 text-slate-100 placeholder:text-slate-400"
                                defaultValue="ws://localhost:9090"
                            />
                        </div>
                        <Button variant="outline" className="border-slate-800 text-slate-300 hover:bg-slate-800">
                            Test Connection
                        </Button>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">Unity Integration</CardTitle>
                        <CardDescription className="text-slate-400">Virtual robotics environment settings</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid gap-2">
                            <Label className="text-slate-300">OSC Port (Inbound)</Label>
                            <Input
                                className="bg-slate-900 border-slate-800 text-slate-100 placeholder:text-slate-400"
                                defaultValue="9000"
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label className="text-slate-300">OSC Port (Outbound)</Label>
                            <Input
                                className="bg-slate-900 border-slate-800 text-slate-100 placeholder:text-slate-400"
                                defaultValue="9001"
                            />
                        </div>
                        <Button variant="outline" className="border-slate-800 text-slate-300 hover:bg-slate-800">
                            Save Ports
                        </Button>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
