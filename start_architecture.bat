@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" "scripts\build_architecture_data.py"
  if errorlevel 1 exit /b %errorlevel%
  ".venv\Scripts\python.exe" "scripts\package_architecture_html.py"
  if errorlevel 1 exit /b %errorlevel%
  ".venv\Scripts\python.exe" "scripts\serve_architecture.py"
) else (
  python "scripts\build_architecture_data.py"
  if errorlevel 1 exit /b %errorlevel%
  python "scripts\package_architecture_html.py"
  if errorlevel 1 exit /b %errorlevel%
  python "scripts\serve_architecture.py"
)
