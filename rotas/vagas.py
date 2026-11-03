
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import Session

from banco.sessao import obter_sessao
from schemas.vagas import VagaCriar, VagaAtualizar, VagaResposta
from servicos.vagas import (
    cadastrar_vaga,
    listar_vagas,
    buscar_vaga_por_id,
    atualizar_vaga,
    desativar_vaga,
)

router = APIRouter(prefix="/vagas", tags=["Vagas"])


@router.post("/", response_model=VagaResposta, status_code=201)
def criar(dados: VagaCriar, db: Session = Depends(obter_sessao)):
    try:
        return cadastrar_vaga(dados, db)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Já existe uma vaga com esse número."
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao cadastrar vaga.")


@router.get("/", response_model=list[VagaResposta])
def listar(db: Session = Depends(obter_sessao)):
    return listar_vagas(db)


@router.get("/{id_vaga}", response_model=VagaResposta)
def consultar(id_vaga: int, db: Session = Depends(obter_sessao)):
    vaga = buscar_vaga_por_id(id_vaga, db)

    if vaga is None or not vaga.ativo:
        raise HTTPException(status_code=404, detail="Vaga não encontrada.")

    return vaga


@router.put("/{id_vaga}", response_model=VagaResposta)
def editar(
    id_vaga: int,
    dados: VagaAtualizar,
    db: Session = Depends(obter_sessao)
):
    try:
        vaga = atualizar_vaga(id_vaga, dados, db)

        if vaga is None:
            raise HTTPException(status_code=404, detail="Vaga não encontrada.")

        return vaga
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Já existe uma vaga com esse número."
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao editar vaga.")


@router.patch("/{id_vaga}/desativar", response_model=VagaResposta)
def desativar(id_vaga: int, db: Session = Depends(obter_sessao)):
    try:
        vaga = desativar_vaga(id_vaga, db)

        if vaga is None:
            raise HTTPException(status_code=404, detail="Vaga não encontrada.")

        return vaga
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao desativar vaga.")
