@echo off
echo ========================================
echo Building Typora Theme Editor Executable
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
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo.

echo Building executable with PyInstaller...
%PYTHON% -m PyInstaller theme_editor.spec --clean
echo.

if exist dist\TyporaThemeEditor.exe (
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Executable location: dist\TyporaThemeEditor.exe
    echo File size: 
    dir dist\TyporaThemeEditor.exe | find "TyporaThemeEditor.exe"
    echo.
    echo You can now run: dist\TyporaThemeEditor.exe
    echo.
) else (
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    echo Check the output above for errors.
    echo.
)

pause
