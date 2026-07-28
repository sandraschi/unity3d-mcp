import {
  Box,
  Camera,
  ChevronRight,
  Layers,
  Lightbulb,
  Search,
} from "lucide-react";
import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface SceneObject {
  name: string;
  tag: string;
  layer: string;
  transform: { position: number[]; rotation: number[]; scale: number[] };
  components: string[];
  children: SceneObject[];
}

interface SceneData {
  active_scenes: { name: string; path: string; loaded: boolean }[];
  root_objects: SceneObject[];
  object_count: number;
}

export default function Hierarchy() {
  const [data, setData] = useState<SceneData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<Set<string>>(
    new Set(["Environment", "Player"]),
  );

  useEffect(() => {
    fetch("/api/v1/scene")
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        setData(d);
        if (d?.root_objects?.length) setSelected(d.root_objects[0].name);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-8rem)]">
        <div className="animate-pulse text-slate-600">Loading scene...</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-8rem)]">
        <div className="text-center max-w-md">
          <Layers className="w-16 h-16 mx-auto text-slate-700 mb-4" />
          <h2 className="text-xl font-semibold text-slate-400 mb-2">
            Scene Hierarchy
          </h2>
          <p className="text-sm text-slate-600">
            Requires Unity Editor with a scene open.
          </p>
        </div>
      </div>
    );
  }

  const toggleExpand = (name: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      next.has(name) ? next.delete(name) : next.add(name);
      return next;
    });
  };

  function renderObject(obj: SceneObject, depth = 0) {
    const hasChildren = obj.children.length > 0;
    const isExpanded = expanded.has(obj.name);
    const isSelected = selected === obj.name;

    return (
      <div key={obj.name}>
        <div
          className={`flex items-center gap-2 px-2 py-1 cursor-pointer transition-colors ${isSelected ? "bg-blue-600/20 text-blue-400 border-l-2 border-blue-500" : "hover:bg-slate-900 text-slate-400"}`}
          style={{ paddingLeft: `${depth * 16 + 8}px` }}
          onClick={() => {
            setSelected(obj.name);
            if (hasChildren) toggleExpand(obj.name);
          }}
        >
          <ChevronRight
            className={`h-3 w-3 text-slate-600 transition-transform ${isExpanded ? "rotate-90" : ""} ${!hasChildren ? "opacity-0" : ""}`}
          />
          <span className="text-blue-500/50">
            {obj.components.includes("Camera") ? (
              <Camera className="h-3 w-3" />
            ) : obj.components.includes("Light") ? (
              <Lightbulb className="h-3 w-3" />
            ) : (
              <Box className="h-3 w-3" />
            )}
          </span>
          <span className="text-xs font-medium truncate">{obj.name}</span>
        </div>
        {hasChildren &&
          isExpanded &&
          obj.children.map((c) => renderObject(c, depth + 1))}
      </div>
    );
  }

  const selectedObj =
    data.root_objects.find((o) => o.name === selected) ||
    data.root_objects
      .flatMap((o) => o.children)
      .find((c) => c.name === selected);

  return (
    <div className="grid grid-cols-12 gap-6 h-[calc(100vh-8rem)]">
      <Card className="col-span-4 border-slate-800 bg-slate-950/50 flex flex-col">
        <CardHeader className="p-4 border-b border-slate-800">
          <div className="flex items-center gap-2 mb-2">
            <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-400">
              Hierarchy
            </CardTitle>
            <span className="text-[10px] text-slate-600 ml-auto">
              {data.object_count} objects
            </span>
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
            {data.root_objects.map((o) => renderObject(o))}
          </div>
        </CardContent>
      </Card>

      <Card className="col-span-8 border-slate-800 bg-slate-950/50 flex flex-col">
        <CardHeader className="p-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="bg-blue-500/20 p-2 rounded">
              <Camera className="h-5 w-5 text-blue-500" />
            </div>
            <div>
              <CardTitle className="text-lg font-bold text-slate-200">
                {selected || "Select an object"}
              </CardTitle>
              <p className="text-xs text-slate-500 font-mono">
                Tag: {selectedObj?.tag || "—"} | Layer:{" "}
                {selectedObj?.layer || "—"}
              </p>
            </div>
          </div>
        </CardHeader>
        <CardContent className="flex-1 overflow-auto p-4 space-y-4">
          {selectedObj && (
            <>
              <div className="space-y-3 p-3 bg-white/5 rounded-lg border border-slate-800">
                <div className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                  <Box className="h-3.5 w-3.5" /> Transform
                </div>
                {["Position", "Rotation", "Scale"].map((label) => (
                  <div
                    key={label}
                    className="grid grid-cols-12 gap-2 items-center"
                  >
                    <span className="col-span-3 text-[10px] font-medium text-slate-500">
                      {label}
                    </span>
                    <div className="col-span-9 grid grid-cols-3 gap-1">
                      {["X", "Y", "Z"].map((axis, ai) => (
                        <div
                          key={axis}
                          className="flex bg-black/40 rounded border border-slate-800"
                        >
                          <span
                            className={`px-1 text-[8px] flex items-center border-r border-slate-800 ${axis === "X" ? "text-red-500 bg-red-500/10" : axis === "Y" ? "text-emerald-500 bg-emerald-500/10" : "text-blue-500 bg-blue-500/10"}`}
                          >
                            {axis}
                          </span>
                          <input
                            className="w-full bg-transparent text-[10px] p-1 text-slate-300 focus:outline-none"
                            value={String(
                              selectedObj.transform[
                                label.toLowerCase() as keyof typeof selectedObj.transform
                              ][ai],
                            )}
                            readOnly
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
              <div className="space-y-3 p-3 bg-white/5 rounded-lg border border-slate-800">
                <div className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                  <Camera className="h-3.5 w-3.5" /> Components (
                  {selectedObj.components.length})
                </div>
                <div className="flex flex-wrap gap-2">
                  {selectedObj.components.map((comp) => (
                    <span
                      key={comp}
                      className="px-2 py-1 rounded bg-slate-800 text-[10px] text-slate-300 font-mono"
                    >
                      {comp}
                    </span>
                  ))}
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
