@echo off
setlocal ENABLEDELAYEDEXPANSION

set PYTHON=python
if exist "..\cea\Scripts\python.exe" set PYTHON=..\cea\Scripts\python.exe

%PYTHON% -m pip install --upgrade pip
%PYTHON% -m pip install pyinstaller -r requirements.txt

if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

set COMMON_ARGS=--name CryptoAdventureRPG --clean --noupx --add-data assets;assets --add-data data;data --add-data save;save

if /I "%1"==--onefile (
  set MODE_ARGS=--onefile
) else (
  set MODE_ARGS=--onedir
)

%PYTHON% -m PyInstaller %MODE_ARGS% %COMMON_ARGS% --console main.py

echo.
echo Build finished: dist
if /I "%1"==--onefile (
  echo Run: dist\CryptoAdventureRPG.exe
) else (
  echo Run: dist\CryptoAdventureRPG\main.exe
)
endlocal 