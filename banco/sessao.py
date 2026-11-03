from functools import lru_cache

from sqlalchemy import event
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from configuracao import DATABASE_URL, USAR_MYSQL_LEGADO


@lru_cache
def obter_engine():
    argumentos = {"pool_pre_ping": True}
    if DATABASE_URL.startswith("sqlite:"):
        argumentos["connect_args"] = {"check_same_thread": False}
        if DATABASE_URL in ("sqlite://", "sqlite:///:memory:"):
            argumentos["poolclass"] = StaticPool
    engine = create_engine(DATABASE_URL, **argumentos)
    if engine.dialect.name == "sqlite":

        @event.listens_for(engine, "connect")
        def ativar_chaves_estrangeiras(conexao, _):
            conexao.execute("PRAGMA foreign_keys=ON")

    return engine


def inicializar_banco():
    # Bancos remotos mantêm seu esquema existente; SQLite serve para uso local.
    if not USAR_MYSQL_LEGADO and DATABASE_URL.startswith("sqlite:"):
        from entidades import models  # noqa: F401

        SQLModel.metadata.create_all(obter_engine())


def obter_sessao():
    if not USAR_MYSQL_LEGADO:
        with Session(obter_engine(), expire_on_commit=False) as sessao:
            yield sessao
        return

    from banco.conexao import obter_conexao

    tunel, conexao_mysql = obter_conexao()
    engine = create_engine(
        "mysql+mysqlconnector://",
        creator=lambda: conexao_mysql,
        poolclass=StaticPool,
    )

    try:
        with Session(engine, expire_on_commit=False) as sessao:
            yield sessao

    finally:
        engine.dispose()
        if tunel is not None:
            tunel.stop()
