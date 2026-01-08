@echo off
setlocal

:: Configuración (Mismas credenciales que el bot original)
set GEMINI_API_KEY=AIzaSyDwfjNQrWfqME13GTioJ0vSHsdX86sv58o
set GMAIL_USER=curriculumfacilentregas@gmail.com
set GMAIL_APP_PASSWORD=hidv hwqe euln oubd

echo.
echo === INICIANDO INTERFAZ WEB DE CV ===
echo.
echo Abrí tu navegador en: http://localhost:5000
echo.

python app.py

pause
