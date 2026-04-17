@echo off
:: ============================================================
::  compilar.bat — Empaqueta el Sistema de Retiros como .exe
::  Ejecuta este archivo desde la raiz del proyecto (junto a main.py)
:: ============================================================
title Compilando Sistema de Retiros...
echo.
echo  =========================================
echo   Sistema de Retiros
echo   Empaquetador automatico con PyInstaller
echo  =========================================
echo.

:: 1) Verificar que Python este instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python no encontrado.
    echo  Descargalo en https://www.python.org/downloads/
    echo  Asegurate de marcar "Add Python to PATH" al instalar.
    pause
    exit /b 1
)
echo  [OK] Python detectado:
python --version

:: 2) Instalar/actualizar dependencias
echo.
echo  [1/4] Instalando dependencias...
pip install reportlab openpyxl pyinstaller --quiet --no-index --find-links packages\
if errorlevel 1 (
    echo  [ERROR] Fallo la instalacion de dependencias.
    pause
    exit /b 1
)
echo        OK

:: 3) Limpiar compilaciones anteriores
echo  [2/4] Limpiando compilaciones anteriores...
if exist build  rmdir /s /q build
if exist dist   rmdir /s /q dist
echo        OK

:: 4) Compilar con el .spec
echo  [3/4] Compilando... (puede tardar 1-3 minutos)
pyinstaller GDR_Sistema_Retiros.spec
if errorlevel 1 (
    echo.
    echo  [ERROR] Fallo la compilacion. Revisa los mensajes de arriba.
    pause
    exit /b 1
)

:: 5) Copiar la base de datos al lado del .exe
echo  [4/4] Copiando base de datos...
if exist data\retiros.db (
    copy /y data\retiros.db dist\SistemaRetiros\data\retiros.db >nul
    echo        Copiado: data\retiros.db
) else (
    :: Si no existe aun (primera vez), crear la carpeta vacia
    :: La app la creara sola al arrancar por primera vez
    if not exist dist\SistemaRetiros\data mkdir dist\SistemaRetiros\data
    echo        Carpeta data\ creada (la BD se generara al primer arranque)
)

echo.
echo  =========================================
echo   LISTO! La aplicacion esta en:
echo.
echo   dist\SistemaRetiros\SistemaRetiros.exe
echo.
echo   Copia TODA la carpeta dist\SistemaRetiros\
echo   a cualquier PC con Windows para distribuirla.
echo  =========================================
echo.
pause
