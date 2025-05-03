@echo off
REM ──────────────────────────────────────────────
REM  rebuild‑api.bat
REM  Stop → Rebuild (no‑cache) → Start → Tail logs in a new window
REM ──────────────────────────────────────────────
setlocal

echo.
echo =============================================
echo  Docker API rebuild script
echo =============================================

echo.
echo [1/3] docker compose down
docker compose down
IF ERRORLEVEL 1 GOTO :error

echo.
echo [2/3] docker compose build --no-cache api
docker compose build --no-cache api
IF ERRORLEVEL 1 GOTO :error

echo.
echo [3/3] docker compose up -d
docker compose up -d
IF ERRORLEVEL 1 GOTO :error

echo.
echo ✅  Stack is up. A new window will show live API logs.
start "API logs" cmd /k "docker compose logs -f api"

echo.
echo Done! (close this window or run the script again whenever you need a rebuild)
GOTO :eof


:error
echo.
echo ❌  Something went wrong — check the message above.
pause
