@echo off
REM WordPress WebP Image Replacer - Windows Launcher

echo Starting WordPress WebP Image Replacer...
echo.

REM Check if uv is installed
where uv >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: UV package manager not found!
    echo.
    echo Please install UV first:
    echo   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo.
    pause
    exit /b 1
)

REM Check if config.json exists
if not exist "config.json" (
    echo WARNING: config.json not found!
    echo.
    echo Copying config.example.json to config.json...
    copy config.example.json config.json
    echo.
    echo Please edit config.json with your WordPress credentials.
    echo Then run this script again.
    echo.
    pause
    exit /b 1
)

REM Sync dependencies
echo Installing/updating dependencies...
uv sync

REM Run the application
echo.
echo Launching application...
uv run python main.py

REM Keep window open if there's an error
if %ERRORLEVEL% neq 0 (
    echo.
    echo Application exited with error code %ERRORLEVEL%
    pause
)
