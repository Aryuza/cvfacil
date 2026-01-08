@echo off
setlocal

:: Configuración (Puedes editar esto una sola vez)
set GEMINI_API_KEY=AIzaSyDwfjNQrWfqME13GTioJ0vSHsdX86sv58o
set GMAIL_USER=curriculumfacilentregas@gmail.com
set GMAIL_APP_PASSWORD=hidv hwqe euln oubd

:: Si no pasas carpeta al ejecutar, te la pide
if "%~1"=="" (
    set /p "CLIENT_FOLDER=Arrastra aqui la carpeta del cliente y presiona Enter: "
) else (
    set CLIENT_FOLDER=%~1
)

:: Quitar comillas si las hay
set CLIENT_FOLDER=%CLIENT_FOLDER:"=%

echo.
echo === INICIANDO AUTOMATIZACION DE CV ===
echo Procesando carpeta: "%CLIENT_FOLDER%"
echo.

python main.py "%CLIENT_FOLDER%"

echo.
echo === PROCESO TERMINADO ===
pause
