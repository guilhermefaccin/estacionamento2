
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from banco.sessao import obter_sessao
from schemas.tarifas import (
    TarifaCriar,
    TarifaAtualizar,
    TarifaResposta,
)
from servicos.tarifas import (
    cadastrar_tarifa,
    listar_tarifas,
    buscar_tarifa_por_id,
    atualizar_tarifa,
    desativar_tarifa,
)

router = APIRouter(
    prefix="/tarifas",
    tags=["Tarifas"]
)


@router.post("/", response_model=TarifaResposta, status_code=status.HTTP_201_CREATED)
def criar(dados: TarifaCriar, db: Session = Depends(obter_sessao)):
    return cadastrar_tarifa(db, dados)


@router.get("/", response_model=list[TarifaResposta])
def listar(db: Session = Depends(obter_sessao)):
    return listar_tarifas(db)


@router.get("/{id_tarifa}", response_model=TarifaResposta)
def buscar(id_tarifa: int, db: Session = Depends(obter_sessao)):
    tarifa = buscar_tarifa_por_id(db, id_tarifa)

    if tarifa is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarifa não encontrada ou inativa"
        )

    return tarifa


@router.put("/{id_tarifa}", response_model=TarifaResposta)
def atualizar(
    id_tarifa: int,
    dados: TarifaAtualizar,
    db: Session = Depends(obter_sessao)
):
    tarifa = buscar_tarifa_por_id(db, id_tarifa)

    if tarifa is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarifa não encontrada ou inativa"
        )

    return atualizar_tarifa(db, tarifa, dados)



@router.patch("/{id_tarifa}/desativar", response_model=TarifaResposta)
def desativar(id_tarifa: int, db: Session = Depends(obter_sessao)):
    tarifa = buscar_tarifa_por_id(db, id_tarifa)

    if tarifa is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarifa não encontrada ou inativa"
        )

    tarifa_desativada = desativar_tarifa(db, tarifa)

    if tarifa_desativada is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Não foi possível desativar a tarifa"
        )

    return tarifa_desativada


    db: Session = Depends(obter_sessao)
