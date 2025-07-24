@echo off
setlocal EnableDelayedExpansion

:: DockFlask Development Helper Script for Windows

set "command=%~1"

if "%command%"=="" set "command=help"

goto %command% 2>nul || goto help

:build
echo [INFO] Building DockFlask Docker image...
docker-compose build
if %errorlevel% equ 0 (
    echo [SUCCESS] Docker image built successfully!
) else (
    echo [ERROR] Failed to build Docker image
    exit /b 1
)
goto :eof

:run
echo [INFO] Starting DockFlask in production mode...
docker-compose up -d
if %errorlevel% equ 0 (
    echo [SUCCESS] Application started at http://localhost:5000
) else (
    echo [ERROR] Failed to start application
    exit /b 1
)
goto :eof

:dev
echo [INFO] Starting DockFlask in development mode...
docker-compose --profile dev up -d
if %errorlevel% equ 0 (
    echo [SUCCESS] Development server started at http://localhost:5001
) else (
    echo [ERROR] Failed to start development server
    exit /b 1
)
goto :eof

:stop
echo [INFO] Stopping DockFlask containers...
docker-compose down
if %errorlevel% equ 0 (
    echo [SUCCESS] Containers stopped successfully!
) else (
    echo [ERROR] Failed to stop containers
    exit /b 1
)
goto :eof

:clean
echo [INFO] Cleaning up containers and images...
docker-compose down --rmi all --volumes --remove-orphans
if %errorlevel% equ 0 (
    echo [SUCCESS] Cleanup completed!
) else (
    echo [ERROR] Failed to cleanup
    exit /b 1
)
goto :eof

:logs
echo [INFO] Showing application logs...
docker-compose logs -f
goto :eof

:health
echo [INFO] Checking application health...
docker-compose ps | findstr "Up" >nul
if %errorlevel% equ 0 (
    echo [SUCCESS] Container is running
    curl -f http://localhost:5000/api/health >nul 2>&1
    if !errorlevel! equ 0 (
        echo [SUCCESS] Health check passed!
        curl -s http://localhost:5000/api/health
    ) else (
        echo [WARNING] Health check failed - application may be starting up
    )
) else (
    echo [ERROR] Container is not running
    exit /b 1
)
goto :eof

:help
echo DockFlask Development Helper for Windows
echo.
echo Usage: %~nx0 [COMMAND]
echo.
echo Commands:
echo   build       Build the Docker image
echo   run         Run the application in production mode
echo   dev         Run the application in development mode
echo   stop        Stop all running containers
echo   clean       Remove containers and images
echo   logs        Show application logs
echo   health      Check application health
echo   help        Show this help message
echo.
goto :eof
