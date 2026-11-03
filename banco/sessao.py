
from sqlmodel import Session, create_engine
from sqlalchemy.pool import StaticPool

from banco.conexao import obter_conexao


def obter_sessao():
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
        conexao_mysql.close()
        tunel.stop()
