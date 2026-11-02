[CmdletBinding()]
param(
    [string]$CodexHome = $(
        if ($env:CODEX_HOME) {
            $env:CODEX_HOME
        } else {
            Join-Path $HOME '.codex'
        }
    ),
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

$sourceRoot = Join-Path $PSScriptRoot 'skills'
$codexPath = [System.IO.Path]::GetFullPath($CodexHome)
$destRoot = Join-Path $codexPath 'skills'

if (-not (Test-Path -LiteralPath $sourceRoot -PathType Container)) {
    throw "Skill source directory not found: $sourceRoot"
}

New-Item -ItemType Directory -Path $destRoot -Force | Out-Null

$skills = Get-ChildItem -LiteralPath $sourceRoot -Directory
foreach ($skill in $skills) {
    $target = Join-Path $destRoot $skill.Name
    if (Test-Path -LiteralPath $target) {
        if (-not $Force) {
            throw "Skill already exists: $target. Re-run with -Force after reviewing the existing version."
        }

        $resolvedTarget = [System.IO.Path]::GetFullPath($target)
        $expectedPrefix = [System.IO.Path]::GetFullPath($destRoot) +
            [System.IO.Path]::DirectorySeparatorChar
        if (-not $resolvedTarget.StartsWith(
                $expectedPrefix,
                [System.StringComparison]::OrdinalIgnoreCase
            )) {
            throw "Refusing to replace a path outside the destination: $resolvedTarget"
        }

        Remove-Item -LiteralPath $resolvedTarget -Recurse -Force
    }

    Copy-Item -LiteralPath $skill.FullName -Destination $destRoot -Recurse
    Write-Host "Installed $($skill.Name) -> $target"
}

Write-Host "Installed $($skills.Count) skill(s) under $destRoot"
