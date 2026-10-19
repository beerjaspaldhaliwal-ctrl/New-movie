@echo off
rem New Movie Library - installs the VST3 and CLAP plugin and tells it where the samples are.
rem Double-click this file inside the Plugin\Windows folder of the download.
setlocal EnableExtensions
chcp 65001 >nul
title New Movie Library - Install

rem The plugin folders are system folders, so ask for administrator rights once.
net session >nul 2>&1
if errorlevel 1 (
  echo Asking for administrator rights...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath \"%~f0\" -Verb RunAs"
  exit /b
)
cd /d "%~dp0"

set "VST3DIR=%CommonProgramFiles%\VST3"
set "CLAPDIR=%CommonProgramFiles%\CLAP"
echo.
echo  NEW MOVIE LIBRARY
echo  =================
echo.
echo Installing the plugin...
if not exist "%VST3DIR%" mkdir "%VST3DIR%"
if not exist "%CLAPDIR%" mkdir "%CLAPDIR%"
if exist "%VST3DIR%\NewMovieLibrary.vst3" rmdir /S /Q "%VST3DIR%\NewMovieLibrary.vst3"
xcopy /E /I /Y /Q "NewMovieLibrary.vst3" "%VST3DIR%\NewMovieLibrary.vst3" >nul
copy /Y "NewMovieLibrary.clap" "%CLAPDIR%\NewMovieLibrary.clap" >nul
if not exist "%VST3DIR%\NewMovieLibrary.vst3\Contents\x86_64-win\NewMovieLibrary.vst3" goto :fail
if not exist "%CLAPDIR%\NewMovieLibrary.clap" goto :fail
echo   VST3  %VST3DIR%\NewMovieLibrary.vst3
echo   CLAP  %CLAPDIR%\NewMovieLibrary.clap

rem The sample library sits two folders up: <download>\New Movie Library
for %%I in ("%~dp0..\..\New Movie Library") do set "LIB=%%~fI"
if not exist "%LIB%\Samples\02 Orchestral" (
  echo.
  echo The "New Movie Library" sample folder was not found next to the Plugin folder.
  echo Open the plugin in your DAW and use "Find the sample library" to point it there.
  goto :done
)
echo.
echo The samples are here:
echo   %LIB%
echo.
echo   [1] Leave them where they are ^(keep this download folder^)
echo   [2] Copy them to Documents\New Movie Library ^(about 470 MB^)
echo.
choice /C 12 /N /M "Press 1 or 2: "
if errorlevel 2 goto :copylib
set "TARGET=%LIB%"
goto :remember

:copylib
set "DOCS="
for /f "usebackq tokens=2,*" %%A in (`reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" /v Personal 2^>nul ^| find "Personal"`) do set "DOCS=%%B"
if defined DOCS call set "DOCS=%DOCS%"
if not defined DOCS set "DOCS=%USERPROFILE%\Documents"
set "TARGET=%DOCS%\New Movie Library"
echo Copying the samples to "%TARGET%" ...
robocopy "%LIB%" "%TARGET%" /E /NFL /NDL /NJH /NJS /NP >nul
if errorlevel 8 goto :fail

:remember
if not exist "%APPDATA%\NewMovieLibrary" mkdir "%APPDATA%\NewMovieLibrary"
<nul set /p "=%TARGET%" > "%APPDATA%\NewMovieLibrary\library_path.txt"
echo Sample location saved: %TARGET%

:done
echo.
echo Finished. In your DAW, rescan plugins and load "New Movie Library" as an instrument.
echo.
pause
exit /b 0

:fail
echo.
echo Something went wrong. You can also install by hand: see Plugin\README.md.
echo.
pause
exit /b 1
