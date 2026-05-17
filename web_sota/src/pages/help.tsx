export function Help() {
    return (
        <div className="space-y-6 p-6">
            <h1 className="text-2xl font-bold">Help & Documentation</h1>
            <p className="text-muted-foreground">Understanding the Unity3D MCP ecosystem — import/export, fleet mesh, and tools.</p>

            <section className="space-y-4">
                <h2 className="text-lg font-semibold">Import / Export Overview</h2>
                <p className="text-sm text-muted-foreground">
                    Unity3D-MCP bridges models between the fleet and Unity. The <strong>Fleet Mesh</strong> page
                    lets you import models from Gazebo, FreeCAD, Resonite, Blender, and World Labs, then
                    export them back to FBX or glTF format.
                </p>

                <div className="grid gap-4 md:grid-cols-2">
                    <div className="rounded-lg border border-border/40 p-4">
                        <h3 className="font-medium text-sm mb-2">Import (into Unity)</h3>
                        <table className="text-xs w-full">
                            <thead><tr className="text-muted-foreground"><th className="text-left pr-2">Source</th><th className="text-left pr-2">Formats</th><th className="text-left">Use case</th></tr></thead>
                            <tbody>
                                <tr><td className="pr-2 py-1">Gazebo</td><td className="pr-2 py-1">FBX, OBJ</td><td className="py-1">Robot simulation → visualization</td></tr>
                                <tr><td className="pr-2 py-1">FreeCAD</td><td className="pr-2 py-1">STEP, STL, OBJ</td><td className="py-1">CAD parts → Unity scene</td></tr>
                                <tr><td className="pr-2 py-1">Resonite</td><td className="pr-2 py-1">VRM, GLB</td><td className="py-1">VR worlds → Unity</td></tr>
                                <tr><td className="pr-2 py-1">Blender</td><td className="pr-2 py-1">FBX, GLTF, OBJ</td><td className="py-1">3D modelling → Unity</td></tr>
                                <tr><td className="pr-2 py-1">World Labs</td><td className="pr-2 py-1">OBJ, FBX, GLB</td><td className="py-1">AI worlds → Unity</td></tr>
                                <tr><td className="pr-2 py-1">Generic</td><td className="pr-2 py-1">Any format</td><td className="py-1">Auto-detect from extension</td></tr>
                            </tbody>
                        </table>
                    </div>
                    <div className="rounded-lg border border-border/40 p-4">
                        <h3 className="font-medium text-sm mb-2">Export (from Unity)</h3>
                        <table className="text-xs w-full">
                            <thead><tr className="text-muted-foreground"><th className="text-left pr-2">Format</th><th className="text-left pr-2">Use case</th></tr></thead>
                            <tbody>
                                <tr><td className="pr-2 py-1">FBX</td><td className="py-1">Full scene exchange (Blender, Gazebo, any 3D app)</td></tr>
                                <tr><td className="pr-2 py-1">glTF</td><td className="py-1">Web, mobile, Resonite — compact, PBR-ready, open standard</td></tr>
                                <tr><td className="pr-2 py-1">GLB</td><td className="py-1">Binary glTF — single file, same as glTF</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>

            <section className="space-y-3">
                <h2 className="text-lg font-semibold">Format cheat sheet</h2>
                <div className="grid gap-3 md:grid-cols-3">
                    {[
                        { name: "FBX", aka: "Filmbox (Autodesk)", use: "Full scene exchange", anim: "Yes", web: "No" },
                        { name: "glTF", aka: "GL Transmission (open)", use: "Web, mobile, Resonite", anim: "Yes", web: "Yes" },
                        { name: "OBJ", aka: "Wavefront (legacy)", use: "Universal mesh baseline", anim: "No", web: "No" },
                        { name: "STEP", aka: "ISO 10303 (engineering)", use: "CAD exchange with FreeCAD", anim: "No", web: "No" },
                        { name: "STL", aka: "Stereolithography", use: "3D printing", anim: "No", web: "No" },
                        { name: "VRM", aka: "VR avatar standard", use: "Resonite humanoid avatars", anim: "Yes", web: "No" },
                    ].map((fmt) => (
                        <div key={fmt.name} className="rounded-lg border border-border/40 p-3">
                            <div className="font-medium text-sm">{fmt.name}</div>
                            <div className="text-xs text-muted-foreground mt-0.5">{fmt.aka}</div>
                            <div className="text-xs mt-2">{fmt.use}</div>
                            <div className="text-xs text-muted-foreground mt-1">Animation: {fmt.anim} &middot; Web: {fmt.web}</div>
                        </div>
                    ))}
                </div>
            </section>

            <section className="space-y-3">
                <h2 className="text-lg font-semibold">REST API endpoints</h2>
                <div className="text-sm text-muted-foreground space-y-1">
                    <p><code>POST /api/v1/gazebo/import</code> — Import Gazebo simulation models</p>
                    <p><code>POST /api/v1/freecad/import</code> — Import FreeCAD CAD models</p>
                    <p><code>POST /api/v1/resonite/import</code> — Import Resonite VRM/GLB</p>
                    <p><code>POST /api/v1/blender/import</code> — Import Blender scenes</p>
                    <p><code>POST /api/v1/worldlabs/import</code> — Import World Labs AI worlds</p>
                    <p><code>POST /api/v1/import/model</code> — Generic import (auto-detect format)</p>
                    <p><code>POST /api/v1/export/fbx</code> — Export Unity object to FBX</p>
                    <p><code>POST /api/v1/export/gltf</code> — Export Unity object to glTF/GLB</p>
                    <p><code>GET /api/v1/health</code> — Health check</p>
                </div>
                <p className="text-xs text-muted-foreground">
                    Request body for import: <code>{"{"}"models": ["name1"], "file_path": "..."{"}"}</code>
                </p>
            </section>
        </div>
    );
}
