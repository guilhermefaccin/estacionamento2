
from datetime import date
from decimal import Decimal

from sqlmodel import SQLModel, Field

from entidades.models import StatusContrato


class ContratoMensalCriar(SQLModel):
    id_cliente: int = Field(gt=0)
    id_vaga: int | None = Field(default=None, gt=0)
    id_tarifa: int = Field(gt=0)

    data_inicio: date
    data_fim: date | None = None

    dia_vencimento: int = Field(ge=1, le=31)
    valor_mensal: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2
    )

    status: StatusContrato = StatusContrato.ATIVO


class ContratoMensalAtualizar(SQLModel):
    id_cliente: int | None = Field(default=None, gt=0)
    id_vaga: int | None = Field(default=None, gt=0)
    id_tarifa: int | None = Field(default=None, gt=0)

    data_inicio: date | None = None
    data_fim: date | None = None

    dia_vencimento: int | None = Field(default=None, ge=1, le=31)
    valor_mensal: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=10,
        decimal_places=2
    )

    status: StatusContrato | None = None


class ContratoMensalResposta(SQLModel):
    id_contrato: int
    id_cliente: int
    id_vaga: int | None
    id_tarifa: int

    data_inicio: date
    data_fim: date | None

    dia_vencimento: int
    valor_mensal: Decimal
    status: StatusContrato
