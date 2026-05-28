import { useState } from "react";

type TabId = "agent-lab" | "import" | "vision" | "jobs" | "worldlabs" | "fleet";

const tabs: { id: TabId; label: string }[] = [
  { id: "agent-lab", label: "Agent Lab (v1.3)" },
  { id: "import", label: "unity_import" },
  { id: "vision", label: "Vision refine" },
  { id: "jobs", label: "unity_jobs" },
  { id: "worldlabs", label: "World Labs" },
  { id: "fleet", label: "Fleet mesh" },
];

const content: Record<TabId, { title: string; lines: string[] }> = {
  "agent-lab": {
    title: "Agent Lab overview",
    lines: [
      "Copy MCPBridge.cs to Assets/Editor/ — bridge listens on http://localhost:10835",
      "HTTP MCP: uv run python -m unity3d_mcp --http --port 10831",
      "Typical loop: blender-mcp export GLB → unity_import → unity_vision_refine review_bundle → apply_bridge_commands",
      "Tools: unity_bridge, unity_render, unity_api, unity_jobs, unity_import, unity_vision_refine, worldlabs",
    ],
  },
  import: {
    title: "unity_import — Blender handoff",
    lines: [
      "unity_import(operation='list_formats')",
      "unity_import(operation='import_blender', file_path='D:/exports/scene.glb', project_path='D:/Unity/MyProject')",
      "unity_import(operation='import_fleet_batch', input_dir='D:/exports', pattern='*.glb', project_path='...')",
      "Assets land in Assets/BlenderImports/ — refresh Unity or use live bridge session",
    ],
  },
  vision: {
    title: "unity_vision_refine + unity_render",
    lines: [
      "unity_render(operation='capture_game_view', output_path='D:/Temp/review.png', include_base64=True)",
      "unity_render(operation='capture_multi_angle', output_dir='D:/Temp/angles', angles=4)",
      "unity_vision_refine(operation='review_bundle', output_dir='D:/Temp/review', goal='Improve lighting')",
      "unity_vision_refine(operation='apply_bridge_commands', commands_json='[{\"action\":\"transform_object\",\"target\":\"Cube\",\"position\":[0,2,0]}]')",
    ],
  },
  jobs: {
    title: "unity_jobs — async queue",
    lines: [
      "unity_jobs(operation='submit', job_type='build', project_path='...', build_target='StandaloneWindows64', output_path='D:/Builds')",
      "unity_jobs(operation='submit', job_type='batch_import', input_dir='D:/exports', project_path='...')",
      "unity_jobs(operation='submit', job_type='simulation', duration=2.0)",
      "unity_jobs(operation='status', job_id='...') | list | cancel",
    ],
  },
  worldlabs: {
    title: "worldlabs — Marble + agent review",
    lines: [
      "worldlabs(operation='import_marble', source_path='...', project_path='...')",
      "worldlabs(operation='assemble_review', source_path='...', project_path='...', output_dir='D:/Temp/wl_review', goal='VRChat world')",
      "assemble_review imports Marble assets then runs unity_vision_refine review_bundle",
    ],
  },
  fleet: {
    title: "Fleet mesh import/export",
    lines: [
      "REST POST /api/v1/blender/import — fleet HTTP bridge",
      "Sources: Blender (GLB/FBX), FreeCAD, Gazebo, Resonite (VRM/GLB), World Labs",
      "Export: POST /api/v1/export/fbx | /api/v1/export/gltf",
      "Pipeline: blender-mcp (author) → unity3d-mcp (scene) → VRChat / Resonite / builds",
    ],
  },
};

export function Help() {
  const [tab, setTab] = useState<TabId>("agent-lab");
  const section = content[tab];

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-2xl font-bold">Help & Reference</h1>
      <p className="text-sm text-muted-foreground">
        Unity3D MCP Agent Lab — bridge, fleet import, vision loops, async jobs. See docs/ROADMAP.md in repo.
      </p>

      <div className="flex flex-wrap gap-2 border-b border-border/40 pb-2">
        {tabs.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={`px-3 py-1.5 rounded-md text-sm font-medium ${
              tab === t.id ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold">{section.title}</h2>
        <ul className="space-y-2 text-sm text-muted-foreground">
          {section.lines.map((line) => (
            <li key={line}>
              {line.startsWith("unity_") || line.startsWith("worldlabs") || line.startsWith("POST") ? (
                <code className="text-xs bg-muted px-1.5 py-0.5 rounded block overflow-x-auto">{line}</code>
              ) : (
                line
              )}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
