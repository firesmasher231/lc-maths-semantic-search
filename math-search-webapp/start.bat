@echo off
echo ============================================================
echo LC Maths Question Search Web Application
echo ============================================================
echo.

REM Check if user wants to configure port
if "%1"=="--configure" (
    echo Running configuration wizard...
    python configure.py
    echo.
    echo Configuration complete! Starting application...
    echo.
)

REM Set default port if not already set
if not defined FLASK_PORT (
    set FLASK_PORT=5000
)

REM Check if port is available (basic check)
netstat -an | find ":%FLASK_PORT%" >nul
if %errorlevel%==0 (
    echo ⚠️  Warning: Port %FLASK_PORT% appears to be in use.
    echo You can use a different port by running:
    echo    set FLASK_PORT=8080 ^&^& start.bat
    echo.
    echo Or run: start.bat --configure
    echo.
)

echo Starting the application on port %FLASK_PORT%...
echo This may take a few minutes on first run while processing PDFs.
echo.
echo Once ready, open your browser to: http://localhost:%FLASK_PORT%
echo.
echo 💡 Tips:
echo    - Use Ctrl+C to stop the application
echo    - Run 'start.bat --configure' to change port settings
echo    - Check QUICKSTART.md for more options
echo ============================================================
echo.

python app.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Application failed to start. Common solutions:
    echo    1. Install dependencies: pip install -r requirements.txt
    echo    2. Try a different port: set FLASK_PORT=8080 ^&^& start.bat
    echo    3. Check if Python is installed and in PATH
    echo.
)

pause 