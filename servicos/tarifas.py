from datetime import datetime

from fastapi import HTTPException
from pydantic import ValidationError
from sqlmodel import Session, select

from entidades.models import Tarifa
from schemas.tarifas import TarifaAtualizar, TarifaCriar


def cadastrar_tarifa(db: Session, dados: TarifaCriar) -> Tarifa:
    valores = dados.model_dump(exclude_unset=True, exclude_none=True)

    if not valores.get("data_inicio_vigencia"):
        valores["data_inicio_vigencia"] = datetime.now()

    tarifa = Tarifa(**valores)

    db.add(tarifa)
    db.commit()
    db.refresh(tarifa)

    return tarifa


def listar_tarifas(db: Session) -> list[Tarifa]:
    statement = select(Tarifa).where(Tarifa.ativo.is_(True))
    return list(db.exec(statement).all())


def buscar_tarifa_por_id(db: Session, id_tarifa: int) -> Tarifa | None:
    statement = select(Tarifa).where(
        Tarifa.id_tarifa == id_tarifa, Tarifa.ativo.is_(True)
    )
    return db.exec(statement).first()


def atualizar_tarifa(db: Session, tarifa: Tarifa, dados: TarifaAtualizar) -> Tarifa:
    alteracoes = dados.model_dump(exclude_unset=True)

    valores = {**tarifa.model_dump(), **alteracoes}
    try:
        TarifaCriar.model_validate(valores)
    except ValidationError as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro
    for campo in ("nome", "modalidade", "valor", "data_inicio_vigencia"):
        if valores[campo] is None:
            raise HTTPException(
                status_code=422, detail=f"O campo {campo} não pode ser nulo"
            )

    for campo, valor in alteracoes.items():
        setattr(tarifa, campo, valor)

    db.add(tarifa)
    db.commit()
    db.refresh(tarifa)

    return tarifa


def desativar_tarifa(db: Session, tarifa: Tarifa) -> Tarifa:
    tarifa.ativo = False

    db.add(tarifa)
    db.commit()
    db.refresh(tarifa)

    return tarifa
