@echo off
REM ===========================================================================
REM  Build_Shocks.bat
REM  Regenerates every GDyn policy shock file for "Beyond Retaliation".
REM
REM  Double-click this file, or run it from a Command Prompt opened in the
REM  repository folder.  It writes to .\Shocks\ and overwrites what is there.
REM
REM  By default it uses the base tariff rates shipped in
REM  data\base_rates_RTMS.csv, so no GEMPACK toolchain is needed.
REM  To read the rates from your own aggregated database instead, put
REM  BaseRate.har in .\data\ and run:   Build_Shocks.bat --har
REM ===========================================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ============================================================
echo  Beyond Retaliation - GDyn shock file builder
echo ============================================================
echo  Working folder: "%CD%"
echo.

REM ---- 1. locate Python --------------------------------------------------
set "PY="
where py >nul 2>&1 && set "PY=py -3"
if not defined PY ( where python >nul 2>&1 && set "PY=python" )
if not defined PY (
    echo [ERROR] Python was not found on the PATH.
    echo         Install Python 3.9 or later from https://www.python.org/downloads/
    echo         and tick "Add python.exe to PATH" during setup.
    goto :fail
)
for /f "delims=" %%v in ('%PY% --version 2^>^&1') do set "PYVER=%%v"
echo  [1/4] Python found: !PYVER!

REM ---- 2. numpy ----------------------------------------------------------
%PY% -c "import numpy" >nul 2>&1
if errorlevel 1 (
    echo  [2/4] Installing numpy...
    %PY% -m pip install --quiet --upgrade numpy
    if errorlevel 1 (
        echo [ERROR] Could not install numpy. Check your internet connection
        echo         or run:  %PY% -m pip install numpy
        goto :fail
    )
) else (
    echo  [2/4] numpy already installed
)

REM ---- 3. optional: HARPY, only needed for the --har route ---------------
if /i "%~1"=="--har" (
    if not exist "data\BaseRate.har" (
        echo [ERROR] --har was requested but "data\BaseRate.har" does not exist.
        echo         Copy BaseRate.har from your aggregated GTAP 11 database
        echo         into the data\ folder, or run without --har.
        goto :fail
    )
    %PY% -c "import harpy" >nul 2>&1
    if errorlevel 1 (
        echo  [3/4] Installing HARPY ^(needs git^)...
        %PY% -m pip install --quiet "git+https://github.com/GEMPACKsoftware/HARPY.git"
        if errorlevel 1 (
            echo [WARN] HARPY install failed - is git installed and on the PATH?
            echo        Falling back to data\base_rates_RTMS.csv.
        )
    ) else (
        echo  [3/4] HARPY already installed
    )
    set "ARGS=--har data\BaseRate.har"
) else (
    echo  [3/4] Using shipped base rates ^(data\base_rates_RTMS.csv^)
    set "ARGS="
)

REM ---- 4. build ----------------------------------------------------------
echo  [4/4] Building shock files...
echo.
%PY% "build_shocks.py" !ARGS! --out "Shocks"
if errorlevel 1 (
    echo.
    echo [ERROR] build_shocks.py failed or the self-check did not pass.
    echo         DO NOT run the generated files. Read the messages above.
    goto :fail
)

echo.
echo ============================================================
echo  DONE. 21 shock files written to "%CD%\Shocks"
echo.
echo  Next: open RunDynam and set the closure and shock file for
echo  each period as set out in section 1 of README.md.
echo ============================================================
echo.
pause
endlocal
exit /b 0

:fail
echo.
echo ============================================================
echo  BUILD FAILED - no files were written.
echo ============================================================
echo.
pause
endlocal
exit /b 1
