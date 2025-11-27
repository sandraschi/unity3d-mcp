<#
.SYNOPSIS
    Run unity3d-mcp test suite

.DESCRIPTION
    Runs pytest with various options for the unity3d-mcp test suite.

.PARAMETER Coverage
    Generate coverage report

.PARAMETER Verbose
    Verbose output

.PARAMETER FailFast
    Stop on first failure

.PARAMETER Markers
    Run only tests with specific markers (e.g., "unit", "integration", "slow")

.PARAMETER Pattern
    Run tests matching pattern

.PARAMETER E2E
    Run end-to-end tests (requires Unity installed)

.PARAMETER Unit
    Run only unit tests

.PARAMETER Integration
    Run only integration tests

.EXAMPLE
    .\run-tests.ps1
    .\run-tests.ps1 -Coverage
    .\run-tests.ps1 -Verbose -FailFast
    .\run-tests.ps1 -Markers "not slow"
    .\run-tests.ps1 -Pattern "test_vrchat"
    .\run-tests.ps1 -E2E
#>

param(
    [switch]$Coverage,
    [switch]$Verbose,
    [switch]$FailFast,
    [switch]$E2E,
    [switch]$Unit,
    [switch]$Integration,
    [string]$Markers = "",
    [string]$Pattern = ""
)

$ErrorActionPreference = "Stop"

# Navigate to project root
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $ProjectRoot

try {
    # Set PYTHONPATH
    $env:PYTHONPATH = "$ProjectRoot\src;$ProjectRoot\tests"

    # Determine test path
    $testPath = "tests/"
    if ($Unit) {
        $testPath = "tests/unit/"
    } elseif ($Integration) {
        $testPath = "tests/integration/"
    } elseif ($E2E) {
        $testPath = "tests/e2e/"
    }

    # Build pytest command
    $pytestArgs = @("pytest", $testPath)

    if ($Verbose) {
        $pytestArgs += "-v"
    }

    if ($FailFast) {
        $pytestArgs += "-x"
    }

    if ($Coverage) {
        $pytestArgs += @(
            "--cov=src/unity3d_mcp",
            "--cov-report=term-missing",
            "--cov-report=html:coverage_html"
        )
    }

    if ($E2E) {
        $pytestArgs += "--run-e2e"
    }

    if ($Markers) {
        $pytestArgs += @("-m", $Markers)
    }

    if ($Pattern) {
        $pytestArgs += @("-k", $Pattern)
    }

    Write-Host "Running: $($pytestArgs -join ' ')" -ForegroundColor Cyan
    Write-Host ""

    # Run pytest
    & python -m $pytestArgs

    $exitCode = $LASTEXITCODE

    if ($Coverage -and $exitCode -eq 0) {
        Write-Host ""
        Write-Host "Coverage report generated in: $ProjectRoot\coverage_html\index.html" -ForegroundColor Green
    }

    exit $exitCode
}
finally {
    Pop-Location
}

