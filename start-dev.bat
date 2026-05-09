@echo off
setlocal EnableExtensions

set "ROOT=%~dp0"
set "BACKEND_DIR=%ROOT%backend"
set "FRONTEND_DIR=%ROOT%frontend"
set "BACKEND_HOST=0.0.0.0"
set "BACKEND_PORT=5000"
set "FRONTEND_HOST=localhost"
set "FRONTEND_PORT=5173"

title HPS Dev Launcher

echo ==================================================
echo   Hypertension Prediction System - Dev Mode
echo   Frontend: http://localhost:%FRONTEND_PORT%
echo   Backend:  http://localhost:%BACKEND_PORT%
echo ==================================================
echo.

call :require_dir "%BACKEND_DIR%" "backend" || goto :fail
call :require_dir "%FRONTEND_DIR%" "frontend" || goto :fail
call :require_file "%BACKEND_DIR%\app.py" "backend app entry" || goto :fail
call :require_file "%FRONTEND_DIR%\package.json" "frontend package.json" || goto :fail
call :require_command uv || goto :fail
call :require_command pnpm || goto :fail

if not exist "%BACKEND_DIR%\.venv\" (
    echo [INFO] Backend virtualenv not found. Running uv sync...
    pushd "%BACKEND_DIR%" || goto :fail
    call uv sync --locked
    if errorlevel 1 (
        popd
        goto :fail
    )
    popd
) else (
    echo [OK] Backend virtualenv found.
)

if not exist "%FRONTEND_DIR%\node_modules\" (
    echo [INFO] Frontend dependencies not found. Running pnpm install...
    pushd "%FRONTEND_DIR%" || goto :fail
    call pnpm install --frozen-lockfile
    if errorlevel 1 (
        popd
        goto :fail
    )
    popd
) else (
    echo [OK] Frontend dependencies found.
)

call :warn_port %BACKEND_PORT% "backend"
call :warn_port %FRONTEND_PORT% "frontend"

echo.
echo [INFO] Starting backend in a new terminal...
start "HPS Flask Backend :%BACKEND_PORT%" /D "%BACKEND_DIR%" cmd /k "set FLASK_DEBUG=1&& uv run flask --app app:create_app --debug run --host %BACKEND_HOST% --port %BACKEND_PORT%"

echo [INFO] Starting frontend dev server in this terminal...
echo [INFO] Press Ctrl+C here to stop the frontend. Close the backend window to stop Flask.
echo.

pushd "%FRONTEND_DIR%" || goto :fail
call pnpm dev -- --host %FRONTEND_HOST% --port %FRONTEND_PORT% --strictPort
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%

:require_command
where "%~1" >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Required command not found: %~1
    echo [ERROR] Install it and make sure it is available in PATH.
    exit /b 1
)
exit /b 0

:require_dir
if not exist "%~1\" (
    echo [ERROR] Missing %~2 directory: %~1
    exit /b 1
)
exit /b 0

:require_file
if not exist "%~1" (
    echo [ERROR] Missing %~2: %~1
    exit /b 1
)
exit /b 0

:warn_port
netstat -ano | findstr /R /C:":%~1 .*LISTENING" >nul 2>nul
if not errorlevel 1 (
    echo [WARN] Port %~1 is already in use; the %~2 server may fail to start.
)
exit /b 0

:fail
set "EXIT_CODE=%ERRORLEVEL%"
if "%EXIT_CODE%"=="0" set "EXIT_CODE=1"
echo.
echo [ERROR] Dev startup failed. See messages above.
exit /b %EXIT_CODE%
