@echo off
rem - start_app.bat
rem - Inicia virtualenv (se existir), a API Flask e um servidor HTTP estático; abre o navegador.
rem - Salve este arquivo na raiz do projeto (mesma pasta de app.py e procedimento.html).
setlocal

rem Muda para a pasta do script (garante que seja executado a partir do repo)
cd /d "%~dp0"

echo Iniciando procedimento de inicializacao...
echo Diretório de trabalho: %CD%

rem Ativa virtualenv se existir em .\venv\Scripts\activate.bat
if exist "venv\Scripts\activate.bat" (
    echo Ativando virtualenv...
    call "venv\Scripts\activate.bat"
) else (
    echo Virtualenv nao encontrada em venv\Scripts\activate.bat — executando com o Python do sistema.
)

rem Cria pasta de logs se nao existir
if not exist "logs" mkdir logs

rem Inicia Flask API em nova janela de console (saida direcionada para logs\flask.log)
echo Abrindo janela para Flask API (porta 5000)...
start "Flask API" cmd /k "python app.py > logs\flask.log 2>&1"

rem Inicia servidor http estático em nova janela (porta 8000) (saida em logs\http.log)
echo Abrindo janela para servidor HTTP estático (porta 8000)...
start "Static Server" cmd /k "python -m http.server 8000 > logs\http.log 2>&1"

rem Aguarda 1s para dar tempo de inicializacao e abre a pagina no navegador padrão
timeout /t 1 > nul
echo Abrindo navegador na pagina de procedimento...
start "" "http://127.0.0.1:8000/procedimento.html"

echo Inicializacao solicitada. Veja logs em %CD%\logs\ (flask.log, http.log).
endlocal
exit /b 0