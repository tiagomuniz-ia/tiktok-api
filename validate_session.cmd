@echo off
echo TikTok Session Validator
echo ========================

if "%~1"=="" (
    echo Uso: %0 SESSION_ID
    echo.
    echo Exemplo: %0 abc123def456ghi789
    exit /b 1
)

echo Validando session_id: %1
python validate_session.py %1
pause 