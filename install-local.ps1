param([string]$Python = "python", [string]$Pnpm = "pnpm")
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

function Invoke-Checked {
    param([string]$Command, [string[]]$Arguments)
    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Command failed: $Command (exit $LASTEXITCODE)" }
}

# No activation, administrator privileges, registry edits or firewall exceptions.
Invoke-Checked $Python @('-c', 'import sys; assert sys.version_info >= (3,11), "Python 3.11+ required"')
if (!(Test-Path -LiteralPath '.venv/Scripts/python.exe')) {
    Invoke-Checked $Python @('-m', 'venv', '.venv')
}
$taskPython = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
Invoke-Checked $taskPython @('-m', 'pip', 'install', 'pip==26.2.2')
$taskRequirements = @(Get-Content -LiteralPath requirements.txt | Where-Object { $_ -and $_ -notmatch '^git\+' })
Invoke-Checked $taskPython (@('-m', 'pip', 'install') + $taskRequirements + @('ziglang==0.13.0', 'loguru==0.7.3', 'orjson==3.13.0'))
Invoke-Checked $taskPython @('scripts/build_ooz_windows.py')
Invoke-Checked $taskPython @('-m', 'pip', 'install', '--force-reinstall', '.venv/build/pyooz-0.1.0-cp38-abi3-win_amd64.whl')
# Dependencies are installed explicitly above: do not fall back to the PyPI
# decompressor-only pyooz package, which cannot write modern game saves.
Invoke-Checked $taskPython @('-m', 'pip', 'install', '--no-deps', 'git+https://github.com/KrisCris/palworld-save-tools.git@82dc6ad06e6162b29c0ef7d321fed2a73609a4d6')
Invoke-Checked $taskPython @('-m', 'pip', 'check')
Invoke-Checked $taskPython @('-c', 'import ooz; assert callable(ooz.compress), "Compression support required"')
Push-Location -LiteralPath 'frontend/palworld-pal-editor-webui'
try {
    Invoke-Checked $Pnpm @('install', '--frozen-lockfile', '--ignore-scripts')
    Invoke-Checked $Pnpm @('run', 'build')
} finally { Pop-Location }
$taskWebRoot = Join-Path $PSScriptRoot 'src/palworld_pal_editor/webui'
New-Item -ItemType Directory -Path $taskWebRoot -Force | Out-Null
Copy-Item -Path 'frontend/palworld-pal-editor-webui/dist/*' -Destination $taskWebRoot -Recurse -Force
Write-Host 'Installed. Run start-local.cmd. No game saves have been changed.'
