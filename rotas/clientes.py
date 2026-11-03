
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from banco.sessao import obter_sessao
from schemas.clientes import (
    ClienteCriar,
    ClienteAtualizar,
    ClienteResposta,
)
from servicos.clientes import (
    cadastrar_cliente,
    listar_clientes,
    buscar_cliente_por_id,
    atualizar_cliente,
    desativar_cliente,
)


router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post("", response_model=ClienteResposta, status_code=201)
def criar_cliente(
    dados: ClienteCriar,
    db: Session = Depends(obter_sessao),
):
    try:
        return cadastrar_cliente(dados, db)
    except IntegrityError as erro:
        db.rollback()
        print("ERRO DE INTEGRIDADE NO CADASTRO:", repr(erro.orig))
        raise HTTPException(
        status_code=409,
        detail="Conflito de integridade no banco. Confira o terminal."
    )
    except SQLAlchemyError as erro:
        db.rollback()
        print("ERRO SQL NO CADASTRO DE CLIENTE:", repr(erro))
        raise HTTPException(
        status_code=500,
        detail="Erro ao cadastrar cliente. Confira o terminal."
    )


@router.get("", response_model=list[ClienteResposta])
def obter_clientes(db: Session = Depends(obter_sessao)):
    return listar_clientes(db)


@router.get("/{id_cliente}", response_model=ClienteResposta)
def obter_cliente(
    id_cliente: int,
    db: Session = Depends(obter_sessao),
):
    cliente = buscar_cliente_por_id(id_cliente, db)

    if cliente is None or not cliente.ativo:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    return cliente


@router.put("/{id_cliente}", response_model=ClienteResposta)
def editar_cliente(
    id_cliente: int,
    dados: ClienteAtualizar,
    db: Session = Depends(obter_sessao),
):
    try:
        cliente = atualizar_cliente(id_cliente, dados, db)

        if cliente is None:
            raise HTTPException(status_code=404, detail="Cliente não encontrado.")

        return cliente
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="CPF/CNPJ já cadastrado ou conflito de integridade.",
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erro ao atualizar cliente no banco de dados.",
        )


@router.patch("/{id_cliente}/desativar", response_model=ClienteResposta)
def rota_desativar_cliente(
    id_cliente: int,
    db: Session = Depends(obter_sessao),
):
    try:
        cliente = desativar_cliente(id_cliente, db)

        if cliente is None:
            raise HTTPException(status_code=404, detail="Cliente não encontrado.")

        return cliente
    except IntegrityError as erro:
        db.rollback()
    print("ERRO DE INTEGRIDADE NO CADASTRO:", repr(erro.orig))
    raise HTTPException(
        status_code=409,
        detail="Conflito de integridade no banco. Confira o terminal."
    )