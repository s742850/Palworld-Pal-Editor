@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run install-local.ps1 first.
  pause
  exit /b 1
)
set "PYTHONPATH=%~dp0src"
set "PYTHONUTF8=1"
set "PAL_EDITOR_ALLOW_REMOTE="
".venv\Scripts\python.exe" -m palworld_pal_editor --mode gui --lang zh-TW --nocli
if errorlevel 1 pause
