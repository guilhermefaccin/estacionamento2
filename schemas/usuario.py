
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class UsuarioCriar(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    cpf: str = Field(pattern=r"^\d{11}$")
    email: EmailStr = Field(max_length=80)
    senha: str = Field(min_length=8, max_length=128)


class UsuarioResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_usuario: int
    nome: str
    cpf: str
    email: EmailStr
    perfil: str
    ativo: bool


class UsuarioAtualizar(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    cpf: str = Field(pattern=r"^\d{11}$")
    email: EmailStr = Field(max_length=80)
