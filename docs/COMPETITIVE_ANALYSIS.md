# Competitive Analysis — Unity MCP Ecosystem

Last updated: 2026-05-28 (Phase 1 started)

Compares **sandraschi/unity3d-mcp** (this repo) with other Unity MCP projects and records
what we adopt, what we skip, and our differentiation.

## Summary

| Repo | Scale | Architecture | Standout |
|------|-------|--------------|----------|
| [CoplayDev/unity-mcp](https://github.com/CoplayDev/unity-mcp) | ~10k stars | Unity package + Python MCP | Broad editor tools, tests, active releases |
| [CoderGamester/mcp-unity](https://github.com/CoplayDev/unity-mcp) | ~1.5k stars | WebSocket Node server + Unity package | IDE-focused, Unity 6+, npm bridge |
| [AnkleBreaker-Studio/unity-mcp-server](https://github.com/AnkleBreaker-Studio/unity-mcp-server) | ~288 tools | JS MCP + Unity plugin | Shader Graph, terrain, MPPM, Hub control |
| [Unity AI Assistant](https://docs.unity3d.com/Packages/com.unity.ai.assistant@2.0/manual/unity-mcp-overview.html) | Official | IPC relay + built-in tools | First-party, user approval for external clients |
| **sandraschi/unity3d-mcp** | ~41 portmanteau ops + direct tools | HTTP FastMCP + **dual mode** (bridge + UnityPy disk) | VRM/VRChat/CVR/Resonite/Cluster, World Labs, fleet webapp |

## Where we lead

- **Social VR pipeline** — VRChat SDK auth/upload/validation, ChilloutVR CCK, Resonite/Cluster prep
- **Dual-mode execution** — live Editor bridge (`MCPBridge.cs` :10835) **and** hands-off UnityPy disk edits
- **VRM avatar workflow** — import, animator setup, multi-platform export guidance
- **World Labs / Gaussian splats** — Marble import, splat package install, VRChat optimization hints
- **Fleet integration** — webapp (10830/10831), `just` recipes, composition with blender-mcp → unity3d-mcp handoff
- **Portmanteau design** — fewer MCP tools, richer `operation` enums (LLM-friendly)

## Gaps we are closing (roadmap)

See [ROADMAP.md](ROADMAP.md).

| Gap (competitors have) | Our response | Phase |
|------------------------|--------------|-------|
| Live scene hierarchy / object CRUD | Wire `unity_api` + `unity_bridge` to `MCPBridge.cs` | 1 (in progress) |
| Game/scene view capture for agents | `unity_render` → `capture_game_view` | 1 (in progress) |
| Bridge-first runtime helper | `utils/unity_runtime.py` | 1 (in progress) |
| Prometheus /metrics telemetry | `utils/telemetry.py` | 1 (in progress) |
| Async long-running jobs (builds, batch) | `unity_jobs` | 2 (done) |
| Vision refine loop (multi-capture review) | `unity_vision_refine` | 3 (done) |
| Blender → Unity import orchestration | `unity_import` | 3 (done) |
| General mesh/scene validation beyond VRChat | `unity_validation` | 4 (done) |
| Docker / GHCR + monitoring stack | Dockerfile, compose profile | 5 |

## What we deliberately skip

- **288 atomic tools** (AnkleBreaker) — context explosion; portmanteau + agentic workflow entry
- **Replacing Coplay package** — users may run Coplay alongside fleet MCP for generic editor ops
- **Reimplementing Unity Hub** — we launch projects and automate pipelines, not clone Hub UI
- **OSC in this repo** — delegated to `osc-mcp` via fleet composition

## Architecture comparison

```
Coplay / mcp-unity:  MCP client → stdio MCP → Unity package (socket/WebSocket) → Editor

sandraschi:          MCP client → stdio OR HTTP (/mcp on :10831)
                              → Hands-In: HTTP bridge MCPBridge.cs :10835
                              → Hands-Off: UnityPy disk YAML/asset inspection
                              → VRChat / World Labs / multi-platform portmanteau tools
```

## Fleet pipeline role

```text
blender-mcp (author GLB/VRM) → unity3d-mcp (scene, SDK, build) → VRChat / Resonite / builds
                                      ↑
                               worldlabs-mcp (Marble worlds)
```

## References

- [ROADMAP.md](ROADMAP.md)
- [ARCHITECTURE_DUAL_MODE.md](ARCHITECTURE_DUAL_MODE.md)
- [GUIDE_EDITOR_AUTO.md](GUIDE_EDITOR_AUTO.md)
- [blender-mcp competitive analysis](https://github.com/sandraschi/blender-mcp/blob/main/docs/COMPETITIVE_ANALYSIS.md)
