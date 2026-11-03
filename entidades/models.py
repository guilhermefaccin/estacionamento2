from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from sqlalchemy import Column, Enum as SAEnum
from sqlalchemy import DateTime, text, func
from sqlmodel import SQLModel, Field
from sqlalchemy import DateTime
from math import ceil


class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios_estacionamento"

    id_usuario: int | None = Field(
        default=None,
        primary_key=True
    )

    nome: str = Field(
        max_length=100,
        nullable=False
    )

    cpf: str = Field(
        max_length=11,
        unique=True,
        nullable=False
    )

    email: str = Field(
        max_length=80,
        nullable=False
    )

    senha: str = Field(
        max_length=255,
        nullable=False
    )

    perfil: str = Field(
        default="USUARIO",
        max_length=10,
        nullable=False
    )

    ativo: bool = Field(
        default=True,
        nullable=False
    )


class Cliente(SQLModel, table=True):
    __tablename__ = "clientes"

    id_cliente: int | None = Field(
        default=None,
        primary_key=True
    )
    nome: str = Field(max_length=150, nullable=False)
    cpf_cnpj: str | None = Field(
        default=None,
        max_length=18,
        unique=True
    )
    telefone: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=150)

    data_cadastro: datetime = Field(
    default_factory=lambda: datetime.now(timezone.utc),
    nullable=False
    )

    data_alteracao: datetime = Field(
    default_factory=lambda: datetime.now(timezone.utc),
    nullable=False
    )

    id_usuario_cadastro: int = Field(nullable=False)
    id_usuario_alteracao: int | None = Field(default=None)

    ativo: bool = Field(default=True, nullable=False)


class Endereco(SQLModel, table=True):
    __tablename__ = "enderecos"

    id_endereco: int | None = Field(
        default=None,
        primary_key=True
    )

    id_cliente: int = Field(nullable=False)

    rua: str = Field(max_length=150, nullable=False)
    numero: str = Field(max_length=20, nullable=False)
    complemento: str | None = Field(default=None, max_length=100)
    bairro: str = Field(max_length=100, nullable=False)
    cidade: str = Field(max_length=100, nullable=False)
    estado: str = Field(max_length=2, nullable=False)
    pais: str = Field(default="Brasil", max_length=60, nullable=False)
    cep: str = Field(max_length=9, nullable=False)

    data_cadastro: datetime | None = Field(default=None)
    data_alteracao: datetime | None = Field(default=None)

    id_usuario_cadastro: int = Field(nullable=False)
    id_usuario_alteracao: int | None = Field(default=None)


class Marca(SQLModel, table=True):
    __tablename__ = "marcas"

    id_marca: int | None = Field(
        default=None,
        primary_key=True
    )

    nome: str = Field(max_length=100, nullable=False)

    data_cadastro: datetime = Field(
        nullable=False,
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")}
    )

    data_alteracao: datetime = Field(
        nullable=False,
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
            "onupdate": func.now()
        }
    )

    id_usuario_cadastro: int = Field(nullable=False)
    id_usuario_alteracao: int | None = Field(default=None)

    ativo: bool = Field(default=True, nullable=False)


class NomeMarca(str, Enum):
    CHEVROLET = "Chevrolet"
    FIAT = "Fiat"
    VOLKSWAGEN = "Volkswagen"
    FORD = "Ford"
    TOYOTA = "Toyota"
    HONDA = "Honda"
    HYUNDAI = "Hyundai"
    JEEP = "Jeep"
    RENAULT = "Renault"
    PEUGEOT = "Peugeot"
    CITROEN = "Citroën"
    NISSAN = "Nissan"
    BMW = "BMW"
    AUDI = "Audi"
    MERCEDES_BENZ = "Mercedes-Benz"
    PORSCHE = "Porsche"
    MITSUBISHI = "Mitsubishi"
    CAOA_CHERY = "Caoa Chery"
    BYD = "BYD"
    GWM = "GWM"


class Veiculo(SQLModel, table=True):
    __tablename__ = "veiculos"

    id_veiculo: int | None = Field(
        default=None,
        primary_key=True
    )

    id_cliente: int = Field(nullable=False)
    id_marca: int = Field(nullable=False)

    placa: str = Field(
        max_length=10,
        nullable=False,
        unique=True
    )

    modelo: str = Field(max_length=80, nullable=False)
    cor: str | None = Field(default=None, max_length=30)

    data_cadastro: datetime = Field(
        default=None,
        nullable=False,
        sa_type=DateTime,
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")}
    )

    data_alteracao: datetime = Field(
        default=None,
        nullable=False,
        sa_type=DateTime,
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
            "onupdate": func.now()
        }
    )

    id_usuario_cadastro: int = Field(nullable=False)
    id_usuario_alteracao: int | None = Field(default=None)

    ativo: bool = Field(default=True, nullable=False)


class TipoVaga(str, Enum):
    CARRO = "carro"


class StatusVaga(str, Enum):
    LIVRE = "livre"
    OCUPADA = "ocupada"
    BLOQUEADA = "bloqueada"


class TipoUsoVaga(str, Enum):
    ROTATIVA = "rotativa"
    MENSALISTA = "mensalista"



class Vaga(SQLModel, table=True):
    __tablename__ = "vagas"

    id_vaga: int | None = Field(
        default=None,
        primary_key=True
    )

    numero_vaga: str = Field(
        max_length=10,
        nullable=False,
        unique=True
    )

    tipo_vaga: TipoVaga = Field(
        default=TipoVaga.CARRO,
        sa_column=Column(
            SAEnum(
                TipoVaga,
                name="tipovaga",
                values_callable=lambda enum_cls: [
                    item.value for item in enum_cls
                ],
                native_enum=True
            ),
            nullable=False,
            default=TipoVaga.CARRO
        )
    )

    status: StatusVaga = Field(
        default=StatusVaga.LIVRE,
        sa_column=Column(
            SAEnum(
                StatusVaga,
                name="statusvaga",
                values_callable=lambda enum_cls: [
                    item.value for item in enum_cls
                ],
                native_enum=True
            ),
            nullable=False,
            default=StatusVaga.LIVRE
        )
    )

    tipo_uso: TipoUsoVaga = Field(
        default=TipoUsoVaga.ROTATIVA,
        sa_column=Column(
            SAEnum(
                TipoUsoVaga,
                name="tipousovaga",
                values_callable=lambda enum_cls: [
                    item.value for item in enum_cls
                ],
                native_enum=True
            ),
            nullable=False,
            default=TipoUsoVaga.ROTATIVA
        )
    )

    ativo: bool = Field(default=True, nullable=False)


class ModalidadeTarifa(str, Enum):
    HORISTA = "horista"
    MENSALISTA = "mensalista"


class Tarifa(SQLModel, table=True):
    __tablename__ = "tarifas"

    id_tarifa: int | None = Field(
        default=None,
        primary_key=True
    )

    nome: str = Field(max_length=100, nullable=False)

    modalidade: ModalidadeTarifa = Field(
    sa_column=Column(
        SAEnum(
            ModalidadeTarifa,
            values_callable=lambda enum_cls: [
                item.value for item in enum_cls
            ],
        ),
        nullable=False,
    )
)

    valor: Decimal = Field(
        max_digits=10,
        decimal_places=2,
        nullable=False
    )

    intervalo_minutos: int | None = Field(default=None)

    data_inicio_vigencia: datetime = Field(
        nullable=False,
        sa_type=DateTime,
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP")
        }
    )

    data_fim_vigencia: datetime | None = Field(
        default=None,
        nullable=True
    )

    ativo: bool = Field(default=True, nullable=False)


class StatusContrato(str, Enum):
    ATIVO = "ativo"
    SUSPENSO = "suspenso"
    ENCERRADO = "encerrado"


class ContratoMensal(SQLModel, table=True):
    __tablename__ = "contratos_mensais"

    id_contrato: int | None = Field(
        default=None,
        primary_key=True
    )

    id_cliente: int = Field(
        foreign_key="clientes.id_cliente",
        nullable=False
    )

    id_vaga: int | None = Field(
        default=None,
        foreign_key="vagas.id_vaga"
    )

    id_tarifa: int = Field(
        foreign_key="tarifas.id_tarifa",
        nullable=False
    )

    data_inicio: date = Field(nullable=False)
    data_fim: date | None = Field(default=None)

    dia_vencimento: int = Field(
        ge=1,
        le=31,
        nullable=False
    )

    valor_mensal: Decimal = Field(
        max_digits=10,
        decimal_places=2,
        nullable=False
    )

    status: StatusContrato = Field(
        default=StatusContrato.ATIVO,
        sa_column=Column(
            SAEnum(
                StatusContrato,
                values_callable=lambda enum_cls: [
                    item.value for item in enum_cls
                ],
            ),
            nullable=False,
            server_default="ativo",
        ),
    )


    id_usuario_cadastro: int = Field(
    foreign_key="usuarios_estacionamento.id_usuario",
    nullable=False
    )

    id_usuario_alteracao: int | None = Field(
        default=None,
        foreign_key="usuarios_estacionamento.id_usuario"
    )


class StatusEstacionamento(str, Enum):
    ABERTO = "aberto"
    FINALIZADO = "finalizado"
    CANCELADO = "cancelado"


class Estacionamento(SQLModel, table=True):
    __tablename__ = "estacionamentos"

    id_estacionamento: int | None = Field(
        default=None,
        primary_key=True
    )

    id_veiculo: int = Field(nullable=False)
    id_vaga: int = Field(nullable=False)
    id_contrato: int | None = Field(default=None)
    id_tarifa: int | None = Field(default=None)

    id_usuario_entrada: int = Field(
        foreign_key="usuarios_estacionamento.id_usuario",
        nullable=False
    )

    id_usuario_saida: int | None = Field(
        default=None,
        foreign_key="usuarios_estacionamento.id_usuario"
    )

    data_hora_entrada: datetime = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=False),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        ),
    )

    data_hora_saida: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=False),
            nullable=True,
        ),
    )

    valor_calculado: Decimal | None = Field(
        default=None,
        max_digits=10,
        decimal_places=2
    )

    
    status: StatusEstacionamento = Field(
        default=StatusEstacionamento.ABERTO,
        sa_column=Column(
            SAEnum(
                StatusEstacionamento,
                name="statusestacionamento",
                values_callable=lambda enum_cls: [
                    item.value for item in enum_cls
                ],
                native_enum=True,
            ),
            nullable=False,
            default=StatusEstacionamento.ABERTO,
            server_default="aberto",
        ),
    )


    data_cadastro: datetime = Field(
    nullable=False,
    sa_type=DateTime,
    sa_column_kwargs={
        "server_default": text("CURRENT_TIMESTAMP")
    }
    )
    data_alteracao: datetime = Field(
    nullable=False,
    sa_type=DateTime,
    sa_column_kwargs={
        "server_default": text("CURRENT_TIMESTAMP"),
        "onupdate": func.now()
    }
    )

class StatusMensalidade(str, Enum):
    PENDENTE = "pendente"
    PAGO = "pago"
    VENCIDO = "vencido"
    CANCELADO = "cancelado"


class Mensalidade(SQLModel, table=True):
    __tablename__ = "mensalidades"

    id_mensalidade: int | None = Field(
        default=None,
        primary_key=True
    )

    id_contrato: int = Field(nullable=False)

    competencia: date = Field(nullable=False)
    data_vencimento: date = Field(nullable=False)

    valor: Decimal = Field(
        max_digits=10,
        decimal_places=2,
        nullable=False
    )

    status: StatusMensalidade = Field(
        default=StatusMensalidade.PENDENTE,
        nullable=False
    )

    data_pagamento: datetime | None = Field(default=None)

    data_cadastro: datetime = Field(
        nullable=False,
        sa_type=DateTime,
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP")
        }
    )

    data_alteracao: datetime = Field(
        nullable=False,
        sa_type=DateTime,
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
            "onupdate": func.now()
        }
    )

    id_usuario_cadastro: int = Field(nullable=False)
    id_usuario_alteracao: int | None = Field(default=None)

class FormaPagamento(str, Enum):
    DINHEIRO = "dinheiro"
    PIX = "pix"
    CARTAO_CREDITO = "cartao_credito"
    CARTAO_DEBITO = "cartao_debito"
    TRANSFERENCIA = "transferencia"


class StatusPagamento(str, Enum):
    PENDENTE = "pendente"
    PAGO = "pago"
    ESTORNADO = "estornado"
    CANCELADO = "cancelado"


class Pagamento(SQLModel, table=True):
    __tablename__ = "pagamentos"

    id_pagamento: int | None = Field(
        default=None,
        primary_key=True
    )

    id_mensalidade: int | None = Field(default=None)
    id_estacionamento: int | None = Field(default=None)

    valor: Decimal = Field(
        max_digits=10,
        decimal_places=2,
        nullable=False
    )

    data_pagamento: datetime | None = Field(default=None)

    forma_pagamento: FormaPagamento = Field(nullable=False)

    status: StatusPagamento = Field(
        default=StatusPagamento.PENDENTE,
        nullable=False
    )

    id_usuario: int = Field(nullable=False)

    data_cadastro: datetime = Field(
        nullable=False,
        sa_type=DateTime,
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP")
        }
    )

    data_alteracao: datetime = Field(
        nullable=False,
        sa_type=DateTime,
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
            "onupdate": func.now()
        }
    )

    id_usuario_cadastro: int = Field(nullable=False)
    id_usuario_alteracao: int | None = Field(default=None)
