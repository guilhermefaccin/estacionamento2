import os
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from banco.sessao import obter_sessao
from configuracao import obter_chave_jwt
from entidades.models import Usuario
from servicos.seguranca import verificar_senha

JWT_SECRET_KEY = obter_chave_jwt()
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Endpoint que futuramente receberá o login
oauth2_scheme = HTTPBearer(auto_error=False)


# Verifica e autentica o usuário pelo e-mail e senha
def autenticar_usuario(email: str, senha: str, db: Session):
    comando = select(Usuario).where(Usuario.email == email, Usuario.ativo.is_(True))

    usuario = db.exec(comando).first()

    if usuario is None or not usuario.senha:
        return None

    if not verificar_senha(senha, usuario.senha):
        return None

    return usuario


# Gera o token JWT
def criar_token_acesso(usuario: Usuario):
    expiracao = datetime.now(UTC) + timedelta(hours=8)

    dados_token = {
        "sub": str(usuario.id_usuario),
        "exp": expiracao,
        "perfil": usuario.perfil,
    }

    token = jwt.encode(dados_token, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    return token


# Recupera o usuário autenticado pelo token
def obter_usuario_logado(
    credenciais: HTTPAuthorizationCredentials | None = Depends(oauth2_scheme),
    db: Session = Depends(obter_sessao),
):
    erro_autenticacao = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credenciais is None:
        raise erro_autenticacao

    try:
        token = credenciais.credentials
        dados = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "exp"]},
        )

        id_usuario = int(dados.get("sub"))

    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise erro_autenticacao from None

    usuario = db.exec(
        select(Usuario).where(Usuario.id_usuario == id_usuario, Usuario.ativo.is_(True))
    ).first()

    if usuario is None:
        raise erro_autenticacao

    return usuario


# Permite acesso somente aos administradores
def exigir_admin(usuario: Usuario = Depends(obter_usuario_logado)):
    if usuario.perfil != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido somente para administradores.",
        )

    return usuario
