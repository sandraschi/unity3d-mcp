# Unity3D-MCP SOTA 2026 Packaging Script
# Generates a .mcpb distribution bundle using official FastMCP standards.

$distDir = "dist"
$bundleName = "unity3d-mcp.mcpb"
$bundlePath = Join-Path $distDir $bundleName

# 1. Ensure dist directory exists
if (-not (Test-Path $distDir)) {
    New-Item -ItemType Directory -Path $distDir | Out-Null
    Write-Host "Created $distDir directory." -ForegroundColor Cyan
}

# 2. Clear old bundle
if (Test-Path $bundlePath) {
    Remove-Item $bundlePath -Force
    Write-Host "Cleared old bundle: $bundlePath" -ForegroundColor Yellow
}

# 3. Pack the extension
Write-Host "Generating SOTA .mcpb bundle..." -ForegroundColor Green

# Use uvx to run mcpb without global installation
uvx mcpb pack . $bundlePath

if ($LASTEXITCODE -eq 0) {
    Write-Host "Successfully packed $bundleName to $distDir." -ForegroundColor Green
    Write-Host "Bundle size: $((Get-Item $bundlePath).Length / 1KB) KB" -ForegroundColor Gray
} else {
    Write-Error "Failed to pack .mcpb bundle. Ensure 'mcpb' is accessible via uvx."
    exit $LASTEXITCODE
}
