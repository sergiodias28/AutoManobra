@echo off
rem start_app_debug.bat - mostra logs em janelas separadas e ativa venv dentro de cada janela
setlocal
cd /d "%~dp0"

echo Diretório de trabalho: %CD%

rem Verifica se existe virtualenv
if exist "venv\Scripts\activate.bat" (
 set "VENV_EXISTS=1"
) else (
 set "VENV_EXISTS=0"
)

rem Escolhe porta para o servidor static (tenta 8000, se ocupada usa 8080)
set "PORT=8000"
netstat -ano | findstr ":%PORT%" >nul 2>&1
if %errorlevel% equ 0 (
 echo Porta %PORT% em uso, tentando 8080...
 set "PORT=8080"
)

rem Inicia Flask API em nova janela (exibe LOGS) usando pasta atual como working dir
if "%VENV_EXISTS%"=="1" (
 start "Flask API" /D "%CD%" cmd /k "if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat ^&^& echo Virtualenv ativada) else (echo Virtualenv nao encontrada) ^&^& python app.py"
) else (
 start "Flask API" /D "%CD%" cmd /k "echo Virtualenv nao encontrada; usando python do sistema ^&^& python app.py"
)

rem Inicia servidor HTTP estático em nova janela (exibe LOGS) com working dir definido
if "%VENV_EXISTS%"=="1" (
 start "Static Server" /D "%CD%" cmd /k "if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat ^&^& echo Servindo porta %PORT%) else (echo Servindo porta %PORT% com python do sistema) ^&^& python -m http.server %PORT% --bind 127.0.0.1"
) else (
 start "Static Server" /D "%CD%" cmd /k "echo Servindo porta %PORT% com python do sistema ^&^& python -m http.server %PORT% --bind 127.0.0.1"
)

rem Aguarda alguns segundos e abre o navegador se o arquivo existir
timeout /t 2 > nul
if exist "procedimento.html" (
 start "" "http://127.0.0.1:%PORT%/procedimento.html"
) else (
 echo Arquivo procedimento.html nao encontrado em %CD%
)

endlocal
exit /b 0