from datetime import datetime

from sqlmodel import Field, SQLModel


class MarcaCriar(SQLModel):
    nome: str = Field(min_length=1, max_length=100)


class MarcaAtualizar(SQLModel):
    nome: str = Field(min_length=1, max_length=100)


class MarcaResposta(SQLModel):
    id_marca: int
    nome: str
    data_cadastro: datetime
    data_alteracao: datetime
    id_usuario_cadastro: int
    id_usuario_alteracao: int | None
    ativo: bool
