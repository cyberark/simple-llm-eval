@echo off
REM Enable immediate exit on error
setlocal enabledelayedexpansion

REM Each command should be followed by '|| exit /b' to stop execution if it fails
command1 || exit /b
command2 || exit /b
