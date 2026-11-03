
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from banco.sessao import obter_sessao
from schemas.estacionamentos import (
    EstacionamentoEntrada,
    EstacionamentoResposta,
)
from servicos.estacionamentos import (
    registrar_entrada,
    listar_abertos,
    buscar_por_id,
    registrar_saida
)

router = APIRouter(
    prefix="/estacionamentos",
    tags=["Estacionamentos"],
)


@router.post(
    "/entrada",
    response_model=EstacionamentoResposta,
    status_code=status.HTTP_201_CREATED,
)
def entrada(
    dados: EstacionamentoEntrada,
    id_usuario: int,
    db: Session = Depends(obter_sessao),
):
    return registrar_entrada(db, dados, id_usuario)


@router.get(
    "/abertos",
    response_model=list[EstacionamentoResposta],
)
def listar(db: Session = Depends(obter_sessao)):
    return listar_abertos(db)


@router.get(
    "/{id_estacionamento}",
    response_model=EstacionamentoResposta,
)
def buscar(
    id_estacionamento: int,
    db: Session = Depends(obter_sessao),
):
    estacionamento = buscar_por_id(db, id_estacionamento)

    if estacionamento is None:
        raise HTTPException(
            status_code=404,
            detail="Estacionamento não encontrado",
        )

    return estacionamento


@router.patch("/{id_estacionamento}/saida", response_model=EstacionamentoResposta)
def saida(
    id_estacionamento: int,
    id_usuario: int,
    db: Session = Depends(obter_sessao),
):
    return registrar_saida(
        db,
        id_estacionamento,
        id_usuario,
    )
