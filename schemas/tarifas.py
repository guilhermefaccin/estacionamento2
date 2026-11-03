from datetime import datetime
from decimal import Decimal

from pydantic import NaiveDatetime, model_validator
from sqlmodel import Field, SQLModel

from entidades.models import ModalidadeTarifa


class TarifaCriar(SQLModel):
    nome: str = Field(min_length=1, max_length=100)
    modalidade: ModalidadeTarifa
    valor: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    intervalo_minutos: int | None = Field(default=None, gt=0)
    data_inicio_vigencia: NaiveDatetime | None = None
    data_fim_vigencia: NaiveDatetime | None = None

    @model_validator(mode="after")
    def validar_tarifa(self):
        if self.modalidade == ModalidadeTarifa.HORISTA and not self.intervalo_minutos:
            raise ValueError("Tarifa horista exige intervalo_minutos maior que zero")
        inicio = self.data_inicio_vigencia or datetime.now()
        if self.data_fim_vigencia is not None and self.data_fim_vigencia < inicio:
            raise ValueError("O fim da vigência deve ser igual ou posterior ao início")
        return self


class TarifaAtualizar(SQLModel):
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    modalidade: ModalidadeTarifa | None = None
    valor: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    intervalo_minutos: int | None = Field(default=None, gt=0)
    data_inicio_vigencia: NaiveDatetime | None = None
    data_fim_vigencia: NaiveDatetime | None = None


class TarifaResposta(SQLModel):
    id_tarifa: int
    nome: str
    modalidade: ModalidadeTarifa
    valor: Decimal
    intervalo_minutos: int | None
    data_inicio_vigencia: datetime
    data_fim_vigencia: datetime | None
    ativo: bool
