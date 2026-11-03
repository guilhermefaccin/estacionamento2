from fastapi import HTTPException
from sqlmodel import Session, select

from entidades.models import Vaga
from schemas.vagas import VagaAtualizar, VagaCriar


def cadastrar_vaga(dados: VagaCriar, db: Session) -> Vaga:
    vaga = Vaga(
        numero_vaga=dados.numero_vaga,
        tipo_vaga=dados.tipo_vaga,
        tipo_uso=dados.tipo_uso,
        status="livre",
        ativo=True,
    )

    db.add(vaga)
    db.commit()
    db.refresh(vaga)
    return vaga


def listar_vagas(db: Session) -> list[Vaga]:
    comando = select(Vaga).where(Vaga.ativo.is_(True))
    return list(db.exec(comando).all())


def buscar_vaga_por_id(id_vaga: int, db: Session) -> Vaga | None:
    comando = select(Vaga).where(Vaga.id_vaga == id_vaga)
    return db.exec(comando).first()


def atualizar_vaga(id_vaga: int, dados: VagaAtualizar, db: Session) -> Vaga | None:
    vaga = buscar_vaga_por_id(id_vaga, db)

    if vaga is None or not vaga.ativo:
        return None

    alteracoes = dados.model_dump(exclude_unset=True)
    if vaga.status == "ocupada" and any(
        campo in alteracoes and alteracoes[campo] != getattr(vaga, campo)
        for campo in ("status", "tipo_uso")
    ):
        raise HTTPException(
            status_code=409,
            detail="Finalize o uso da vaga antes de alterar seu status ou tipo",
        )
    if vaga.status != "ocupada" and alteracoes.get("status") == "ocupada":
        raise HTTPException(
            status_code=409,
            detail="Registre uma entrada ou contrato para ocupar a vaga",
        )

    for campo, valor in alteracoes.items():
        if valor is not None:
            setattr(vaga, campo, valor)

    db.add(vaga)
    db.commit()
    db.refresh(vaga)
    return vaga


def desativar_vaga(id_vaga: int, db: Session) -> Vaga | None:
    vaga = buscar_vaga_por_id(id_vaga, db)

    if vaga is None or not vaga.ativo:
        return None

    if vaga.status == "ocupada":
        raise HTTPException(
            status_code=409, detail="Uma vaga ocupada não pode ser desativada"
        )

    vaga.ativo = False

    db.add(vaga)
    db.commit()
    db.refresh(vaga)
    return vaga
