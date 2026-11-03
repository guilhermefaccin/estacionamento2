from sqlmodel import Session, select

from entidades.models import Marca
from schemas.marcas import MarcaCriar, MarcaAtualizar


def cadastrar_marca(dados: MarcaCriar, db: Session) -> Marca:
    marca = Marca(
        nome=dados.nome,
        id_usuario_cadastro=1,
        ativo=True,
    )

    db.add(marca)
    db.commit()
    db.refresh(marca)

    return marca


def listar_marcas(db: Session) -> list[Marca]:
    comando = select(Marca).where(Marca.ativo.is_(True))
    return list(db.exec(comando).all())


def buscar_marca_por_id(
    id_marca: int,
    db: Session,
) -> Marca | None:
    comando = select(Marca).where(Marca.id_marca == id_marca)
    return db.exec(comando).first()


def atualizar_marca(
    id_marca: int,
    dados: MarcaAtualizar,
    db: Session,
) -> Marca | None:
    marca = buscar_marca_por_id(id_marca, db)

    if marca is None or not marca.ativo:
        return None

    marca.nome = dados.nome
    marca.id_usuario_alteracao = 1

    db.add(marca)
    db.commit()
    db.refresh(marca)

    return marca


def desativar_marca(
    id_marca: int,
    db: Session,
) -> Marca | None:
    marca = buscar_marca_por_id(id_marca, db)

    if marca is None or not marca.ativo:
        return None

    marca.ativo = False
    marca.id_usuario_alteracao = 1

    db.add(marca)
    db.commit()
    db.refresh(marca)

    return marca