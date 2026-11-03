from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from banco.sessao import obter_sessao
from schemas.veiculos import (
    VeiculoCriar,
    VeiculoAtualizar,
    VeiculoResposta,
)
from servicos.veiculos import (
    cadastrar_veiculo,
    listar_veiculos,
    buscar_veiculo_por_id,
    atualizar_veiculo,
    desativar_veiculo,
)

router = APIRouter(prefix="/veiculos", tags=["Veículos"])


@router.post("/", response_model=VeiculoResposta, status_code=201)
def criar_veiculo(
    dados: VeiculoCriar,
    db: Session = Depends(obter_sessao),
):
    try:
        return cadastrar_veiculo(dados, db)
    except IntegrityError as erro:
        db.rollback()
        print("ERRO DE INTEGRIDADE NO CADASTRO DE VEÍCULO:", repr(erro.orig))
        raise HTTPException(
            status_code=409,
            detail="Placa duplicada ou referência inválida para cliente, marca ou usuário.",
        )
    except SQLAlchemyError as erro:
        db.rollback()
        print("ERRO SQL NO CADASTRO DE VEÍCULO:", repr(erro))
        raise HTTPException(
            status_code=500,
            detail="Erro ao cadastrar veículo. Confira o terminal.",
        )


@router.get("/", response_model=list[VeiculoResposta])
def consultar_veiculos(
    db: Session = Depends(obter_sessao),
):
    return listar_veiculos(db)


@router.get("/{id_veiculo}", response_model=VeiculoResposta)
def consultar_veiculo(
    id_veiculo: int,
    db: Session = Depends(obter_sessao),
):
    veiculo = buscar_veiculo_por_id(id_veiculo, db)

    if not veiculo:
        raise HTTPException(
            status_code=404,
            detail="Veículo não encontrado.",
        )

    return veiculo


@router.put("/{id_veiculo}", response_model=VeiculoResposta)
def editar_veiculo(
    id_veiculo: int,
    dados: VeiculoAtualizar,
    db: Session = Depends(obter_sessao),
):
    try:
        veiculo = atualizar_veiculo(id_veiculo, dados, db)

        if not veiculo:
            raise HTTPException(
                status_code=404,
                detail="Veículo não encontrado.",
            )

        return veiculo

    except HTTPException:
        raise
    except IntegrityError as erro:
        db.rollback()
        print("ERRO DE INTEGRIDADE NA EDIÇÃO DE VEÍCULO:", repr(erro.orig))
        raise HTTPException(
            status_code=409,
            detail="Placa duplicada ou referência inválida para cliente, marca ou usuário.",
        )
    except SQLAlchemyError as erro:
        db.rollback()
        print("ERRO SQL NA EDIÇÃO DE VEÍCULO:", repr(erro))
        raise HTTPException(
            status_code=500,
            detail="Erro ao editar veículo. Confira o terminal.",
        )


@router.patch("/{id_veiculo}/desativar", response_model=VeiculoResposta)
def desativar_veiculo_rota(
    id_veiculo: int,
    db: Session = Depends(obter_sessao),
):
    try:
        veiculo = desativar_veiculo(id_veiculo, db)

        if not veiculo:
            raise HTTPException(
                status_code=404,
                detail="Veículo não encontrado.",
            )

        return veiculo

    except HTTPException:
        raise
    except SQLAlchemyError as erro:
        db.rollback()
        print("ERRO SQL AO DESATIVAR VEÍCULO:", repr(erro))
        raise HTTPException(
            status_code=500,
            detail="Erro ao desativar veículo. Confira o terminal.",
        )