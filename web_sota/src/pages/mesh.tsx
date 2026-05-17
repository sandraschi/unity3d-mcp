import { useState } from "react";

const BACKEND = "http://127.0.0.1:10831";

const FLEET_SOURCES = [
  { id: "gazebo",  label: "Gazebo",  desc: "Physics simulation",        defaultFile: "gazebo_models/scout.fbx" },
  { id: "freecad", label: "FreeCAD", desc: "CAD model export",         defaultFile: "freecad_models/part.step" },
  { id: "resonite",label: "Resonite",desc: "VR spatial sync",          defaultFile: "resonite_models/avatar.vrm" },
  { id: "blender", label: "Blender", desc: "3D modeling",              defaultFile: "blender_models/scene.fbx" },
  { id: "worldlabs",label: "WorldLabs",desc: "AI-generated 3D worlds", defaultFile: "worldlabs_models/world.obj" },
];

export default function FleetMesh() {
  const [source, setSource] = useState("gazebo");
  const [models, setModels] = useState("");
  const [filePath, setFilePath] = useState("");
  const [exportName, setExportName] = useState("");
  const [exportFmt, setExportFmt] = useState("fbx");
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const activeSrc = FLEET_SOURCES.find((s) => s.id === source)!;

  async function doImport() {
    const modelList = models.split("\n").map((s) => s.trim()).filter(Boolean);
    if (!modelList.length) return;
    setLoading(true);
    setResult(null);
    try {
      const r = await fetch(`${BACKEND}/api/v1/${source}/import`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          models: modelList,
          file_path: filePath || null,
        }),
      });
      const data = await r.json();
      setResult(JSON.stringify(data, null, 2));
    } catch (e: unknown) {
      setResult(`Error: ${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setLoading(false);
    }
  }

  async function doExport() {
    if (!exportName) return;
    setLoading(true);
    setResult(null);
    try {
      const r = await fetch(`${BACKEND}/api/v1/export/fbx`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: exportName, format: exportFmt }),
      });
      const data = await r.json();
      setResult(JSON.stringify(data, null, 2));
    } catch (e: unknown) {
      setResult(`Error: ${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-8 p-6">
      <h1 className="text-2xl font-bold">Fleet Mesh — Import / Export</h1>
      <p className="text-muted-foreground">
        Bridge models between the fleet repos and Unity 3D. Select a source, enter model names, and import.
      </p>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Import panel */}
        <div className="rounded-lg border border-border/40 p-4 space-y-4">
          <h2 className="text-lg font-semibold">Import from fleet</h2>
          <div className="flex flex-wrap gap-2">
            {FLEET_SOURCES.map((s) => (
              <button
                key={s.id}
                onClick={() => setSource(s.id)}
                className={`px-3 py-1.5 rounded text-sm font-medium border transition-colors ${
                  source === s.id
                    ? "border-primary bg-primary/10 text-primary"
                    : "border-border hover:bg-accent"
                }`}
              >
                {s.label}
              </button>
            ))}
          </div>
          <p className="text-xs text-muted-foreground">{activeSrc.desc}</p>

          <div className="space-y-2">
            <label className="text-xs font-medium">Model names (one per line)</label>
            <textarea
              value={models}
              onChange={(e) => setModels(e.target.value)}
              placeholder={`scout\nwarehouse\ncamera_sensor`}
              className="flex h-24 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            />
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium">File path template (optional)</label>
            <input
              value={filePath}
              onChange={(e) => setFilePath(e.target.value)}
              placeholder={activeSrc.defaultFile}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
            />
          </div>
          <button
            onClick={doImport}
            disabled={loading}
            className="px-4 py-2 rounded bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
          >
            {loading ? "Importing…" : `Import from ${activeSrc.label}`}
          </button>
        </div>

        {/* Export panel */}
        <div className="rounded-lg border border-border/40 p-4 space-y-4">
          <h2 className="text-lg font-semibold">Export from Unity</h2>
          <div className="space-y-2">
            <label className="text-xs font-medium">Object name</label>
            <input
              value={exportName}
              onChange={(e) => setExportName(e.target.value)}
              placeholder="MyModel"
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
            />
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium">Format</label>
            <select
              value={exportFmt}
              onChange={(e) => setExportFmt(e.target.value)}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
            >
              <option value="fbx">FBX</option>
              <option value="obj">OBJ (not implemented)</option>
            </select>
          </div>
          <button
            onClick={doExport}
            disabled={loading || !exportName}
            className="px-4 py-2 rounded bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
          >
            Export as FBX
          </button>
          <p className="text-xs text-muted-foreground">
            glTF export not yet available — use FBX and convert with Blender.
          </p>
        </div>
      </div>

      {result && (
        <div className="rounded-lg border border-border/40 p-4">
          <pre className="text-xs font-mono whitespace-pre-wrap">{result}</pre>
        </div>
      )}
    </div>
  );
}
