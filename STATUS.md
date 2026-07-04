# unity3d-mcp — Status

**Version:** 0.1.0
**Updated:** 2026-07-04

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
| Dashboard API fetch | ✅ | New — uses `/api/v1/health` |
| `zustand` / `framer-motion` | ❌ | Missing from package.json |
| Chat personality selector | ❌ | Static placeholder |
| GitHub CI workflow | ❌ | Missing |
