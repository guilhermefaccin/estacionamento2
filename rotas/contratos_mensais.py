
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from banco.sessao import obter_sessao
from schemas.contratos_mensais import (
    ContratoMensalCriar,
    ContratoMensalAtualizar,
    ContratoMensalResposta,
)
from servicos.contratos_mensais import (
    cadastrar_contrato,
    listar_contratos,
    buscar_contrato_por_id,
    atualizar_contrato,
    desativar_contrato,
)

router = APIRouter(
    prefix="/contratos-mensais",
    tags=["Contratos Mensais"],
)


@router.post(
    "/",
    response_model=ContratoMensalResposta,
    status_code=status.HTTP_201_CREATED,
)
def criar(
    dados: ContratoMensalCriar,
    id_usuario: int,
    db: Session = Depends(obter_sessao),
):
    return cadastrar_contrato(db, dados, id_usuario)


@router.get(
    "/",
    response_model=list[ContratoMensalResposta],
)
def listar(db: Session = Depends(obter_sessao)):
    return listar_contratos(db)


@router.get(
    "/{id_contrato}",
    response_model=ContratoMensalResposta,
)
def buscar(
    id_contrato: int,
    db: Session = Depends(obter_sessao),
):
    contrato = buscar_contrato_por_id(db, id_contrato)

    if contrato is None:
        raise HTTPException(
            status_code=404,
            detail="Contrato não encontrado ou encerrado",
        )

    return contrato


@router.put(
    "/{id_contrato}",
    response_model=ContratoMensalResposta,
)
def atualizar(
    id_contrato: int,
    dados: ContratoMensalAtualizar,
    id_usuario: int,
    db: Session = Depends(obter_sessao),
):
    contrato = buscar_contrato_por_id(db, id_contrato)

    if contrato is None:
        raise HTTPException(
            status_code=404,
            detail="Contrato não encontrado ou encerrado",
        )

    return atualizar_contrato(db, contrato, dados, id_usuario)


@router.patch(
    "/{id_contrato}/encerrar",
    response_model=ContratoMensalResposta,
)
def encerrar(
    id_contrato: int,
    id_usuario: int,
    db: Session = Depends(obter_sessao),
):
    contrato = buscar_contrato_por_id(db, id_contrato)

    if contrato is None:
        raise HTTPException(
            status_code=404,
            detail="Contrato não encontrado ou encerrado",
        )

    return desativar_contrato(db, contrato, id_usuario)
