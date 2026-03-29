@echo off
echo === LeCroy Options Recovery - Windows Build ===
echo.

echo [1/2] Installing dependencies...
pip install pycryptodome pyinstaller
if errorlevel 1 (
    echo ERROR: pip install failed.
    pause
    exit /b 1
)

echo.
echo [2/2] Building executables...

pyinstaller --onefile --clean --name gen      gen.py
pyinstaller --onefile --clean --name list     list.py
pyinstaller --onefile --clean --name validate validate.py

echo.
echo === Build complete ===
echo Executables are in: dist\
echo   dist\gen.exe
echo   dist\list.exe
echo   dist\validate.exe
pause
