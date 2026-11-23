@echo off
setlocal
cd /d "%~dp0"
if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" run.py
) else (
    python run.py
)
endlocal
