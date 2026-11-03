
from sqlmodel import SQLModel

from entidades.models import StatusVaga, TipoUsoVaga, TipoVaga


class VagaCriar(SQLModel):
    numero_vaga: str
    tipo_vaga: TipoVaga = TipoVaga.CARRO
    tipo_uso: TipoUsoVaga = TipoUsoVaga.ROTATIVA


class VagaAtualizar(SQLModel):
    numero_vaga: str | None = None
    status: StatusVaga | None = None
    tipo_uso: TipoUsoVaga | None = None


class VagaResposta(SQLModel):
    id_vaga: int
    numero_vaga: str
    tipo_vaga: TipoVaga
    status: StatusVaga
    tipo_uso: TipoUsoVaga
    ativo: bool
