set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]
import 'scripts/just/fleet.just'

REPO := justfile_directory()

# --- Dashboard ---

# Open the interactive recipe dashboard in the browser
default:
    @just --list


# Synchronize deps, pre-commit hooks, and web frontend
bootstrap:
    uv sync --extra dev --group dev
    uv run pre-commit install
    Set-Location web_sota; npm ci; if ($LASTEXITCODE -ne 0) { npm install }
    Write-Host "Pre-commit hooks installed." -ForegroundColor Green
# --- Quality ---

# Execute Ruff SOTA v13.1 linting
lint:
    Set-Location '{{justfile_directory()}}'; uv run ruff check .; Set-Location '{{justfile_directory()}}\web_sota'; npx @biomejs/biome ci .

# Execute Ruff SOTA v13.1 fix and formatting
fix:
    Set-Location '{{justfile_directory()}}'; uv run ruff check . --fix --unsafe-fixes; uv run ruff format .; Set-Location '{{justfile_directory()}}\web_sota'; npx @biomejs/biome check --write .

# --- Hardening ---

# Execute Bandit security audit
check-sec:
    Set-Location '{{justfile_directory()}}'
    uv run bandit -r src/

# Execute safety audit of dependencies
audit-deps:
    Set-Location '{{justfile_directory()}}'
    uv run safety check
# --- Playwright E2E ---

# Install Playwright browsers (one-time)
e2e-install:
    cd {{REPO}}\web_sota
    npx playwright install chromium

# Run Playwright E2E smoke tests (start backend first: just serve)
e2e:
    cd {{REPO}}\web_sota
    npx playwright test

# --- Native build ---

# Build the PyInstaller backend .exe and copy to Tauri resources
build-sidecar:
    powershell.exe -NoProfile -File '{{justfile_directory()}}\native\build.ps1'

# Build the Tauri NSIS desktop installer
build-native: build-sidecar
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    Set-Location '{{justfile_directory()}}\native'
    npx @tauri-apps/cli build --bundles nsis


# Bootstrap: install dev deps + pre-commit hook
