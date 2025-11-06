import paramiko
import sys
import os

# --- Configurações de Acesso SSH ---
# Substitua estas variáveis pelas credenciais reais e pelo host.
# É altamente recomendado usar variáveis de ambiente ou um sistema de segredos
# para armazenar credenciais em produção, em vez de codificá-las aqui.
REMOTE_HOST = '10.140.40.73'
REMOTE_COMMAND = 'sage_ctrl CTM:14D1:52 0'
SSH_USER = 'sagetr1'
# Para autenticação baseada em senha (NÃO recomendado para automação):
SSH_PASSWORD = 'sagetr1' 
# Para autenticação baseada em chave (RECOMENDADO):
# PATH_TO_KEY = '/caminho/para/sua/chave_privada'

def execute_remote_command(hostname, username, command, password=None, key_filename=None):
    """
    Conecta-se a um servidor remoto via SSH e executa um comando.

    Args:
        hostname (str): O endereço IP ou nome do host.
        username (str): O nome de usuário SSH.
        command (str): O comando a ser executado.
        password (str, opcional): Senha para autenticação.
        key_filename (str, opcional): Caminho para o arquivo de chave privada.

    Returns:
        tuple: (exit_status, stdout_output, stderr_output)
    """
    ssh_client = paramiko.SSHClient()
    # Esta linha adiciona automaticamente a chave do host (se não estiver no known_hosts),
    # mas em produção, use um arquivo known_hosts configurado para segurança máxima.
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    
    print(f"Tentando conectar a {hostname} como usuário {username}...")

    try:
        # Tenta conectar usando senha ou chave
        ssh_client.connect(
            hostname=hostname,
            username=username,
            password=password,
            key_filename=key_filename
        )
        
        print(f"Conexão SSH bem-sucedida. Executando comando: '{command}'")
        
        # Executa o comando
        stdin, stdout, stderr = ssh_client.exec_command(command)
        
        # Lê a saída (stdout) e o erro (stderr)
        stdout_output = stdout.read().decode().strip()
        stderr_output = stderr.read().decode().strip()
        
        # Obtém o status de saída (0 geralmente indica sucesso)
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Comando executado com sucesso.")
        else:
            print(f"Comando falhou. Status de saída: {exit_status}")
        
        return exit_status, stdout_output, stderr_output

    except paramiko.AuthenticationException:
        print("Erro de autenticação. Verifique o usuário, senha ou chave.")
        return 1, "", "Authentication failed."
    except paramiko.SSHException as e:
        print(f"Erro SSH: {e}")
        return 1, "", f"SSH error: {e}"
    except Exception as e:
        print(f"Erro ao conectar ou executar comando: {e}")
        return 1, "", f"Connection/Execution error: {e}"
    finally:
        if 'ssh_client' in locals() and ssh_client:
            ssh_client.close()
            print("Conexão SSH encerrada.")

if __name__ == "__main__":
    # Exemplo de uso
    
    # 1. Configurar credenciais:
    # Escolha UMA forma de autenticação. Chave é a mais segura.
    
    # Exemplo 1: Autenticação por CHAVE (mais seguro)
    # exit_code, out, err = execute_remote_command(
    #     REMOTE_HOST,
    #     SSH_USER,
    #     REMOTE_COMMAND,
    #     key_filename=PATH_TO_KEY 
    # )

    # Exemplo 2: Autenticação por SENHA (ATIVADO com as credenciais fornecidas)
    exit_code, out, err = execute_remote_command(
        REMOTE_HOST,
        SSH_USER,
        REMOTE_COMMAND,
        password=SSH_PASSWORD
    )

    # Exemplo 3: Usando um método simples para demonstração (substitua conforme necessário)
    # *** ESTE BLOCO FOI DESATIVADO POIS O EXEMPLO 2 FOI ATIVADO ***
    # key_path = os.path.expanduser('~/.ssh/id_rsa') 
    # if os.path.exists(key_path) and not SSH_USER == 'seu_usuario_ssh':
    #     print("Tentando autenticar via chave padrão...")
    #     exit_code, out, err = execute_remote_command(
    #         REMOTE_HOST,
    #         SSH_USER,
    #         REMOTE_COMMAND,
    #         key_filename=key_path
    #     )
    # else:
    #     print("Usuário e/ou caminho da chave não configurados corretamente. Script de demonstração.")
    #     exit_code, out, err = 1, "", "Configuração de usuário/chave necessária."

    # --- Resultado ---
    print("\n--- Resultado da Execução ---")
    print(f"Status de Saída: {exit_code}")
    if out:
        print("\nSaída Padrão (STDOUT):")
        print(out)
    if err:
        print("\nSaída de Erro (STDERR):")
        print(err)

    sys.exit(exit_code)