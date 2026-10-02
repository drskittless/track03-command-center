param(
  [Parameter(Mandatory = $true, Position = 0)]
  [ValidateSet('parth', 'kshitij', 'prajjwal')]
  [string]$Role
)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $RepoRoot

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
  throw 'uv is required on Windows. Install uv for Windows, reopen PowerShell, then rerun scripts/setup.ps1.'
}
if (-not (Get-Command pnpm -ErrorAction SilentlyContinue)) {
  throw 'pnpm is required. Install Node.js and pnpm for Windows, reopen PowerShell, then rerun scripts/setup.ps1.'
}

Set-Content -LiteralPath '.role' -Value $Role -NoNewline
git config core.hooksPath .githooks
if ($LASTEXITCODE -ne 0) { throw 'git config core.hooksPath failed.' }
uv sync
if ($LASTEXITCODE -ne 0) { throw 'uv sync failed.' }

# WSL-created node_modules links are not executable from native Windows Node.
$WebRoot = (Resolve-Path 'apps/web').Path
$NodeModules = Join-Path $WebRoot 'node_modules'
$EslintShim = Join-Path $NodeModules '.bin/eslint'
$EslintWindowsShim = Join-Path $NodeModules '.bin/eslint.cmd'
$HasPosixShim = $false
if (Test-Path -LiteralPath $EslintShim) {
  $Shim = Get-Item -LiteralPath $EslintShim -Force
  if (($Shim.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
    $HasPosixShim = $true
  } else {
    $FirstLine = Get-Content -LiteralPath $EslintShim -TotalCount 1
    $HasPosixShim = $FirstLine -eq '#!/bin/sh'
  }
}
if ($HasPosixShim -and -not (Test-Path -LiteralPath $EslintWindowsShim)) {
  $ResolvedNodeModules = (Resolve-Path $NodeModules).Path
  $ExpectedNodeModules = Join-Path $RepoRoot 'apps/web/node_modules'
  if ($ResolvedNodeModules -ne $ExpectedNodeModules -or -not $ResolvedNodeModules.StartsWith("$RepoRoot\apps\web\node_modules", [StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to remove node_modules outside the expected repo path: $ResolvedNodeModules"
  }
  Remove-Item -LiteralPath $ResolvedNodeModules -Recurse -Force
}

pnpm -C apps/web install
if ($LASTEXITCODE -ne 0) { throw 'pnpm install failed.' }
Write-Output "setup done for $Role"
