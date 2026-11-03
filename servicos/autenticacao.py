
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from banco.sessao import obter_sessao
from entidades.models import Usuario
from servicos.seguranca import verificar_senha


# Carrega as configurações do .env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY não configurada no arquivo .env")


# Endpoint que futuramente receberá o login
oauth2_scheme = HTTPBearer()


# Verifica e autentica o usuário pelo e-mail e senha
def autenticar_usuario(email: str, senha: str, db: Session):
    comando = select(Usuario).where(
        Usuario.email == email,
        Usuario.ativo == True
    )

    usuario = db.exec(comando).first()

    if usuario is None or not usuario.senha:
        return None

    if not verificar_senha(senha, usuario.senha):
        return None

    return usuario


# Gera o token JWT
def criar_token_acesso(usuario: Usuario):
    expiracao = datetime.now(timezone.utc) + timedelta(hours=8)

    dados_token = {
        "sub": str(usuario.id_usuario),
        "exp": expiracao,
        "perfil": usuario.perfil
    }

    token = jwt.encode(
        dados_token,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

    return token


# Recupera o usuário autenticado pelo token
def obter_usuario_logado(
    credenciais: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(obter_sessao)
):
    erro_autenticacao = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        token = credenciais.credentials
        dados = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        id_usuario = int(dados.get("sub"))

    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise erro_autenticacao

    usuario = db.exec(
        select(Usuario).where(
            Usuario.id_usuario == id_usuario,
            Usuario.ativo == True
        )
    ).first()

    if usuario is None:
        raise erro_autenticacao

    return usuario


# Permite acesso somente aos administradores
def exigir_admin(
    usuario: Usuario = Depends(obter_usuario_logado)
):
    if usuario.perfil != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido somente para administradores."
        )

    return usuario
