# Docker deployment

Image: `ghcr.io/sandraschi/unity3d-mcp:latest`

The container runs the **MCP HTTP server** (FastAPI on **10831**) and optional Prometheus sidecar (**9092**). It does **not** bundle Unity Editor — use **Hands-In** live GUI on the host (see [DUAL_MODE.md](DUAL_MODE.md)).

## Quick start

```powershell
cd D:\Dev\repos\unity3d-mcp
docker compose up unity3d-mcp
```

Health: `http://127.0.0.1:10831/api/v1/health`

Metrics: `http://127.0.0.1:9092/metrics` and `http://127.0.0.1:10831/api/v1/metrics`

## Build locally

```powershell
docker build --target production -t ghcr.io/sandraschi/unity3d-mcp:local .
docker run --rm -p 10831:10831 -p 9092:9092 ghcr.io/sandraschi/unity3d-mcp:local
```

## Monitoring profile

```powershell
docker compose --profile monitoring up -d
```

## Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `MCP_PORT` | 10831 | HTTP MCP |
| `PROMETHEUS_PORT` | 9092 | Metrics sidecar |
| `UNITY3D_MCP_LOG_FORMAT` | json | Loki-friendly logs |
| `UNITY3D_MCP_BRIDGE_HOST` | host.docker.internal | Reach host Unity bridge |
| `UNITY3D_MCP_BRIDGE_PORT` | 10835 | MCPBridge.cs port |

## CI / GHCR

Pushes to `main` publish via `.github/workflows/docker-publish.yml`.
