from datetime import datetime, timedelta

import pytest


def entrada(cadastros):
    return {
        "id_veiculo": cadastros["veiculo"]["id_veiculo"],
        "id_vaga": cadastros["vaga"]["id_vaga"],
        "id_tarifa": cadastros["tarifa"]["id_tarifa"],
    }


def test_entrada_saida_e_auditoria(client, cadastros):
    resposta = client.post(
        "/estacionamentos/entrada?id_usuario=999", json=entrada(cadastros)
    )
    assert resposta.status_code == 201, resposta.text
    registro = resposta.json()
    assert registro["id_usuario_entrada"] == 7
    assert client.get("/vagas/1").json()["status"] == "ocupada"
    assert client.patch("/vagas/1/desativar").status_code == 409
    assert (
        client.post("/estacionamentos/entrada", json=entrada(cadastros)).status_code
        == 409
    )
    # Uma tarifa desativada após a entrada ainda permite finalizar a cobrança.
    assert client.patch("/tarifas/1/desativar").status_code == 200
    saida = client.patch(f"/estacionamentos/{registro['id_estacionamento']}/saida")
    assert saida.status_code == 200, saida.text
    assert saida.json()["id_usuario_saida"] == 7
    assert float(saida.json()["valor_calculado"]) == 10.0
    assert client.get("/vagas/1").json()["status"] == "livre"
    assert client.get("/estacionamentos/abertos").json() == []
    assert (
        client.patch(
            f"/estacionamentos/{registro['id_estacionamento']}/saida"
        ).status_code
        == 409
    )


def test_entrada_sem_tarifa_nao_ocupa_vaga(client, cadastros):
    dados = entrada(cadastros)
    dados.pop("id_tarifa")
    assert client.post("/estacionamentos/entrada", json=dados).status_code == 400
    assert client.get("/vagas/1").json()["status"] == "livre"


def test_cobranca_por_intervalo_iniciado(client, cadastros, monkeypatch):
    resposta = client.post("/estacionamentos/entrada", json=entrada(cadastros))
    assert resposta.status_code == 201
    inicio = datetime.fromisoformat(resposta.json()["data_hora_entrada"])

    class Relogio:
        @staticmethod
        def now():
            return inicio + timedelta(minutes=61)

    monkeypatch.setattr("servicos.estacionamentos.datetime", Relogio)
    saida = client.patch(
        f"/estacionamentos/{resposta.json()['id_estacionamento']}/saida"
    )
    assert saida.status_code == 200, saida.text
    assert float(saida.json()["valor_calculado"]) == 20.0


def test_entrada_com_tarifa_futura(client, cadastros):
    futuro = (datetime.now() + timedelta(days=1)).isoformat()
    assert (
        client.put("/tarifas/1", json={"data_inicio_vigencia": futuro}).status_code
        == 200
    )
    assert (
        client.post("/estacionamentos/entrada", json=entrada(cadastros)).status_code
        == 400
    )


def test_cadastro_edicao_e_desativacao(client, cadastros):
    assert client.put("/clientes/1", json={"nome": "Nome alterado"}).status_code == 200
    assert client.put("/marcas/1", json={"nome": "Outra marca"}).status_code == 200
    veiculo = {**cadastros["veiculo"], "modelo": "Outro modelo"}
    assert client.put("/veiculos/1", json=veiculo).status_code == 200
    assert client.patch("/veiculos/1/desativar").status_code == 200
    assert client.get("/veiculos/").json() == []
    assert client.patch("/clientes/1/desativar").status_code == 200
    assert client.get("/clientes").json() == []


def test_referencias_invalidas(client, cadastros):
    dados = {**cadastros["veiculo"], "placa": "XYZ9876", "id_cliente": 999}
    assert client.post("/veiculos/", json=dados).status_code == 404


def test_usuario_login_permissoes_e_email_duplicado(client):
    dados = {
        "nome": "Operador",
        "cpf": "98765432100",
        "email": "operador@example.com",
        "senha": "Senha@123",
    }
    resposta = client.post("/usuarios", json=dados)
    assert resposta.status_code == 201, resposta.text
    assert "senha" not in resposta.json()
    assert (
        client.post("/usuarios", json={**dados, "cpf": "98765432101"}).status_code
        == 409
    )
    resposta = client.post(
        "/login", json={"email": dados["email"], "senha": dados["senha"]}
    )
    assert resposta.status_code == 200
    client.headers["Authorization"] = f"Bearer {resposta.json()['access_token']}"
    assert client.get("/usuarios").status_code == 403
    assert client.get("/usuarios/7").status_code == 403
    assert (
        client.post("/clientes", json={"nome": "Cliente do operador"}).status_code
        == 201
    )


def test_alterar_senha_admin(client):
    dados = {
        "senha_atual": "errada",
        "nova_senha": "NovaSenha@123",
        "confirmar_nova_senha": "NovaSenha@123",
    }
    assert client.patch("/admin/alterar-senha", json=dados).status_code == 400
    dados["senha_atual"] = "Teste@123"
    assert client.patch("/admin/alterar-senha", json=dados).status_code == 200
    assert (
        client.post(
            "/login", json={"email": "admin@example.com", "senha": "Teste@123"}
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/login", json={"email": "admin@example.com", "senha": "NovaSenha@123"}
        ).status_code
        == 200
    )


@pytest.mark.parametrize(
    "path",
    [
        "/usuarios",
        "/clientes",
        "/vagas/",
        "/estacionamentos/abertos",
        "/contratos-mensais/",
    ],
)
def test_rotas_exigem_autenticacao(client, path):
    client.headers.pop("Authorization")
    assert client.get(path).status_code == 401
    assert client.get("/status").json() == {"status": "online"}
    assert client.get("/").status_code == 200


def test_tarifa_invalida(client):
    assert (
        client.post(
            "/tarifas/",
            json={"nome": "Sem intervalo", "modalidade": "horista", "valor": 10},
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/tarifas/",
            json={
                "nome": "Invertida",
                "modalidade": "mensalista",
                "valor": 100,
                "data_inicio_vigencia": "2026-05-01T00:00:00",
                "data_fim_vigencia": "2026-04-01T00:00:00",
            },
        ).status_code
        == 422
    )


def test_contrato_reserva_transfere_e_libera_vaga(client, cadastros):
    tarifa = client.post(
        "/tarifas/", json={"nome": "Mensal", "modalidade": "mensalista", "valor": 200}
    ).json()
    for numero in ("M01", "M02"):
        assert (
            client.post(
                "/vagas/", json={"numero_vaga": numero, "tipo_uso": "mensalista"}
            ).status_code
            == 201
        )
    dados = {
        "id_cliente": 1,
        "id_vaga": 2,
        "id_tarifa": tarifa["id_tarifa"],
        "data_inicio": "2026-01-01",
        "dia_vencimento": 10,
        "valor_mensal": 200,
    }
    resposta = client.post("/contratos-mensais/", json=dados)
    assert resposta.status_code == 201, resposta.text
    assert client.get("/vagas/2").json()["status"] == "ocupada"
    assert client.post("/contratos-mensais/", json=dados).status_code == 409
    assert client.put("/contratos-mensais/1", json={"id_vaga": 3}).status_code == 200
    assert client.get("/vagas/2").json()["status"] == "livre"
    assert client.get("/vagas/3").json()["status"] == "ocupada"
    assert client.patch("/contratos-mensais/1/encerrar").status_code == 200
    assert client.get("/vagas/3").json()["status"] == "livre"
    assert client.get("/contratos-mensais/").json() == []


def test_contrato_rejeita_vaga_rotativa(client, cadastros):
    tarifa = client.post(
        "/tarifas/", json={"nome": "Mensal", "modalidade": "mensalista", "valor": 200}
    ).json()
    resposta = client.post(
        "/contratos-mensais/",
        json={
            "id_cliente": 1,
            "id_vaga": 1,
            "id_tarifa": tarifa["id_tarifa"],
            "data_inicio": "2026-01-01",
            "dia_vencimento": 10,
            "valor_mensal": 200,
        },
    )
    assert resposta.status_code == 400
