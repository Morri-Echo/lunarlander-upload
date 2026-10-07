param([int]$Steps = 1000000, [string]$Backend = 'subproc')
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$python = Join-Path (Get-Location) '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { throw 'Create .venv and install requirements.txt first.' }
function Invoke-CheckedPython {
    & $python @args
    if ($LASTEXITCODE -ne 0) { throw "Python failed with exit code $LASTEXITCODE" }
}
Invoke-CheckedPython -m src.smoke_test
Invoke-CheckedPython -m src.train --steps $Steps --backend $Backend
Invoke-CheckedPython -m src.evaluate
Invoke-CheckedPython -m src.plot_results
Invoke-CheckedPython -m src.export_report
