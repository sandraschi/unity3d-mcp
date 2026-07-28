# unity3d-mcp — Status

**Version:** 0.1.0
**Updated:** 2026-07-25

## Fleet Standards Compliance

| Standard | Status | Notes |
|----------|--------|-------|
| Port registration (10830/10831) | ✅ | In WEBAPP_PORTS.md |
| `glama.json` | ✅ | Root |
| `llms.txt` + `llms-full.txt` | ✅ | Root |
| `justfile` with recipes | ✅ | |
| `start.ps1` + `start.bat` | ✅ | |
| Tauri NSIS build pipeline | ✅ | |
| NSIS hooks | ✅ | |
| CUA smoke test | ✅ | |
| Session context injection | ✅ | 5 files |
| `.env.example` | ✅ | New |
| `color-scheme: dark` CSS | ✅ | New |
| Vite `/api` + `/mcp` proxy | ✅ | New |
| `.pre-commit-config.yaml` | ✅ | New |
| `mcpb/manifest.json` | ✅ | New |
| `STATUS.md` / `TODO.md` | ✅ | New |
| Dashboard API fetch | ✅ | Uses `/api/v1/health` + `/api/v1/status` |
| REST API endpoints | ✅ | 8 endpoints: health, status, llm/providers, scene, avatar/status, packages, editor/scripts, apps |
| Frontend pages wired to backend | ✅ | Dashboard, Status, Script Console, Hierarchy, Avatar Pipeline, Plugin Manager, Apps, Settings |
| Hierarchy interactive tree | ✅ | Clickable objects, inspector with transforms/components |
| Scene /api/v1/scene | ✅ | Returns full hierarchy with transforms and components |
| `zustand` / `framer-motion` | ❌ | Missing from package.json |
| Chat personality selector | ❌ | Static placeholder |
| GitHub CI workflow | ❌ | Missing |
