# unity3d-mcp MCP HTTP server (no Unity Editor in container).
#
# Build:
#   docker build --target production -t ghcr.io/sandraschi/unity3d-mcp:local .
#
# Run:
#   docker run --rm -p 10831:10831 -p 9092:9092 ghcr.io/sandraschi/unity3d-mcp:local
#
# Live GUI (Hands-In) requires Unity Editor + MCPBridge.cs on the HOST (port 10835).

FROM python:3.12-slim AS base

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

ENV MCP_TRANSPORT=http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=10831
ENV PROMETHEUS_PORT=9092
ENV UNITY3D_MCP_METRICS_ENABLED=true
ENV UNITY3D_MCP_LOG_FORMAT=json
ENV UNITY3D_MCP_LOG_LEVEL=INFO

WORKDIR /app

FROM base AS production

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir -e ".[monitoring]"

RUN useradd --create-home --shell /bin/bash mcp \
    && mkdir -p /app/logs \
    && chown -R mcp:mcp /app

USER mcp

EXPOSE 10831 9092

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:10831/api/v1/health', timeout=5)"

CMD ["uvicorn", "unity3d_mcp.app:app", "--host", "0.0.0.0", "--port", "10831"]

ARG BUILD_DATE
ARG VERSION
ARG VCS_REF

LABEL org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.title="Unity3D MCP" \
      org.opencontainers.image.description="Agentic Unity MCP server (bridge + disk dual mode)" \
      org.opencontainers.image.vendor="FlowEngineer sandraschi" \
      org.opencontainers.image.source="https://github.com/sandraschi/unity3d-mcp" \
      org.opencontainers.image.licenses="MIT"
