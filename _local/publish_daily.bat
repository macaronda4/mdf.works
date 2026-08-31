@echo off
rem 下書きを1本公開して push する。タスクスケジューラから1日1回呼ばれる。
rem 下書きが尽きたら何もせずに終わる。作業ツリーが汚れているときも中止する。
setlocal
cd /d "%~dp0.."

set LOG=%~dp0publish.log
set PYTHONIOENCODING=utf-8

for /f "tokens=1-3 delims=/ " %%a in ("%date%") do set TODAY=%%a-%%b-%%c
echo. >> "%LOG%"
echo ================ %TODAY% %time% ================ >> "%LOG%"

python "_local\publish_next.py" --write --push >> "%LOG%" 2>&1
set RC=%errorlevel%

rem このファイル自身の出力は ASCII にしておく（コードページによる文字化けを避ける）
if %RC%==0 (
  echo [OK] exit=0 >> "%LOG%"
) else (
  echo [NG] exit=%RC% >> "%LOG%"
)
exit /b %RC%
