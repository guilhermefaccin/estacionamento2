from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from servicos.autenticacao import exigir_admin
from banco.sessao import obter_sessao
from schemas.marcas import MarcaCriar, MarcaAtualizar, MarcaResposta
from servicos.marcas import (
    cadastrar_marca,
    listar_marcas,
    buscar_marca_por_id,
    atualizar_marca,
    desativar_marca,
)

router = APIRouter(prefix="/marcas", tags=["Marcas"])


@router.post("/", response_model=MarcaResposta, status_code=201)
def criar_marca(
    dados: MarcaCriar,
    db: Session = Depends(obter_sessao),
    usuario_logado = Depends(exigir_admin),
):
    try:
        return cadastrar_marca(dados, db)
    except IntegrityError as erro:
        db.rollback()
        print("ERRO DE INTEGRIDADE AO CADASTRAR MARCA:", repr(erro.orig))
        raise HTTPException(
            status_code=409,
            detail="Nome inválido ou referência de usuário inválida.",
        )
    except SQLAlchemyError as erro:
        db.rollback()
        print("ERRO SQL AO CADASTRAR MARCA:", repr(erro))
        raise HTTPException(
            status_code=500,
            detail="Erro ao cadastrar marca. Confira o terminal.",
        )


@router.get("/", response_model=list[MarcaResposta])
def consultar_marcas(db: Session = Depends(obter_sessao)):
    return listar_marcas(db)


@router.get("/{id_marca}", response_model=MarcaResposta)
def consultar_marca(
    id_marca: int,
    db: Session = Depends(obter_sessao),
):
    marca = buscar_marca_por_id(id_marca, db)

    if marca is None or not marca.ativo:
        raise HTTPException(status_code=404, detail="Marca não encontrada.")

    return marca


@router.put("/{id_marca}", response_model=MarcaResposta)
def editar_marca(
    id_marca: int,
    dados: MarcaAtualizar,
    db: Session = Depends(obter_sessao),
    usuario_logado = Depends(exigir_admin),
):
    try:
        marca = atualizar_marca(id_marca, dados, db)

        if marca is None:
            raise HTTPException(status_code=404, detail="Marca não encontrada.")

        return marca
    except HTTPException:
        raise
    except IntegrityError as erro:
        db.rollback()
        print("ERRO DE INTEGRIDADE AO EDITAR MARCA:", repr(erro.orig))
        raise HTTPException(
            status_code=409,
            detail="Nome inválido ou referência de usuário inválida.",
        )
    except SQLAlchemyError as erro:
        db.rollback()
        print("ERRO SQL AO EDITAR MARCA:", repr(erro))
        raise HTTPException(
            status_code=500,
            detail="Erro ao editar marca. Confira o terminal.",
        )


@router.patch("/{id_marca}/desativar", response_model=MarcaResposta)
def desativar_marca_rota(
    id_marca: int,
    db: Session = Depends(obter_sessao),
    usuario_logado = Depends(exigir_admin),
):
    try:
        marca = desativar_marca(id_marca, db)

        if marca is None:
            raise HTTPException(status_code=404, detail="Marca não encontrada.")

        return marca
    except HTTPException:
        raise
    except SQLAlchemyError as erro:
        db.rollback()
        print("ERRO SQL AO DESATIVAR MARCA:", repr(erro))
        raise HTTPException(
            status_code=500,
            detail="Erro ao desativar marca. Confira o terminal.",
        )