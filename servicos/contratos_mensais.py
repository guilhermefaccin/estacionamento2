from fastapi import HTTPException
from pydantic import ValidationError
from sqlmodel import Session, select

from entidades.models import (
    Cliente,
    ContratoMensal,
    ModalidadeTarifa,
    StatusContrato,
    StatusVaga,
    Tarifa,
    Vaga,
)
from schemas.contratos_mensais import (
    ContratoMensalAtualizar,
    ContratoMensalCriar,
)


def validar_contrato(db: Session, contrato: ContratoMensal):
    cliente = db.get(Cliente, contrato.id_cliente)
    tarifa = db.get(Tarifa, contrato.id_tarifa)
    if cliente is None or not cliente.ativo:
        raise HTTPException(status_code=404, detail="Cliente não encontrado ou inativo")
    if (
        tarifa is None
        or not tarifa.ativo
        or tarifa.modalidade != ModalidadeTarifa.MENSALISTA
    ):
        raise HTTPException(
            status_code=400, detail="O contrato exige tarifa mensalista ativa"
        )
    if contrato.data_fim and contrato.data_fim < contrato.data_inicio:
        raise HTTPException(
            status_code=422,
            detail="O fim do contrato deve ser igual ou posterior ao início",
        )
    if contrato.id_vaga is None:
        return
    vaga = db.exec(
        select(Vaga).where(Vaga.id_vaga == contrato.id_vaga).with_for_update()
    ).first()
    if vaga is None or not vaga.ativo or vaga.tipo_uso != "mensalista":
        raise HTTPException(
            status_code=400, detail="Selecione uma vaga mensalista ativa"
        )
    if contrato.status != StatusContrato.ATIVO:
        return
    outro = db.exec(
        select(ContratoMensal).where(
            ContratoMensal.id_vaga == contrato.id_vaga,
            ContratoMensal.status == StatusContrato.ATIVO,
            ContratoMensal.id_contrato != (contrato.id_contrato or 0),
        )
    ).first()
    if outro or vaga.status == StatusVaga.BLOQUEADA:
        raise HTTPException(
            status_code=409,
            detail="A vaga está bloqueada ou vinculada a outro contrato ativo",
        )


def sincronizar_status_vaga(db: Session, id_vaga: int | None) -> None:
    if id_vaga is None:
        return

    vaga = db.get(Vaga, id_vaga)

    if vaga is None or not vaga.ativo:
        return

    contrato_ativo = db.exec(
        select(ContratoMensal).where(
            ContratoMensal.id_vaga == id_vaga,
            ContratoMensal.status == StatusContrato.ATIVO,
        )
    ).first()

    if contrato_ativo:
        vaga.status = StatusVaga.OCUPADA
    elif vaga.status != StatusVaga.BLOQUEADA:
        vaga.status = StatusVaga.LIVRE

    db.add(vaga)


def cadastrar_contrato(
    db: Session,
    dados: ContratoMensalCriar,
    id_usuario: int,
) -> ContratoMensal:
    valores = dados.model_dump(exclude_unset=True)

    contrato = ContratoMensal(**valores)
    contrato.id_usuario_cadastro = id_usuario
    contrato.id_usuario_alteracao = id_usuario

    validar_contrato(db, contrato)

    db.add(contrato)
    db.flush()

    if contrato.status == StatusContrato.ATIVO:
        sincronizar_status_vaga(db, contrato.id_vaga)

    db.commit()
    db.refresh(contrato)

    return contrato


def listar_contratos(db: Session) -> list[ContratoMensal]:
    statement = select(ContratoMensal).where(
        ContratoMensal.status != StatusContrato.ENCERRADO
    )

    return list(db.exec(statement).all())


def buscar_contrato_por_id(
    db: Session,
    id_contrato: int,
) -> ContratoMensal | None:
    statement = select(ContratoMensal).where(
        ContratoMensal.id_contrato == id_contrato,
        ContratoMensal.status != StatusContrato.ENCERRADO,
    )

    return db.exec(statement).first()


def atualizar_contrato(
    db: Session,
    contrato: ContratoMensal,
    dados: ContratoMensalAtualizar,
    id_usuario: int,
) -> ContratoMensal:
    vaga_anterior = contrato.id_vaga
    alteracoes = dados.model_dump(exclude_unset=True)

    valores = {**contrato.model_dump(), **alteracoes}
    try:
        ContratoMensalCriar.model_validate(valores)
    except ValidationError as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro
    candidato = ContratoMensal(**valores)
    validar_contrato(db, candidato)

    for campo, valor in alteracoes.items():
        setattr(contrato, campo, valor)

    contrato.id_usuario_alteracao = id_usuario

    db.add(contrato)
    db.flush()

    sincronizar_status_vaga(db, vaga_anterior)
    sincronizar_status_vaga(db, contrato.id_vaga)

    db.commit()
    db.refresh(contrato)

    return contrato


def desativar_contrato(
    db: Session,
    contrato: ContratoMensal,
    id_usuario: int,
) -> ContratoMensal:
    id_vaga = contrato.id_vaga

    contrato.status = StatusContrato.ENCERRADO
    contrato.id_usuario_alteracao = id_usuario

    db.add(contrato)
    db.flush()

    sincronizar_status_vaga(db, id_vaga)

    db.commit()
    db.refresh(contrato)

    return contrato
