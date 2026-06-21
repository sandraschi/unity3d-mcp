"""Smoke test for unity3d-mcp Agent Lab tool surface and dual-mode reporting."""

from __future__ import annotations

import asyncio


async def main() -> int:
    from unity3d_mcp.server import server_instance
    from unity3d_mcp.utils.execution_mode import describe_execution_mode

    print("=== unity3d-mcp smoke test ===")
    app = server_instance.app
    tools = await app.list_tools()
    names = {t.name for t in tools}
    required = {
        "unity_bridge",
        "unity_render",
        "unity_import",
        "unity_vision_refine",
        "unity_validation",
        "unity_jobs",
    }
    missing = required - names
    print(f"Tools registered: {len(names)}")
    if missing:
        print(f"FAIL missing tools: {sorted(missing)}")
        return 1
    print(f"OK phase tools present: {sorted(required)}")

    mode = await describe_execution_mode()
    print(f"Execution mode: {mode.get('label')} ({mode.get('mode')}) bridge={mode.get('bridge_connected')}")

    for tool_name, args in [
        ("unity_validation", {"operation": "list_limits"}),
        ("unity_import", {"operation": "list_formats"}),
        ("unity_jobs", {"operation": "list"}),
        ("unity_bridge", {"operation": "execution_mode"}),
    ]:
        result = await app.call_tool(tool_name, args)
        text = result.content[0].text if result.content else str(result)
        print(f"OK {tool_name}: {text[:140].replace(chr(10), ' ')}")

    print("=== smoke test passed ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
