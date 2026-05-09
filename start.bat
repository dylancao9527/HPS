@echo off
setlocal EnableExtensions

set "ROOT=%~dp0"
set "BACKEND_DIR=%ROOT%backend"
set "FRONTEND_DIR=%ROOT%frontend"
set "BACKEND_HOST=0.0.0.0"
set "BACKEND_PORT=5000"
set "SKIP_BUILD=0"

if /I "%~1"=="--skip-build" set "SKIP_BUILD=1"

title HPS Single Service

echo ==================================================
echo   Hypertension Prediction System - Single Service
echo   URL: http://localhost:%BACKEND_PORT%
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

if "%SKIP_BUILD%"=="1" (
    if not exist "%BACKEND_DIR%\static\index.html" (
        echo [ERROR] Cannot use --skip-build because backend\static\index.html is missing.
        goto :fail
    )
    echo [INFO] Skipping frontend build.
) else (
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

    echo [INFO] Building frontend into backend\static...
    pushd "%FRONTEND_DIR%" || goto :fail
    call pnpm build
    if errorlevel 1 (
        popd
        goto :fail
    )
    popd
    echo [OK] Frontend build complete.
)

call :warn_port %BACKEND_PORT% "backend"

echo.
echo [INFO] Starting Flask single service...
echo [INFO] Press Ctrl+C to stop.
echo.

pushd "%BACKEND_DIR%" || goto :fail
set "FLASK_DEBUG=0"
call uv run flask --app app:create_app run --host %BACKEND_HOST% --port %BACKEND_PORT%
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
echo [ERROR] Startup failed. See messages above.
exit /b %EXIT_CODE%
