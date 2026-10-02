$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $RepoRoot

uv run python -m scripts.gen_contract
if ($LASTEXITCODE -ne 0) { throw 'Contract schema generation failed.' }
pnpm -C apps/web gen:types
if ($LASTEXITCODE -ne 0) { throw 'Frontend type generation failed.' }
