import { defineConfig } from '@playwright/test';
export default defineConfig({
    testDir: './e2e', timeout: 60000, retries: 1,
    use: { baseURL: 'http://localhost:10830', headless: true, screenshot: 'only-on-failure' },
    webServer: {
        command: 'uv run python -m unity3d_mcp.server --port 10831',
        port: 10831, timeout: 30000, reuseExistingServer: false
    }
});
