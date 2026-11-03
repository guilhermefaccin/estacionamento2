from pydantic import BaseModel, ConfigDict, Field


class VeiculoCriar(BaseModel):
    id_cliente: int = Field(gt=0)
    id_marca: int = Field(gt=0)
    placa: str = Field(min_length=1, max_length=10)
    modelo: str = Field(min_length=1, max_length=80)
    cor: str | None = Field(default=None, max_length=30)


class VeiculoAtualizar(BaseModel):
    id_cliente: int = Field(gt=0)
    id_marca: int = Field(gt=0)
    placa: str = Field(min_length=1, max_length=10)
    modelo: str = Field(min_length=1, max_length=80)
    cor: str | None = Field(default=None, max_length=30)


class VeiculoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_veiculo: int
    id_cliente: int
    id_marca: int
    placa: str
    modelo: str
    cor: str | None
    ativo: bool
