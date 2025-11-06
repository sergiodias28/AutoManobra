# Projeto Flask para execução de comando SSH

Este projeto Flask permite executar o comando `sage_ctrl CTM:14D1:52 0` em uma máquina remota via SSH.

## Requisitos

- Python 3
- pip

## Instalação

1. Instale as dependências:
   pip install -r requirements.txt

## Execução com Gunicorn

Execute o servidor Flask em produção com Gunicorn:

   gunicorn -w 4 -b 0.0.0.0:5000 app:app

## Integração com Nginx (opcional)

Configure o Nginx como proxy reverso:

server {
    listen 80;
    server_name seu_dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
