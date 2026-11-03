
from sqlmodel import Session, select
from datetime import datetime
from entidades.models import Tarifa
from schemas.tarifas import TarifaCriar, TarifaAtualizar


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
    statement = select(Tarifa).where(Tarifa.ativo == True)
    return list(db.exec(statement).all())


def buscar_tarifa_por_id(db: Session, id_tarifa: int) -> Tarifa | None:
    statement = select(Tarifa).where(
        Tarifa.id_tarifa == id_tarifa,
        Tarifa.ativo == True
    )
    return db.exec(statement).first()


def atualizar_tarifa(
    db: Session,
    tarifa: Tarifa,
    dados: TarifaAtualizar
) -> Tarifa:
    alteracoes = dados.model_dump(exclude_unset=True)

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
