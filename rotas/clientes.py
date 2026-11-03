from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import Session

from banco.sessao import obter_sessao
from schemas.clientes import (
    ClienteAtualizar,
    ClienteCriar,
    ClienteResposta,
)
from servicos.autenticacao import obter_usuario_logado
from servicos.clientes import (
    atualizar_cliente,
    buscar_cliente_por_id,
    cadastrar_cliente,
    desativar_cliente,
    listar_clientes,
)

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post("", response_model=ClienteResposta, status_code=201)
def criar_cliente(
    dados: ClienteCriar,
    db: Session = Depends(obter_sessao),
    usuario_logado=Depends(obter_usuario_logado),
):
    try:
        return cadastrar_cliente(dados, db, usuario_logado.id_usuario)
    except IntegrityError as erro:
        db.rollback()
        print("ERRO DE INTEGRIDADE NO CADASTRO:", repr(erro.orig))
        raise HTTPException(
            status_code=409,
            detail="Conflito de integridade no banco. Confira o terminal.",
        ) from None
    except SQLAlchemyError as erro:
        db.rollback()
        print("ERRO SQL NO CADASTRO DE CLIENTE:", repr(erro))
        raise HTTPException(
            status_code=500, detail="Erro ao cadastrar cliente. Confira o terminal."
        ) from None


@router.get("", response_model=list[ClienteResposta])
def obter_clientes(db: Session = Depends(obter_sessao)):
    return listar_clientes(db)


@router.get("/{id_cliente}", response_model=ClienteResposta)
def obter_cliente(
    id_cliente: int,
    db: Session = Depends(obter_sessao),
    usuario_logado=Depends(obter_usuario_logado),
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
    usuario_logado=Depends(obter_usuario_logado),
):
    try:
        cliente = atualizar_cliente(id_cliente, dados, db, usuario_logado.id_usuario)

        if cliente is None:
            raise HTTPException(status_code=404, detail="Cliente não encontrado.")

        return cliente
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="CPF/CNPJ já cadastrado ou conflito de integridade.",
        ) from None
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erro ao atualizar cliente no banco de dados.",
        ) from None


@router.patch("/{id_cliente}/desativar", response_model=ClienteResposta)
def rota_desativar_cliente(
    id_cliente: int,
    db: Session = Depends(obter_sessao),
    usuario_logado=Depends(obter_usuario_logado),
):
    try:
        cliente = desativar_cliente(id_cliente, db, usuario_logado.id_usuario)

        if cliente is None:
            raise HTTPException(status_code=404, detail="Cliente não encontrado.")

        return cliente
    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="O cliente possui registros associados e n?o pode ser desativado.",
        ) from erro
