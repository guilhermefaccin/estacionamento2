from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from banco.sessao import obter_sessao
from schemas.estacionamentos import (
    EstacionamentoEntrada,
    EstacionamentoResposta,
)
from servicos.autenticacao import obter_usuario_logado
from servicos.estacionamentos import (
    buscar_por_id,
    listar_abertos,
    registrar_entrada,
    registrar_saida,
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
    usuario_logado=Depends(obter_usuario_logado),
    db: Session = Depends(obter_sessao),
):
    return registrar_entrada(db, dados, usuario_logado.id_usuario)


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
    usuario_logado=Depends(obter_usuario_logado),
    db: Session = Depends(obter_sessao),
):
    return registrar_saida(
        db,
        id_estacionamento,
        usuario_logado.id_usuario,
    )
