const API_BASE = "/mcp";

export async function getBackendHealth(): Promise<{ ok: boolean; error?: string }> {
  try {
    const r = await fetch(`${API_BASE}/api/v1/health`);
    if (!r.ok) return { ok: false, error: `HTTP ${r.status}` };
    return { ok: true };
  } catch (e) {
    return { ok: false, error: e instanceof Error ? e.message : "Network error" };
  }
}

interface MCPResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
}

export async function callTool<T>(
  tool: string,
  params: Record<string, unknown> = {},
): Promise<MCPResponse<T>> {
  try {
    const response = await fetch(`${API_BASE}/api/v1/tool`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tool, params }),
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return (await response.json()) as MCPResponse<T>;
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
    };
  }
}
