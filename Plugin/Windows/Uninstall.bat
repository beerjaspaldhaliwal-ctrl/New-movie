@echo off
rem New Movie Library - removes the VST3 and CLAP plugin. Your samples are not touched.
setlocal EnableExtensions
title New Movie Library - Uninstall
net session >nul 2>&1
if errorlevel 1 (
  echo Asking for administrator rights...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath \"%~f0\" -Verb RunAs"
  exit /b
)
if exist "%CommonProgramFiles%\VST3\NewMovieLibrary.vst3" rmdir /S /Q "%CommonProgramFiles%\VST3\NewMovieLibrary.vst3"
if exist "%CommonProgramFiles%\CLAP\NewMovieLibrary.clap" del /Q "%CommonProgramFiles%\CLAP\NewMovieLibrary.clap"
if exist "%APPDATA%\NewMovieLibrary" rmdir /S /Q "%APPDATA%\NewMovieLibrary"
echo The plugin has been removed. The sample folder was left in place.
echo.
pause
