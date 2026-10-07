param([string]$Python = '', [switch]$Genesis)
$ErrorActionPreference = 'Stop'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    function Invoke-Checked {
        param([string]$Command, [string[]]$Arguments)
        & $Command @Arguments
        if ($LASTEXITCODE -ne 0) { throw "$Command failed with exit code $LASTEXITCODE" }
    }
    $launcher = if ($Python) { $Python } else { 'py' }
    $prefix = if ($Python) { @() } else { @('-3.9') }
    $version = & $launcher @prefix -c 'import sys; print(sys.version.split()[0])'
    if ($LASTEXITCODE -ne 0 -or $version -notlike '3.9.*') {
        throw 'Install Python 3.9 (64-bit), or pass -Python with its executable path.'
    }
    $environment = if ($Genesis) { '.venv-genesis' } else { '.venv' }
    $requirements = if ($Genesis) { 'requirements-genesis.txt' } else { 'requirements.txt' }
    $constraints = if ($Genesis) { 'requirements-genesis-lock.txt' } else { 'requirements-lock.txt' }
    Invoke-Checked -Command $launcher -Arguments ($prefix + @('-m', 'venv', $environment))
    $pythonExe = Join-Path (Get-Location) "$environment\Scripts\python.exe"
    Invoke-Checked -Command $pythonExe -Arguments @('-m', 'pip', 'install', '--upgrade', 'pip==25.3', 'setuptools==75.8.2', 'wheel==0.45.1')
    Invoke-Checked -Command $pythonExe -Arguments @('-m', 'pip', 'install', '-r', $requirements, '-c', $constraints)
    Invoke-Checked -Command $pythonExe -Arguments @('-m', 'pip', 'check')
    Write-Output "Ready: $environment. No activation is needed."
} finally {
    Pop-Location
}
