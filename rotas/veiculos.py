from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import Session

from banco.sessao import obter_sessao
from schemas.veiculos import (
    VeiculoAtualizar,
    VeiculoCriar,
    VeiculoResposta,
)
from servicos.autenticacao import obter_usuario_logado
from servicos.veiculos import (
    atualizar_veiculo,
    buscar_veiculo_por_id,
    cadastrar_veiculo,
    desativar_veiculo,
    listar_veiculos,
)

router = APIRouter(prefix="/veiculos", tags=["Veículos"])


@router.post("/", response_model=VeiculoResposta, status_code=201)
def criar_veiculo(
    dados: VeiculoCriar,
    db: Session = Depends(obter_sessao),
    usuario_logado=Depends(obter_usuario_logado),
):
    try:
        return cadastrar_veiculo(dados, db, usuario_logado.id_usuario)
    except IntegrityError as erro:
        db.rollback()
        print("ERRO DE INTEGRIDADE NO CADASTRO DE VEÍCULO:", repr(erro.orig))
        raise HTTPException(
            status_code=409,
            detail="Placa duplicada ou referência inválida para cliente, marca ou usuário.",
        ) from None
    except SQLAlchemyError as erro:
        db.rollback()
        print("ERRO SQL NO CADASTRO DE VEÍCULO:", repr(erro))
        raise HTTPException(
            status_code=500,
            detail="Erro ao cadastrar veículo. Confira o terminal.",
        ) from None


@router.get("/", response_model=list[VeiculoResposta])
def consultar_veiculos(
    db: Session = Depends(obter_sessao),
    usuario_logado=Depends(obter_usuario_logado),
):
    return listar_veiculos(db)


@router.get("/{id_veiculo}", response_model=VeiculoResposta)
def consultar_veiculo(
    id_veiculo: int,
    db: Session = Depends(obter_sessao),
    usuario_logado=Depends(obter_usuario_logado),
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
    usuario_logado=Depends(obter_usuario_logado),
):
    try:
        veiculo = atualizar_veiculo(id_veiculo, dados, db, usuario_logado.id_usuario)

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
        ) from None
    except SQLAlchemyError as erro:
        db.rollback()
        print("ERRO SQL NA EDIÇÃO DE VEÍCULO:", repr(erro))
        raise HTTPException(
            status_code=500,
            detail="Erro ao editar veículo. Confira o terminal.",
        ) from None


@router.patch("/{id_veiculo}/desativar", response_model=VeiculoResposta)
def desativar_veiculo_rota(
    id_veiculo: int,
    db: Session = Depends(obter_sessao),
    usuario_logado=Depends(obter_usuario_logado),
):
    try:
        veiculo = desativar_veiculo(id_veiculo, db, usuario_logado.id_usuario)

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
        ) from None
