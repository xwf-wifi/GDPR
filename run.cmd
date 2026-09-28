@echo off
cd /d "%~dp0"
if "%~1"=="" (
  echo Usage: run.cmd baidu.com
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo Run setup.cmd first.
  exit /b 1
)
".venv\Scripts\python.exe" collect.py --domain "%~1"
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" export_workbook.py
if errorlevel 1 exit /b 1
echo Open reports\GDPR_review.xlsx and review the row for %1.
