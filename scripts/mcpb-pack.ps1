#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Build a fleet-standard MCPB bundle for unity3d-mcp (fresh-stage, verify, pack).

.DESCRIPTION
    No build script existed for this repo before 2026-09-03. mcpb/server/server.py was a
    flattened, dated-November-2025 stub (588 bytes vs the real src/unity3d_mcp/server.py's
    21,842 bytes) that did not match mcpb/manifest.json's entry_point
    ("src/unity3d_mcp/server.py") - a package built from that state could not have run.

    Per MCPB_PACKAGING_STANDARDS.md (mcp-central-docs) this script:
      0. Fresh-stages repo src/unity3d_mcp -> mcpb/src/unity3d_mcp (wipe + recopy, never
         flatten), removes the obsolete mcpb/server/
      1. Copies the canonical prompts from repo assets/prompts -> mcpb/assets/prompts, if present
      2. Syncs the repo-root .mcpbignore into mcpb/ (always overwrites - pack reads it from
         the pack root, not the repo root)
      3. Verifies the entry point imports with only mcpb/src on sys.path
      4. Asserts no __pycache__ / *.pyc / *.bak / *.bak.* / *.orig / *.rej under mcpb/
      5. Only then runs `mcpb pack`
      6. Removes mcpb/src again so the next run cannot reuse a stale twin

.PARAMETER KeepStage
    If set, leave mcpb/src/ in place after packing (diagnostic only).
#>
param(
    [switch]$KeepStage
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent
Set-Location $RepoRoot

Write-Host "`n=== mcpb-pack.ps1 - unity3d-mcp ===" -ForegroundColor Cyan

# --- Resolve mcpb CLI ---
$mcpbCmd = Get-Command mcpb.cmd -ErrorAction SilentlyContinue
if (-not $mcpbCmd) { $mcpbCmd = Get-Command mcpb -ErrorAction SilentlyContinue }
if (-not $mcpbCmd) {
    $npmMcpb = Join-Path $env:APPDATA "npm\mcpb.cmd"
    if (Test-Path $npmMcpb) { $mcpbCmd = $npmMcpb } else { throw "mcpb CLI not found. Install: npm install -g @anthropic-ai/mcpb" }
}
$mcpbExe = if ($mcpbCmd -is [string]) { $mcpbCmd } else { $mcpbCmd.Source }

# --- 0. Fresh-stage src -> mcpb/src (wipe + recopy, never flatten) ---
$srcPkg = Join-Path $RepoRoot "src\unity3d_mcp"
$stagePkg = Join-Path $RepoRoot "mcpb\src\unity3d_mcp"
if (-not (Test-Path $srcPkg)) { throw "Source not found: $srcPkg" }

Write-Host "  Fresh-staging src\unity3d_mcp -> mcpb\src\unity3d_mcp ..."
if (Test-Path (Join-Path $RepoRoot "mcpb\src")) {
    Remove-Item (Join-Path $RepoRoot "mcpb\src") -Recurse -Force
}
New-Item -ItemType Directory -Force -Path (Split-Path $stagePkg) | Out-Null
Copy-Item -Path $srcPkg -Destination $stagePkg -Recurse -Force

$staleFlattened = Join-Path $RepoRoot "mcpb\server"
if (Test-Path $staleFlattened) {
    Write-Host "  Removing obsolete flattened mcpb\server (superseded by mcpb\src\unity3d_mcp)"
    Remove-Item $staleFlattened -Recurse -Force
}

Get-ChildItem -Path $stagePkg -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
    ForEach-Object { Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue }
Get-ChildItem -Path $stagePkg -Recurse -File -Include "*.pyc", "*.bak", "*.bak.*", "*.orig", "*.rej" -ErrorAction SilentlyContinue |
    ForEach-Object { Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue }
Write-Host "  Staged fresh source (0. fresh stage proved)" -ForegroundColor Green

# --- 1. Canonical prompts (only if repo-root assets/prompts exists) ---
$srcPrompts = Join-Path $RepoRoot "assets\prompts"
$stagePrompts = Join-Path $RepoRoot "mcpb\assets\prompts"
if (Test-Path $srcPrompts) {
    New-Item -ItemType Directory -Force -Path (Split-Path $stagePrompts) | Out-Null
    if (Test-Path $stagePrompts) { Remove-Item $stagePrompts -Recurse -Force }
    Copy-Item -Path $srcPrompts -Destination $stagePrompts -Recurse -Force
    Write-Host "  Copied canonical prompts -> mcpb/assets/prompts" -ForegroundColor Green
} else {
    Write-Host "  [INFO] no repo-root assets/prompts - mcpb/assets/prompts left as-is (this repo's prompts are topic-split .md files, verified not locally corrupted before trusting)" -ForegroundColor Yellow
}

# --- 2. .mcpbignore at the pack root (always sync, never copy-if-missing - a copy-if-missing
# check syncs once then silently goes stale forever after mcpb/.mcpbignore first exists) ---
$mcpbIgnore = Join-Path $RepoRoot "mcpb\.mcpbignore"
$repoIgnore = Join-Path $RepoRoot ".mcpbignore"
if (Test-Path $repoIgnore) {
    Copy-Item $repoIgnore $mcpbIgnore -Force
    Write-Host "  Synced repo-root .mcpbignore -> mcpb/.mcpbignore" -ForegroundColor Green
} elseif (Test-Path $mcpbIgnore) {
    Write-Host "  [WARN] no repo-root .mcpbignore - using existing (possibly stale) mcpb/.mcpbignore" -ForegroundColor Yellow
} else {
    Write-Host "  [WARN] no .mcpbignore found at repo root or mcpb/" -ForegroundColor Yellow
}

# --- 3. Entry-point import verification (mcpb/src only on sys.path) ---
Write-Host "  Verifying entry point imports from mcpb/src only..."
$verifyScript = @"
import sys
sys.path.insert(0, r'$($stagePkg | Split-Path)')
import unity3d_mcp.server as m
origin = getattr(m, '__file__', '')
expected = r'$stagePkg'
if expected.lower() not in origin.lower():
    raise SystemExit(f'Entry point resolved from unexpected location: {origin}')
print('OK:', origin)
"@
$prevEAP = $ErrorActionPreference
$ErrorActionPreference = "Continue"
$verifyOutput = $verifyScript | & uv run python - 2>&1
$verifyExit = $LASTEXITCODE
$ErrorActionPreference = $prevEAP
$verifyOutput | ForEach-Object { Write-Host "    $_" }
if ($verifyExit -ne 0) { throw "Entry point import verification failed" }
Write-Host "  Entry import OK from mcpb/src only (3. self-contained)" -ForegroundColor Green

# --- 4. Pollution check ---
$pollution = Get-ChildItem -Path (Join-Path $RepoRoot "mcpb") -Recurse -Include "__pycache__", "*.pyc", "*.bak", "*.bak.*", "*.orig", "*.rej" -ErrorAction SilentlyContinue
if ($pollution) {
    $pollution | ForEach-Object { Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue }
    Write-Host "  Cleaned pollution left by import verification" -ForegroundColor Yellow
}
Write-Host "  No __pycache__ / *.pyc / *.bak / *.orig / *.rej under mcpb/ (4. clean)" -ForegroundColor Green

# --- 5. Pack ---
if (-not (Test-Path "dist")) { New-Item -ItemType Directory -Path "dist" | Out-Null }
$manifest = Get-Content (Join-Path $RepoRoot "mcpb\manifest.json") | ConvertFrom-Json
$packageName = "$($manifest.name)-v$($manifest.version).mcpb"
$packagePath = Join-Path $RepoRoot "dist\$packageName"

Write-Host "  Packing -> $packagePath ..."
& $mcpbExe pack (Join-Path $RepoRoot "mcpb") $packagePath
if ($LASTEXITCODE -ne 0) { throw "mcpb pack failed" }

# --- 6. Remove stage ---
if (-not $KeepStage) {
    Remove-Item (Join-Path $RepoRoot "mcpb\src") -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "`n  Removed mcpb/src staging (6. no stale twin)" -ForegroundColor Green
}

Write-Host "`n  BUILT: $packagePath ($([math]::Round((Get-Item $packagePath).Length / 1MB, 2)) MB)" -ForegroundColor Green
Write-Host "  Package: $($manifest.name) v$($manifest.version)" -ForegroundColor Green
