"""Configurações compartilhadas pela API e pelos comandos locais."""

import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
USAR_MYSQL_LEGADO = not DATABASE_URL and bool(os.getenv("MYSQL_DATABASE"))
if not DATABASE_URL and not USAR_MYSQL_LEGADO:
    DATABASE_URL = f"sqlite:///{(BASE_DIR / 'estacionamento.db').as_posix()}"


def obter_chave_jwt() -> str:
    chave = os.getenv("JWT_SECRET_KEY")
    if chave:
        return chave
    if USAR_MYSQL_LEGADO or not DATABASE_URL.startswith("sqlite:"):
        raise RuntimeError(
            "Configure JWT_SECRET_KEY no arquivo .env para usar banco remoto."
        )

    # Persiste a chave local para manter as sessões após reiniciar o servidor.
    caminho = BASE_DIR / ".jwt_secret"
    try:
        with caminho.open("x", encoding="utf-8") as arquivo:
            arquivo.write(secrets.token_urlsafe(48))
    except FileExistsError:
        pass
    return caminho.read_text(encoding="utf-8").strip()
