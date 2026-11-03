
from sqlmodel import Session, select

from entidades.models import (
    ContratoMensal,
    StatusContrato,
    Vaga,
    StatusVaga,
)
from schemas.contratos_mensais import (
    ContratoMensalCriar,
    ContratoMensalAtualizar,
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
