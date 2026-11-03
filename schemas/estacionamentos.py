
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field
from entidades.models import StatusEstacionamento


class EstacionamentoEntrada(SQLModel):
    id_veiculo: int = Field(gt=0)
    id_vaga: int = Field(gt=0)
    id_tarifa: int | None = Field(default=None, gt=0)
    id_contrato: int | None = Field(default=None, gt=0)


class EstacionamentoResposta(SQLModel):
    id_estacionamento: int
    id_veiculo: int
    id_vaga: int
    id_contrato: int | None
    id_tarifa: int | None
    id_usuario_entrada: int
    id_usuario_saida: int | None
    data_hora_entrada: datetime
    data_hora_saida: datetime | None
    valor_calculado: Decimal | None
    status: StatusEstacionamento
