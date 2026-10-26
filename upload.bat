@echo off
setlocal
chcp 65001 >nul 2>nul
title BIP Update - buat paket + push GitHub
cd /d "%~dp0"

set "PYEXE="
for /f "usebackq delims=" %%i in (`py -3 -c "import sys;print(sys.executable)" 2^>nul`) do if not defined PYEXE set "PYEXE=%%i"
if not defined PYEXE for /f "usebackq delims=" %%i in (`python -c "import sys;print(sys.executable)" 2^>nul`) do if not defined PYEXE set "PYEXE=%%i"
if not defined PYEXE (
  echo.
  echo   [X] Python tidak ditemukan.
  echo.
  pause
  exit /b 1
)

"%PYEXE%" -c "import pyzipper" >nul 2>nul
if errorlevel 1 (
  echo   [*] Memasang pyzipper...
  "%PYEXE%" -m pip install --disable-pip-version-check -q pyzipper
  if errorlevel 1 (
    echo   [X] Gagal memasang pyzipper.
    pause
    exit /b 1
  )
)

echo.
echo   [*] Membuat ZIP berpassword + update.json...
"%PYEXE%" "%~dp0buat_paket.py"
if errorlevel 1 (
  echo   [X] Gagal membuat paket.
  pause
  exit /b 1
)

echo.
echo   [*] Commit & push ke GitHub...
git add -A
git commit -m "Update paket BIP"
if errorlevel 1 (
  echo   [!] Tidak ada perubahan baru atau commit gagal.
)

git push origin main
set "RC=%ERRORLEVEL%"
echo.
if "%RC%"=="0" (
  echo   [SELESAI] Paket sudah di-push ke GitHub.
) else (
  echo   [GAGAL] Push gagal. Pastikan token GitHub sudah benar.
)
pause
exit /b %RC%
