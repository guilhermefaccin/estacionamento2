from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import Session

from banco.sessao import obter_sessao
from entidades import models
from entidades.models import Usuario
from schemas.usuario import (
    UsuarioAtualizar,
    UsuarioCriar,
    UsuarioResposta,
)
from servicos.autenticacao import (
    exigir_admin,
)
from servicos.usuario import (
    atualizar_usuario,
    buscar_usuario_por_id,
    cadastrar_usuario,
    desativar_usuario,
    listar_usuarios,
)

router = APIRouter(tags=["Usuários"])


@router.post("/usuarios", response_model=UsuarioResposta, status_code=201)
def criar_usuario(
    dados: UsuarioCriar,
    db: Session = Depends(obter_sessao),
    usuario_logado: models.Usuario = Depends(exigir_admin),
):
    try:
        return cadastrar_usuario(dados, db)

    except IntegrityError as e:
        db.rollback()
        print(f"Erro de integridade ao cadastrar usuario: {e}")
        raise HTTPException(
            status_code=409,
            detail="Conflito de integridade no banco de dados. Verifique o terminal.",
        ) from None

    except SQLAlchemyError as e:
        db.rollback()
        print(f"Erro de banco de dados: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao cadastrar usuario no banco de dados.",
        ) from None


@router.get("/usuarios", response_model=list[UsuarioResposta])
def obter_usuarios(
    db: Session = Depends(obter_sessao),
    usuario_logado: models.Usuario = Depends(exigir_admin),
):
    return listar_usuarios(db)


@router.get("/usuarios/{id_usuario}", response_model=UsuarioResposta)
def obter_usuario(
    id_usuario: int,
    db: Session = Depends(obter_sessao),
    usuario_logado: Usuario = Depends(exigir_admin),
):
    usuario = buscar_usuario_por_id(id_usuario, db)

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado.",
        )

    return usuario


@router.put("/usuarios/{id_usuario}", response_model=UsuarioResposta)
def editar_usuario(
    id_usuario: int,
    dados: UsuarioAtualizar,
    db: Session = Depends(obter_sessao),
    usuario_logado: models.Usuario = Depends(exigir_admin),
):
    try:
        usuario = atualizar_usuario(id_usuario, dados, db)

        if usuario is None:
            raise HTTPException(
                status_code=404,
                detail="Usuário não encontrado.",
            )

        return usuario

    except IntegrityError as e:
        db.rollback()
        print(f"Erro de integridade ao atualizar usuario: {e}")
        raise HTTPException(
            status_code=409,
            detail="CPF já cadastrado ou conflito de integridade.",
        ) from None

    except SQLAlchemyError as e:
        db.rollback()
        print(f"Erro de banco de dados ao atualizar usuario: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao atualizar usuario no banco de dados.",
        ) from None


@router.patch("/usuarios/{id_usuario}/desativar", response_model=UsuarioResposta)
def rota_desativar_usuario(
    id_usuario: int,
    db: Session = Depends(obter_sessao),
    usuario_logado: models.Usuario = Depends(exigir_admin),
):
    usuario = desativar_usuario(id_usuario, db)

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado.",
        )

    return usuario
