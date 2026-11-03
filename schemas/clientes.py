
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClienteCriar(BaseModel):
    nome: str = Field(min_length=1, max_length=150)
    cpf_cnpj: str | None = Field(default=None, max_length=18)
    telefone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = Field(default=None, max_length=150)


class ClienteAtualizar(BaseModel):
    nome: str = Field(min_length=1, max_length=150)
    cpf_cnpj: str | None = Field(default=None, max_length=18)
    telefone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = Field(default=None, max_length=150)


class ClienteResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_cliente: int
    nome: str
    cpf_cnpj: str | None
    telefone: str | None
    email: str | None
    ativo: bool
