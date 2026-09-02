@echo off
rem ---------------------------------------------------------------------------
rem Publish one draft per day, then commit and push.
rem
rem NOTE: keep this file ASCII-only. cmd.exe reads .bat in the system ANSI
rem code page, so UTF-8 Japanese comments corrupt the commands themselves.
rem Anything that needs Japanese belongs in publish_next.py, not here.
rem ---------------------------------------------------------------------------
setlocal
cd /d "%~dp0.."

set "LOG=%~dp0publish.log"

rem Redirection goes first on purpose: a digit right before ">>" would be
rem read as a file handle, so "exit=%RC%>>" silently swallows the number.
>> "%LOG%" echo.
>> "%LOG%" echo ======== %date% %time% ========

rem --write already implies commit and push (use --no-push to keep it local)
>> "%LOG%" 2>&1 python "_local\publish_next.py" --write
set RC=%errorlevel%

if "%RC%"=="0" (
  >> "%LOG%" echo [OK] exit=%RC%
) else (
  >> "%LOG%" echo [NG] exit=%RC%
)

exit /b %RC%
