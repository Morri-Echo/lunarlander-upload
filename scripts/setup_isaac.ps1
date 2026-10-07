param([Parameter(Mandatory=$true)][string]$Python311)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
function Invoke-Checked {
    param([string]$Command, [string[]]$Arguments)
    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Command failed with exit code $LASTEXITCODE" }
}
$version = & $Python311 -c 'import sys; print(sys.version.split()[0])'
if ($LASTEXITCODE -ne 0 -or $version -notlike '3.11.*') { throw 'Isaac Sim 5.0 requires Python 3.11.' }
Invoke-Checked -Command $Python311 -Arguments @('-m', 'venv', '.venv-isaac')
$python = Join-Path (Get-Location) '.venv-isaac\Scripts\python.exe'
Invoke-Checked -Command $python -Arguments @('-m', 'pip', 'install', '--upgrade', 'pip')
Invoke-Checked -Command $python -Arguments @('-m', 'pip', 'install', 'isaacsim[all,extscache]==5.0.0', '--extra-index-url', 'https://pypi.nvidia.com')
if (-not (Test-Path 'external\IsaacLab')) {
    New-Item -ItemType Directory -Force external | Out-Null
    Invoke-Checked -Command 'git' -Arguments @('clone', '--depth', '1', '--branch', 'v2.2.0', 'https://github.com/isaac-sim/IsaacLab.git', 'external/IsaacLab')
}
Get-ChildItem 'external\IsaacLab\source' -Directory | Where-Object Name -Like 'isaaclab*' | ForEach-Object {
    Invoke-Checked -Command $python -Arguments @('-m', 'pip', 'install', '-e', $_.FullName)
}
Write-Output 'Installed. Review NVIDIA EULA, then run .venv-isaac\Scripts\python.exe -m src.isaac_check'
