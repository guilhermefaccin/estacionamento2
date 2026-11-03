from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.pool import QueuePool
from sqlmodel import Session, SQLModel, create_engine

from banco.sessao import obter_sessao
from entidades.models import Usuario
from main import app
from servicos.seguranca import gerar_hash_senha


@pytest.fixture
def client(monkeypatch):
    engine = create_engine(
        f"sqlite:///file:teste_{uuid4().hex}?mode=memory&cache=shared&uri=true",
        connect_args={"check_same_thread": False},
        poolclass=QueuePool,
    )

    @event.listens_for(engine, "connect")
    def foreign_keys(conexao, _):
        conexao.execute("PRAGMA foreign_keys=ON")

    SQLModel.metadata.create_all(engine)
    with Session(engine) as db:
        db.add(
            Usuario(
                id_usuario=7,
                nome="Administrador",
                cpf="12345678901",
                email="admin@example.com",
                senha=gerar_hash_senha("Teste@123"),
                perfil="ADMIN",
            )
        )
        db.commit()

    def sessao_teste():
        with Session(engine, expire_on_commit=False) as db:
            yield db

    monkeypatch.setattr("main.inicializar_banco", lambda: None)
    app.dependency_overrides[obter_sessao] = sessao_teste
    try:
        with TestClient(app) as test_client:
            resposta = test_client.post(
                "/login", json={"email": "admin@example.com", "senha": "Teste@123"}
            )
            assert resposta.status_code == 200, resposta.text
            test_client.headers["Authorization"] = (
                f"Bearer {resposta.json()['access_token']}"
            )
            yield test_client
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


@pytest.fixture
def cadastros(client):
    def criar(path, dados):
        resposta = client.post(path, json=dados)
        assert resposta.status_code == 201, resposta.text
        return resposta.json()

    cliente = criar("/clientes", {"nome": "Cliente teste"})
    marca = criar("/marcas/", {"nome": "Marca teste"})
    veiculo = criar(
        "/veiculos/",
        {
            "id_cliente": cliente["id_cliente"],
            "id_marca": marca["id_marca"],
            "placa": "ABC1D23",
            "modelo": "Modelo teste",
        },
    )
    vaga = criar("/vagas/", {"numero_vaga": "A01", "tipo_uso": "rotativa"})
    tarifa = criar(
        "/tarifas/",
        {
            "nome": "Hora",
            "modalidade": "horista",
            "valor": "10.00",
            "intervalo_minutos": 60,
        },
    )
    return {
        "cliente": cliente,
        "marca": marca,
        "veiculo": veiculo,
        "vaga": vaga,
        "tarifa": tarifa,
    }
