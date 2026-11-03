from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from banco.sessao import obter_sessao
from entidades.models import Usuario
from schemas.autenticacao import AlterarSenhaRequest, LoginRequest, LoginResposta
from servicos.autenticacao import (
    autenticar_usuario,
    criar_token_acesso,
    exigir_admin,
)
from servicos.seguranca import gerar_hash_senha, verificar_senha

router = APIRouter(tags=["Autenticação"])


@router.patch("/admin/alterar-senha", status_code=200)
def alterar_senha_admin(
    dados: AlterarSenhaRequest,
    usuario: Usuario = Depends(exigir_admin),
    db: Session = Depends(obter_sessao),
):
    # Confere a senha atual
    if not verificar_senha(dados.senha_atual, usuario.senha):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A senha atual está incorreta.",
        )

    # Confere se as novas senhas são iguais
    if dados.nova_senha != dados.confirmar_nova_senha:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A confirmação da nova senha não corresponde.",
        )

    # Gera o hash da nova senha
    usuario.senha = gerar_hash_senha(dados.nova_senha)

    db.add(usuario)
    db.commit()

    return {"mensagem": "Senha alterada com sucesso."}


@router.post("/login", response_model=LoginResposta)
def login(dados: LoginRequest, db: Session = Depends(obter_sessao)):
    usuario = autenticar_usuario(email=str(dados.email), senha=dados.senha, db=db)

    if usuario is None:
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")

    token = criar_token_acesso(usuario)

    return LoginResposta(access_token=token, token_type="bearer")
