@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
    python main.py
) else (
    py main.py
)
if errorlevel 1 (
    echo.
    echo If Pygame is missing, run: py -m pip install -r requirements.txt
    pause
)
