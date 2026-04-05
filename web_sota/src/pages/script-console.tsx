import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
    Play,
    Save,
    Trash2,
    History,
    FileCode,
    Terminal,
    Zap,
    BookOpen
} from "lucide-react";

export default function ScriptConsole() {
    return (
        <div className="grid grid-cols-12 gap-6 h-[calc(100vh-8rem)]">
            {/* Library & History */}
            <div className="col-span-3 flex flex-col gap-6">
                <Card className="flex-1 border-slate-800 bg-slate-950/50 overflow-hidden flex flex-col">
                    <CardHeader className="p-4 border-b border-slate-800">
                        <CardTitle className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                            <BookOpen className="h-3.5 w-3.5 text-blue-400" />
                            Snippet Library
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="p-0 overflow-auto">
                        <SnippetItem label="Batch Rename Objects" icon={<FileCode className="h-3.5 w-3.5" />} language="C#" />
                        <SnippetItem label="Generate Grid Layout" icon={<FileCode className="h-3.5 w-3.5" />} language="C#" />
                        <SnippetItem label="Optimize Mesh Assets" icon={<FileCode className="h-3.5 w-3.5" />} language="C#" />
                        <SnippetItem label="Export Selected FBX" icon={<FileCode className="h-3.5 w-3.5" />} language="C#" />
                    </CardContent>
                </Card>

                <Card className="h-48 border-slate-800 bg-slate-950/50 flex flex-col">
                    <CardHeader className="p-4 border-b border-slate-800">
                        <CardTitle className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                            <History className="h-3.5 w-3.5 text-yellow-500" />
                            Run History
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="p-2 space-y-1 overflow-auto font-mono text-[9px]">
                        <div className="p-2 rounded hover:bg-white/5 cursor-pointer text-slate-400">
                            <span className="text-emerald-500">api_execute_method</span> (Rename...) - 2m ago
                        </div>
                        <div className="p-2 rounded hover:bg-white/5 cursor-pointer text-slate-400">
                            <span className="text-emerald-500">api_get_scene...</span> - 15m ago
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Editor Workspace */}
            <div className="col-span-9 flex flex-col gap-6">
                <Card className="flex-1 border-slate-800 bg-slate-950/50 flex flex-col">
                    <CardHeader className="flex flex-row items-center justify-between py-2 border-b border-slate-800">
                        <div className="flex items-center gap-2">
                            <Badge variant="outline" className="bg-blue-500/10 text-blue-400 border-blue-500/20 text-[10px] h-5">Editor Script</Badge>
                            <span className="text-xs font-mono text-slate-300">NewScript_01.cs</span>
                        </div>
                        <div className="flex gap-2">
                            <Button size="sm" variant="ghost" className="h-8 text-slate-400">
                                <Save className="h-4 w-4 mr-2" />
                                Save
                            </Button>
                            <Button size="sm" className="bg-emerald-600 hover:bg-emerald-700 text-white shadow-lg shadow-emerald-900/20">
                                <Play className="h-4 w-4 mr-2" />
                                Execute
                            </Button>
                        </div>
                    </CardHeader>
                    <CardContent className="flex-1 p-0 overflow-hidden">
                        <div className="h-full bg-black/40 p-4 font-mono text-sm leading-relaxed text-blue-400/90 whitespace-pre">
                            {`using UnityEditor;
using UnityEngine;

public class HierarchyAutomator {
    [MenuItem("MCP/Automate Scene")]
    public static void Run() {
        var selection = Selection.gameObjects;
        foreach (var obj in selection) {
            Debug.Log("Processing: " + obj.name);
            // Industrial logic here
        }
    }
}`}
                        </div>
                    </CardContent>
                </Card>

                {/* Output Console */}
                <Card className="h-48 border-slate-800 bg-slate-950/50 flex flex-col overflow-hidden">
                    <CardHeader className="flex flex-row items-center justify-between py-2 border-b border-slate-800 bg-slate-900/50">
                        <div className="flex items-center gap-2">
                            <Terminal className="h-3.5 w-3.5 text-emerald-500" />
                            <span className="text-[10px] font-bold uppercase text-slate-400">Console Output</span>
                        </div>
                        <Button size="sm" variant="ghost" className="h-6 w-6 p-0 hover:bg-red-900/20 hover:text-red-500 transition-colors">
                            <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                    </CardHeader>
                    <CardContent className="p-3 font-mono text-[11px] space-y-1 overflow-auto">
                        <div className="flex gap-2 text-slate-500">
                            <span className="text-slate-600">[00:34:12]</span>
                            <span className="text-blue-500">INFO:</span> Initializing Unity Editor Bridge...
                        </div>
                        <div className="flex gap-2 text-slate-500">
                            <span className="text-slate-600">[00:34:13]</span>
                            <span className="text-emerald-500">SUCCESS:</span> Script compiled successfully.
                        </div>
                        <div className="flex gap-2 text-slate-200">
                            <span className="text-slate-600">[00:34:13]</span>
                            <span>Processing: MainCamera</span>
                        </div>
                        <div className="flex gap-2 text-slate-200">
                            <span className="text-slate-600">[00:34:13]</span>
                            <span>Processing: Directional Light</span>
                        </div>
                        <div className="flex gap-2 text-slate-500">
                            <span className="text-slate-600">[00:34:14]</span>
                            <span className="text-emerald-500">DONE:</span> Execution finished in 1.4s
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}

function SnippetItem({ label, icon, language }: { label: string, icon: React.ReactNode, language: string }) {
    return (
        <div className="group flex items-center justify-between px-4 py-3 hover:bg-slate-900 cursor-pointer border-b border-slate-900/50 transition-colors">
            <div className="flex items-center gap-3">
                <div className="text-slate-500 group-hover:text-blue-400 transition-colors">{icon}</div>
                <div className="space-y-0.5">
                    <div className="text-xs font-medium text-slate-300">{label}</div>
                    <div className="text-[9px] text-slate-500 font-mono">{language}</div>
                </div>
            </div>
            <Zap className="h-3 w-3 text-slate-700 opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>
    );
}
