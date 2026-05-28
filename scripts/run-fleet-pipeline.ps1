# Fleet E2E pipeline: blender-mcp export -> unity3d-mcp import -> validate -> build
#
# Examples:
#   .\scripts\run-fleet-pipeline.ps1 -ProjectPath "D:\Unity\MyProject" -ModelPath "D:\exports\avatar.glb" -SkipBuild
#   .\scripts\run-fleet-pipeline.ps1 -ProjectPath "D:\Unity\MyProject" -ObjectNames "Avatar"

param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectPath,

    [string]$ModelPath = "",
    [string]$BlenderUrl = "http://127.0.0.1:10849",
    [string]$UnityUrl = "http://127.0.0.1:10831",
    [string]$GazeboMcpUrl = "http://127.0.0.1:10991",
    [string[]]$GazeboModels = @(),
    [string]$GazeboFileTemplate = "gazebo_models/{model}.fbx",
    [switch]$WithGazebo,
    [switch]$TryGazeboMcpExport,
    [string]$ExportOperation = "export_glb",
    [string]$ExportDir = "",
    [string[]]$ObjectNames = @(),
    [string]$TargetPlatform = "vrchat",
    [string]$AvatarPrefab = "",
    [string]$BuildTarget = "StandaloneWindows64",
    [string]$BuildOutputDir = "",
    [double]$BuildTimeout = 3600,
    [switch]$SkipExport,
    [switch]$SkipValidate,
    [switch]$SkipBuild,
    [switch]$Json
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

$argsList = @(
    "run", "python", "scripts/fleet_pipeline.py",
    "--project-path", $ProjectPath,
    "--blender-url", $BlenderUrl,
    "--unity-url", $UnityUrl,
    "--gazebo-mcp-url", $GazeboMcpUrl,
    "--gazebo-file-template", $GazeboFileTemplate,
    "--export-operation", $ExportOperation,
    "--target-platform", $TargetPlatform,
    "--build-target", $BuildTarget,
    "--build-timeout", $BuildTimeout
)

if ($ModelPath) { $argsList += @("--model-path", $ModelPath) }
if ($GazeboModels -and $GazeboModels.Count -gt 0) {
    $argsList += @("--gazebo-models")
    $argsList += $GazeboModels
}
if ($WithGazebo) { $argsList += "--with-gazebo" }
if ($TryGazeboMcpExport) { $argsList += "--try-gazebo-mcp-export" }
if ($ExportDir) { $argsList += @("--export-dir", $ExportDir) }
if ($ObjectNames -and $ObjectNames.Count -gt 0) {
    $argsList += @("--object-names")
    $argsList += $ObjectNames
}
if ($AvatarPrefab) { $argsList += @("--avatar-prefab", $AvatarPrefab) }
if ($BuildOutputDir) { $argsList += @("--build-output-dir", $BuildOutputDir) }
if ($SkipExport) { $argsList += "--skip-export" }
if ($SkipValidate) { $argsList += "--skip-validate" }
if ($SkipBuild) { $argsList += "--skip-build" }
if ($Json) { $argsList += "--json" }

Write-Host "Running fleet pipeline for project: $ProjectPath"
uv @argsList
exit $LASTEXITCODE
