import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
    CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
    ChevronRight,
    Search,
    Plus,
    Box,
    Layers,
    Type,
    Camera,
    Lightbulb,
    Trash2,
    Copy,
    Settings2
} from "lucide-react";

export default function Hierarchy() {
    return (
        <div className="grid grid-cols-12 gap-6 h-[calc(100vh-8rem)]">
            {/* Hierarchy Tree */}
            <Card className="col-span-4 border-slate-800 bg-slate-950/50 flex flex-col">
                <CardHeader className="p-4 border-b border-slate-800">
                    <div className="flex items-center justify-between mb-4">
                        <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-400">Hierarchy</CardTitle>
                        <Button size="sm" variant="ghost" className="h-8 w-8 p-0">
                            <Plus className="h-4 w-4" />
                        </Button>
                    </div>
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3 w-3 text-slate-500" />
                        <input
                            placeholder="Search scene..."
                            className="w-full bg-slate-900 border border-slate-800 rounded px-8 py-1.5 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-blue-500"
                        />
                    </div>
                </CardHeader>
                <CardContent className="flex-1 overflow-auto p-0">
                    <div className="py-2">
                        <HierarchyItem label="Main Camera" icon={<Camera className="h-3 w-3" />} selected />
                        <HierarchyItem label="Directional Light" icon={<Lightbulb className="h-3 w-3" />} />
                        <HierarchyItem label="Environment" icon={<Box className="h-3 w-3" />} hasChildren expanded>
                            <HierarchyItem label="Terrain" icon={<Layers className="h-3 w-3" />} depth={1} />
                            <HierarchyItem label="Water" icon={<Layers className="h-3 w-3" />} depth={1} />
                        </HierarchyItem>
                        <HierarchyItem label="Player" icon={<Box className="h-3 w-3" />} hasChildren>
                            <HierarchyItem label="Model" icon={<Box className="h-3 w-3" />} depth={1} />
                            <HierarchyItem label="Canvas" icon={<Type className="h-3 w-3" />} depth={1} />
                        </HierarchyItem>
                    </div>
                </CardContent>
            </Card>

            {/* Inspector */}
            <Card className="col-span-8 border-slate-800 bg-slate-950/50 flex flex-col">
                <CardHeader className="p-4 border-b border-slate-800 flex flex-row items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="bg-blue-500/20 p-2 rounded">
                            <Camera className="h-5 w-5 text-blue-500" />
                        </div>
                        <div>
                            <CardTitle className="text-lg font-bold text-slate-200">Main Camera</CardTitle>
                            <CardDescription className="text-xs text-slate-500 font-mono">Tag: MainCamera | Layer: Default</CardDescription>
                        </div>
                    </div>
                    <div className="flex gap-2">
                        <Button size="sm" variant="ghost" className="h-8 w-8 p-0">
                            <Copy className="h-4 w-4 text-slate-500" />
                        </Button>
                        <Button size="sm" variant="ghost" className="h-8 w-8 p-0 hover:text-red-500">
                            <Trash2 className="h-4 w-4 text-slate-500" />
                        </Button>
                    </div>
                </CardHeader>
                <CardContent className="flex-1 overflow-auto p-4 space-y-4">
                    <InspectorSection title="Transform" icon={<Box className="h-3.5 w-3.5" />}>
                        <TransformField label="Position" x="0.00" y="1.00" z="-10.00" />
                        <TransformField label="Rotation" x="0.00" y="0.00" z="0.00" />
                        <TransformField label="Scale" x="1.00" y="1.00" z="1.00" />
                    </InspectorSection>

                    <InspectorSection title="Camera" icon={<Camera className="h-3.5 w-3.5" />}>
                        <div className="grid grid-cols-2 gap-4">
                            <PropertyField label="Process" value="Perspective" />
                            <PropertyField label="Field of View" value="60" />
                            <PropertyField label="Clipping Planes" value="0.01 - 1000" />
                            <PropertyField label="Target Display" value="Display 1" />
                        </div>
                    </InspectorSection>

                    <InspectorSection title="Audio Listener" icon={<Settings2 className="h-3.5 w-3.5" />}>
                        <p className="text-[10px] text-slate-500 italic">No additional settings for this component.</p>
                    </InspectorSection>
                </CardContent>
            </Card>
        </div>
    );
}

function HierarchyItem({ label, icon, depth = 0, selected = false, hasChildren = false, expanded = false, children }: { label: string, icon: React.ReactNode, depth?: number, selected?: boolean, hasChildren?: boolean, expanded?: boolean, children?: React.ReactNode }) {
    return (
        <>
            <div
                className={`flex items-center gap-2 px-2 py-1 cursor-pointer transition-colors ${selected ? 'bg-blue-600/20 text-blue-400 border-l-2 border-blue-500' : 'hover:bg-slate-900 text-slate-400'}`}
                style={{ paddingLeft: `${(depth * 16) + 8}px` }}
            >
                <ChevronRight className={`h-3 w-3 text-slate-600 transition-transform ${expanded ? 'rotate-90' : ''} ${!hasChildren ? 'opacity-0' : ''}`} />
                <span className="text-blue-500/50">{icon}</span>
                <span className="text-xs font-medium truncate">{label}</span>
            </div>
            {expanded && children}
        </>
    );
}

function InspectorSection({ title, icon, children }: { title: string, icon: React.ReactNode, children: React.ReactNode }) {
    return (
        <div className="space-y-3 p-3 bg-white/5 rounded-lg border border-slate-800">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-400">
                {icon}
                {title}
            </div>
            {children}
        </div>
    );
}

function TransformField({ label, x, y, z }: { label: string, x: string, y: string, z: string }) {
    return (
        <div className="grid grid-cols-12 gap-2 items-center">
            <span className="col-span-3 text-[10px] font-medium text-slate-500">{label}</span>
            <div className="col-span-9 grid grid-cols-3 gap-1">
                <div className="flex bg-black/40 rounded border border-slate-800">
                    <span className="px-1 text-[8px] text-red-500 flex items-center bg-red-500/10 border-r border-slate-800">X</span>
                    <input
                        className="w-full bg-transparent text-[10px] p-1 text-slate-300 focus:outline-none"
                        value={x}
                        title={`${label} X`}
                        name={`${label.toLowerCase()}-x`}
                    />
                </div>
                <div className="flex bg-black/40 rounded border border-slate-800">
                    <span className="px-1 text-[8px] text-emerald-500 flex items-center bg-emerald-500/10 border-r border-slate-800">Y</span>
                    <input
                        className="w-full bg-transparent text-[10px] p-1 text-slate-300 focus:outline-none"
                        value={y}
                        title={`${label} Y`}
                        name={`${label.toLowerCase()}-y`}
                    />
                </div>
                <div className="flex bg-black/40 rounded border border-slate-800">
                    <span className="px-1 text-[8px] text-blue-500 flex items-center bg-blue-500/10 border-r border-slate-800">Z</span>
                    <input
                        className="w-full bg-transparent text-[10px] p-1 text-slate-300 focus:outline-none"
                        value={z}
                        title={`${label} Z`}
                        name={`${label.toLowerCase()}-z`}
                    />
                </div>
            </div>
        </div>
    );
}

function PropertyField({ label, value }: { label: string, value: string }) {
    return (
        <div className="space-y-1">
            <label className="text-[10px] font-medium text-slate-500">{label}</label>
            <div className="bg-black/40 rounded border border-slate-800 p-1.5 text-[10px] text-slate-300">
                {value}
            </div>
        </div>
    );
}
