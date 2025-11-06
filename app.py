import os
from flask import Flask, request, jsonify
import paramiko
from paramiko.ssh_exception import NoValidConnectionsError
from flask_cors import CORS
import socket
import logging
import re

# ----------------------------------------------------------------------
# ⚠️ Configuração de Segurança e Parâmetros
# ----------------------------------------------------------------------
# NOTA EDUCATIVA: É crucial nunca armazenar credenciais diretamente no código-fonte.
# Usamos variáveis de ambiente (os.environ.get) para simular uma prática segura.
# Para este exemplo, usamos os valores fornecidos.

SSH_HOST = '10.140.40.73'
SSH_USER = 'sagetr1'
SSH_PASS = 'sagetr1'

# Comando padrão para a Etapa1.10 (Abrir14D1) — código '52' e estado '0' separados por espaço
DEFAULT_COMMAND = "sage_ctrl CTM:14D1:52 0"

# ----------------------------------------------------------------------

app = Flask(__name__)
# Configuração para desenvolvimento: permite que o frontend (aberto via file:// ou localhost:8080)
# acesse esta API (rodando, por exemplo, em localhost:5000).
CORS(app) 

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

@app.route('/api/execute_ssh', methods=['POST'])
def execute_ssh_command():
    """
    Endpoint para executar comandos no servidor via SSH.
    Recebe um comando via POST e retorna a saída.
    """
    data = request.get_json(silent=True) or {}
    command = data.get('command') or DEFAULT_COMMAND
    app.logger.info("Payload recebido: %s", data)
    app.logger.info("Comando a executar (original): %s", command)

    # Normaliza comando curto do frontend: transforma sufixos numéricos tipo ':520' em '520'
    try:
        # encontra último ':' e verifica sufixo
        last_colon = command.rfind(':')
        if last_colon != -1:
            tail = command[last_colon+1:]
            # somente quando o sufixo for apenas dígitos, sem espaços, e tiver pelo menos3 dígitos
            if tail.isdigit() and len(tail) >=3 and ' ' not in tail:
                # ex: '520' -> '520'
                new_tail = tail[:-1] + ' ' + tail[-1]
                command = command[:last_colon+1] + new_tail
                app.logger.info("Comando normalizado: %s", command)
    except Exception as e:
        app.logger.warning("Falha ao normalizar comando: %s", e)

    # 1. Cria o cliente SSH
    ssh_client = paramiko.SSHClient()
    
    # Esta linha adiciona automaticamente a chave do host que você está tentando
    # se conectar ao seu arquivo de chaves de host (HostKeys), o que simplifica 
    # a conexão em ambientes controlados ou de teste.
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # 2. Conecta ao servidor
        app.logger.info(f"Conectando a {SSH_HOST} como {SSH_USER}...")
        ssh_client.connect(
            hostname=SSH_HOST, 
            username=SSH_USER, 
            password=SSH_PASS,
            timeout=10, # Define um tempo limite de10 segundos
            look_for_keys=False,
            allow_agent=False
        )
        app.logger.info("Conexão SSH estabelecida com sucesso.")

        # 3. Executa o comando
        stdin, stdout, stderr = ssh_client.exec_command(command, get_pty=True)
        output = stdout.read().decode(errors='replace').strip()
        error = stderr.read().decode(errors='replace').strip()
        try:
            exit_status = stdout.channel.recv_exit_status()
        except Exception:
            exit_status = None

        app.logger.info("exit_status=%s stdout=%s stderr=%s", exit_status, output, error)

        # 4. Verifica o status e formata a resposta
        resp = {
            "command_executed": command,
            "exit_status": exit_status,
            "server_output": output,
            "server_error": error
        }
        if error or (exit_status not in (0, None)):
            resp["status"] = "ERROR"
            return jsonify(resp),500
        resp["status"] = "SUCCESS"
        return jsonify(resp),200

    except paramiko.AuthenticationException:
        app.logger.error("Falha de autenticação")
        return jsonify({"status":"AUTH_ERROR","message":"Usuário/senha inválidos","command_executed":command}),401
    except (NoValidConnectionsError, socket.timeout, TimeoutError) as e:
        app.logger.error("Erro de conexão SSH: %s", e)
        return jsonify({"status":"CONNECTION_ERROR","message":str(e),"command_executed":command}),502
    except Exception as e:
        app.logger.exception("Erro inesperado")
        return jsonify({"status":"API_ERROR","message":str(e),"command_executed":command}),500
    finally:
        # 6. Fecha a conexão
        try:
            ssh_client.close()
            app.logger.info("Conexão SSH encerrada.")
        except Exception:
            pass

if __name__ == '__main__':
    app.logger.info("API iniciando em http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)