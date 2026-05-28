import { Activity, Box, Camera, Cpu, GitPullRequest, ScanEye, ShieldCheck } from "lucide-react";
import { useState } from "react";
import { callTool, getBackendHealth } from "@/api/mcp";

type TabId = "bridge" | "import" | "vision" | "validation" | "jobs" | "platform";

function ResultBox({ text }: { text: string | null }) {
  if (!text) return null;
  return (
    <pre className="mt-3 p-3 text-xs bg-slate-900 rounded-lg overflow-x-auto whitespace-pre-wrap border border-slate-800 text-slate-300">
      {text}
    </pre>
  );
}

export function AgentTools() {
  const [tab, setTab] = useState<TabId>("validation");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [backendOk, setBackendOk] = useState<boolean | null>(null);

  const [projectPath, setProjectPath] = useState("D:/Unity/MyProject");
  const [modelPath, setModelPath] = useState("D:/exports/avatar.glb");
  const [avatarPrefab, setAvatarPrefab] = useState("Assets/Avatars/MyAvatar.prefab");
  const [outputPath, setOutputPath] = useState("D:/Temp/unity_review.png");
  const [outputDir, setOutputDir] = useState("D:/Temp/unity_angles");
  const [platform, setPlatform] = useState("vrchat");

  const tabs: { id: TabId; label: string; icon: typeof Camera }[] = [
    { id: "bridge", label: "Bridge", icon: Box },
    { id: "import", label: "Import", icon: GitPullRequest },
    { id: "vision", label: "Vision", icon: ScanEye },
    { id: "validation", label: "Validation", icon: ShieldCheck },
    { id: "jobs", label: "Jobs", icon: Cpu },
    { id: "platform", label: "Platform audit", icon: Activity },
  ];

  const run = async (tool: string, params: Record<string, unknown>) => {
    setLoading(true);
    setResult(null);
    try {
      const res = await callTool(tool, params);
      setResult(JSON.stringify(res, null, 2));
    } catch (e) {
      setResult(e instanceof Error ? e.message : "Error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100">Agent Tools</h1>
          <p className="text-sm text-slate-400 mt-1">
            Phase 4 (v1.4): bridge, fleet import, vision refine, validation, jobs, unified platform audit.
          </p>
        </div>
        <button
          type="button"
          onClick={async () => setBackendOk((await getBackendHealth()).ok)}
          className="px-3 py-1.5 text-sm bg-slate-800 rounded-md hover:bg-slate-700 text-slate-200"
        >
          Check backend
        </button>
      </div>

      {backendOk !== null && (
        <p className={`text-sm ${backendOk ? "text-green-500" : "text-red-500"}`}>
          Backend {backendOk ? "online" : "offline"} — run web_sota/start.ps1 or uvicorn on 10831.
        </p>
      )}

      <div className="grid gap-3 sm:grid-cols-2">
        <label className="text-xs text-slate-400">
          Project path
          <input
            className="mt-1 w-full rounded-md bg-slate-900 border border-slate-800 px-3 py-2 text-sm text-slate-100"
            value={projectPath}
            onChange={(e) => setProjectPath(e.target.value)}
          />
        </label>
        <label className="text-xs text-slate-400">
          Target platform
          <select
            className="mt-1 w-full rounded-md bg-slate-900 border border-slate-800 px-3 py-2 text-sm text-slate-100"
            value={platform}
            onChange={(e) => setPlatform(e.target.value)}
          >
            <option value="vrchat">vrchat</option>
            <option value="chilloutvr">chilloutvr</option>
            <option value="resonite">resonite</option>
            <option value="cluster">cluster</option>
          </select>
        </label>
      </div>

      <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-2">
        {tabs.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => {
              setTab(t.id);
              setResult(null);
            }}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium ${
              tab === t.id ? "bg-blue-600 text-white" : "bg-slate-900 text-slate-400 hover:text-white"
            }`}
          >
            <t.icon className="h-4 w-4" />
            {t.label}
          </button>
        ))}
      </div>

      {tab === "bridge" && (
        <section className="space-y-3">
          <button
            type="button"
            disabled={loading}
            onClick={() => run("unity_bridge", { operation: "status" })}
            className="px-4 py-2 rounded-md bg-blue-600 text-white text-sm disabled:opacity-50"
          >
            Bridge status
          </button>
          <button
            type="button"
            disabled={loading}
            onClick={() => run("unity_bridge", { operation: "get_hierarchy" })}
            className="ml-2 px-4 py-2 rounded-md bg-slate-800 text-slate-200 text-sm disabled:opacity-50"
          >
            Hierarchy
          </button>
        </section>
      )}

      {tab === "import" && (
        <section className="space-y-3">
          <label className="text-xs text-slate-400 block">
            Model path
            <input
              className="mt-1 w-full rounded-md bg-slate-900 border border-slate-800 px-3 py-2 text-sm"
              value={modelPath}
              onChange={(e) => setModelPath(e.target.value)}
            />
          </label>
          <button
            type="button"
            disabled={loading}
            onClick={() =>
              run("unity_import", {
                operation: "import_blender",
                file_path: modelPath,
                project_path: projectPath,
              })
            }
            className="px-4 py-2 rounded-md bg-blue-600 text-white text-sm disabled:opacity-50"
          >
            Import Blender asset
          </button>
        </section>
      )}

      {tab === "vision" && (
        <section className="space-y-3">
          <label className="text-xs text-slate-400 block">
            Output PNG
            <input
              className="mt-1 w-full rounded-md bg-slate-900 border border-slate-800 px-3 py-2 text-sm"
              value={outputPath}
              onChange={(e) => setOutputPath(e.target.value)}
            />
          </label>
          <button
            type="button"
            disabled={loading}
            onClick={() =>
              run("unity_render", { operation: "capture_game_view", output_path: outputPath })
            }
            className="px-4 py-2 rounded-md bg-blue-600 text-white text-sm disabled:opacity-50"
          >
            Capture game view
          </button>
          <button
            type="button"
            disabled={loading}
            onClick={() =>
              run("unity_vision_refine", {
                operation: "review_bundle",
                output_dir: outputDir,
                goal: "Improve lighting and composition",
              })
            }
            className="ml-2 px-4 py-2 rounded-md bg-slate-800 text-slate-200 text-sm disabled:opacity-50"
          >
            Review bundle
          </button>
        </section>
      )}

      {tab === "validation" && (
        <section className="space-y-3">
          <button
            type="button"
            disabled={loading}
            onClick={() =>
              run("unity_validation", { operation: "validate_scene", target_platform: platform })
            }
            className="px-4 py-2 rounded-md bg-blue-600 text-white text-sm disabled:opacity-50"
          >
            Validate scene (bridge)
          </button>
          <button
            type="button"
            disabled={loading}
            onClick={() =>
              run("unity_validation", { operation: "check_missing_scripts", target_platform: platform })
            }
            className="ml-2 px-4 py-2 rounded-md bg-slate-800 text-slate-200 text-sm disabled:opacity-50"
          >
            Missing scripts
          </button>
          <button
            type="button"
            disabled={loading}
            onClick={() =>
              run("unity_validation", {
                operation: "validate_avatar",
                project_path: projectPath,
                avatar_prefab: avatarPrefab,
                target_platform: platform,
              })
            }
            className="ml-2 px-4 py-2 rounded-md bg-slate-800 text-slate-200 text-sm disabled:opacity-50"
          >
            Validate avatar
          </button>
          <label className="text-xs text-slate-400 block">
            Avatar prefab
            <input
              className="mt-1 w-full rounded-md bg-slate-900 border border-slate-800 px-3 py-2 text-sm"
              value={avatarPrefab}
              onChange={(e) => setAvatarPrefab(e.target.value)}
            />
          </label>
        </section>
      )}

      {tab === "jobs" && (
        <section className="space-y-3">
          <button
            type="button"
            disabled={loading}
            onClick={() =>
              run("unity_jobs", {
                operation: "submit",
                job_type: "build",
                project_path: projectPath,
                build_target: "StandaloneWindows64",
                output_path: "D:/Builds",
              })
            }
            className="px-4 py-2 rounded-md bg-blue-600 text-white text-sm disabled:opacity-50"
          >
            Submit build job
          </button>
        </section>
      )}

      {tab === "platform" && (
        <section className="space-y-3">
          <button
            type="button"
            disabled={loading}
            onClick={() =>
              run("multiplatform", {
                operation: "audit_all",
                project_path: projectPath,
                avatar_object: avatarPrefab,
                model_path: modelPath,
                platform,
              })
            }
            className="px-4 py-2 rounded-md bg-blue-600 text-white text-sm disabled:opacity-50"
          >
            Unified platform audit
          </button>
          <button
            type="button"
            disabled={loading}
            onClick={() =>
              run("unity_validation", {
                operation: "unified_audit",
                project_path: projectPath,
                avatar_prefab: avatarPrefab,
                model_path: modelPath,
                target_platform: platform,
              })
            }
            className="ml-2 px-4 py-2 rounded-md bg-slate-800 text-slate-200 text-sm disabled:opacity-50"
          >
            unity_validation unified_audit
          </button>
        </section>
      )}

      <ResultBox text={result} />
    </div>
  );
}
