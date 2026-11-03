
from sqlmodel import Session, select

from entidades.models import Cliente
from schemas.clientes import ClienteCriar, ClienteAtualizar


def cadastrar_cliente(dados: ClienteCriar, db: Session) -> Cliente:
    cliente = Cliente.model_validate(
        dados.model_dump(),
        update={"id_usuario_cadastro": 1}
    )

    db.add(cliente)
    db.commit()
    db.refresh(cliente)

    return cliente


def listar_clientes(db: Session) -> list[Cliente]:
    comando = select(Cliente).where(Cliente.ativo == True)
    return list(db.exec(comando).all())


def buscar_cliente_por_id(
    id_cliente: int,
    db: Session
) -> Cliente | None:
    comando = select(Cliente).where(
        Cliente.id_cliente == id_cliente
    )
    return db.exec(comando).first()


def atualizar_cliente(
    id_cliente: int,
    dados: ClienteAtualizar,
    db: Session
) -> Cliente | None:
    cliente = buscar_cliente_por_id(id_cliente, db)

    if cliente is None or not cliente.ativo:
        return None

    atualizacoes = dados.model_dump()

    for campo, valor in atualizacoes.items():
        setattr(cliente, campo, valor)

    db.add(cliente)
    db.commit()
    db.refresh(cliente)

    return cliente


def desativar_cliente(
    id_cliente: int,
    db: Session
) -> Cliente | None:
    cliente = buscar_cliente_por_id(id_cliente, db)

    if cliente is None or not cliente.ativo:
        return None

    cliente.ativo = False

    db.add(cliente)
    db.commit()
    db.refresh(cliente)

    return cliente
