@echo off
echo ========================================
echo Building CriticMarkup Editor Executable
echo ========================================
echo.

REM Set Python path
set PYTHON=C:\WPy64-31131\python\python.exe

REM Check if PyInstaller is installed
%PYTHON% -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    %PYTHON% -m pip install pyinstaller
    echo.
)

echo Cleaning previous builds...
if exist build\criticmarkup rmdir /s /q build\criticmarkup
if exist dist\CriticMarkupEditor.exe del /q dist\CriticMarkupEditor.exe
echo.

echo Building executable with PyInstaller...
%PYTHON% -m PyInstaller criticmarkup_editor.spec --clean
echo.

if exist dist\CriticMarkupEditor.exe (
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Executable location: dist\CriticMarkupEditor.exe
    echo File size: 
    dir dist\CriticMarkupEditor.exe | find "CriticMarkupEditor.exe"
    echo.
    echo You can now run: dist\CriticMarkupEditor.exe
    echo.
) else (
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    echo Check the output above for errors.
    echo.
)

pause
