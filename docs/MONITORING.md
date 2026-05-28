# Monitoring (Phase 5)

Prometheus metrics, JSON logs for Loki, optional Docker monitoring profile.

## Metrics

| Endpoint | Port | Notes |
|----------|------|--------|
| Sidecar | `http://127.0.0.1:9092/metrics` | `PROMETHEUS_PORT` (default **9092**) |
| HTTP app | `http://127.0.0.1:10831/api/v1/metrics` | Same registry via FastAPI |

Enable/disable: `UNITY3D_MCP_METRICS_ENABLED=true|false`

Install optional dep:

```powershell
uv sync --extra monitoring
```

### Key series

- `unity3d_mcp_tool_calls_total{tool,status}`
- `unity3d_mcp_tool_duration_seconds{tool}`
- `unity3d_mcp_bridge_connected` — 1 when MCPBridge.cs responds
- `unity3d_mcp_execution_mode` — 1 = Hands-In live GUI, 0 = Hands-Off
- `unity3d_mcp_jobs_active`

## JSON logs (Loki)

```powershell
$env:UNITY3D_MCP_LOG_FORMAT = "json"
uv run python -m unity3d_mcp --http --port 10831
```

Log file (when using `unity3d_mcp.app`): `logs/unity3d-mcp.log`

## Docker monitoring stack

```powershell
cd D:\Dev\repos\unity3d-mcp
docker compose --profile monitoring up -d
```

| Service | URL |
|---------|-----|
| Grafana | http://localhost:3000 (admin/admin) |
| Prometheus | http://localhost:9090 |
| Loki | http://localhost:3100 |

See [DOCKER.md](DOCKER.md).

## Smoke test

```powershell
uv run python scripts/smoke_test.py
```
