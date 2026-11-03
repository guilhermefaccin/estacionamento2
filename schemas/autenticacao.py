from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class LoginResposta(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AlterarSenhaRequest(BaseModel):
    senha_atual: str
    nova_senha: str = Field(min_length=8)
    confirmar_nova_senha: str
