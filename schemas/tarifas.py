
from datetime import datetime
from decimal import Decimal

from sqlmodel import SQLModel, Field

from entidades.models import ModalidadeTarifa


class TarifaCriar(SQLModel):
    nome: str = Field(min_length=1, max_length=100)
    modalidade: ModalidadeTarifa
    valor: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    intervalo_minutos: int | None = Field(default=None, gt=0)
    data_inicio_vigencia: datetime | None = None
    data_fim_vigencia: datetime | None = None


class TarifaAtualizar(SQLModel):
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    modalidade: ModalidadeTarifa | None = None
    valor: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    intervalo_minutos: int | None = Field(default=None, gt=0)
    data_inicio_vigencia: datetime | None = None
    data_fim_vigencia: datetime | None = None


class TarifaResposta(SQLModel):
    id_tarifa: int
    nome: str
    modalidade: ModalidadeTarifa
    valor: Decimal
    intervalo_minutos: int | None
    data_inicio_vigencia: datetime
    data_fim_vigencia: datetime | None
    ativo: bool
