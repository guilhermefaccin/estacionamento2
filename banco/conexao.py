
import os
from pathlib import Path

import mysql.connector
from sshtunnel import SSHTunnelForwarder
from dotenv import load_dotenv

# Localiza o arquivo .env na raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def obter_conexao():
    """
    Abre um túnel SSH e conecta ao MySQL.
    Retorna o túnel e a conexão para que ambos permaneçam ativos.
    """

    configuracao_ssh = {
        "host": os.getenv("SSH_HOST"),
        "port": int(os.getenv("SSH_PORT", "22")),
        "username": os.getenv("SSH_USER"),
        "password": os.getenv("SSH_PASSWORD"),
    }

    configuracao_mysql = {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DATABASE"),
        "connection_timeout": 10,
    }

    tunel = None

    try:
        tunel = SSHTunnelForwarder(
            (configuracao_ssh["host"], configuracao_ssh["port"]),
            ssh_username=configuracao_ssh["username"],
            ssh_password=configuracao_ssh["password"],
            remote_bind_address=(
                configuracao_mysql["host"],
                configuracao_mysql["port"],
            ),
            local_bind_address=("127.0.0.1", 0),
        )

        tunel.start()

        configuracao_mysql["host"] = "127.0.0.1"
        configuracao_mysql["port"] = tunel.local_bind_port

        conexao = mysql.connector.connect(**configuracao_mysql)

        return tunel, conexao

    except Exception:
        if tunel is not None and tunel.is_active:
            tunel.stop()

        raise
