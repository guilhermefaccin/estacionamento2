from datetime import datetime

from sqlmodel import SQLModel


class MarcaCriar(SQLModel):
    nome: str


class MarcaAtualizar(SQLModel):
    nome: str


class MarcaResposta(SQLModel):
    id_marca: int
    nome: str
    data_cadastro: datetime
    data_alteracao: datetime
    id_usuario_cadastro: int
    id_usuario_alteracao: int | None
    ativo: bool