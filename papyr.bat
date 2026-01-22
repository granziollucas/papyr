@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%~dp0src;%PYTHONPATH%"
if exist ".venv\\Scripts\\python.exe" (
  set "PYTHON=.venv\\Scripts\\python.exe"
) else (
  set "PYTHON=python"
)

if "%~1"=="" goto interactive
%PYTHON% -m papyr %*
if errorlevel 1 pause
goto :eof

:interactive
%PYTHON% -m papyr bootstrap
if errorlevel 1 pause
if errorlevel 1 goto :eof
echo Papyr shell. Type "help" for commands, "exit" to quit.
:loop
set /p PAPYR_CMD=papyr^> 
if "%PAPYR_CMD%"=="" goto loop
if /i "%PAPYR_CMD%"=="exit" goto :eof
if /i "%PAPYR_CMD%"=="quit" goto :eof
if /i "%PAPYR_CMD%"=="help" (
  echo Examples: init ^| new ^| resume ^<path^> ^| config show ^| doctor
  goto loop
)
%PYTHON% -m papyr %PAPYR_CMD%
if errorlevel 1 pause
goto loop
