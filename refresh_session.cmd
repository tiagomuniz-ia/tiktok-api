@echo off
echo TikTok Session Generator
echo =======================
echo.

set /p USERNAME="Digite seu nome de usuário ou email do TikTok: "
set /p PASSWORD="Digite sua senha do TikTok: "

echo.
echo Iniciando processo de login...
python refresh_session.py "%USERNAME%" "%PASSWORD%"

echo.
echo Processo concluído.
pause 