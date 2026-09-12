@echo off
setlocal EnableDelayedExpansion

if "%~1"=="" (
    echo.
    echo Usage: filetool filename
    echo Example: filetool login.html
    echo.
    exit /b
)

set "TARGET=%~1"
set "FOUND="

echo.
echo Searching for %TARGET%...
echo.

for /f "delims=" %%F in ('dir /s /b "%CD%\%TARGET%" 2^>nul') do (
    set "FOUND=%%F"
    goto found
)

:found
if defined FOUND (
    echo FOUND:
    echo !FOUND!
    echo.
    echo Opening...
    start "" "!FOUND!"
    goto end
)

echo File not found: %TARGET%
echo.

set /p CREATE="Create it in the project root? (Y/N): "

if /i "!CREATE!"=="Y" (
    type nul > "%CD%\%TARGET%"
    echo Created:
    echo %CD%\%TARGET%
    start "" "%CD%\%TARGET%"
)

:end
endlocal