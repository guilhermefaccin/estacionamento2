import socket
import threading
import time

import pytest
import uvicorn

from main import app


@pytest.mark.browser
def test_interface_login_cadastros_e_operacao(client, cadastros):
    playwright = pytest.importorskip("playwright.sync_api")
    client.post("/vagas/", json={"numero_vaga": "M01", "tipo_uso": "mensalista"})
    client.post(
        "/tarifas/", json={"nome": "Mensal", "modalidade": "mensalista", "valor": 200}
    )
    contrato = client.post(
        "/contratos-mensais/",
        json={
            "id_cliente": 1,
            "id_vaga": 2,
            "id_tarifa": 2,
            "data_inicio": "2026-01-01",
            "dia_vencimento": 10,
            "valor_mensal": 200,
        },
    )
    assert contrato.status_code == 201
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    porta = sock.getsockname()[1]
    servidor = uvicorn.Server(uvicorn.Config(app, log_level="error", lifespan="off"))
    thread = threading.Thread(
        target=servidor.run, kwargs={"sockets": [sock]}, daemon=True
    )
    thread.start()
    try:
        limite = time.monotonic() + 10
        while not servidor.started and time.monotonic() < limite:
            time.sleep(0.01)
        assert servidor.started
        with playwright.sync_playwright() as p:
            browser = p.chromium.launch(channel="msedge", headless=True)
            page = browser.new_page()
            erros = []
            page.on("pageerror", lambda erro: erros.append(str(erro)))
            page.on("dialog", lambda dialog: dialog.accept())
            page.goto(f"http://127.0.0.1:{porta}")
            expect = playwright.expect
            expect(page.locator("#login-screen")).to_be_visible()
            expect(page.locator(".sidebar")).to_be_hidden()
            page.fill("#login-email", "admin@example.com")
            page.fill("#login-senha", "Teste@123")
            page.click("#btn-login")
            expect(page.locator("#app-container")).to_be_visible()
            expect(page.locator("#stat-vagas")).to_have_text("2")

            page.click('[data-page="usuarios"]')
            page.fill("#u-nome", "Operador navegador")
            page.fill("#u-cpf", "98765432100")
            page.fill("#u-email", "operador@example.com")
            page.fill("#u-senha", "Senha@123")
            page.click('#form-usuarios button[type="submit"]')
            expect(page.locator("#lista-usuarios")).to_contain_text(
                "Operador navegador"
            )
            page.locator('#lista-usuarios [data-edit][data-id="8"]').click()
            expect(page.locator("#u-senha")).to_be_hidden()
            page.fill("#u-nome", "Operador atualizado")
            page.click('#form-usuarios button[type="submit"]')
            expect(page.locator("#lista-usuarios")).to_contain_text(
                "Operador atualizado"
            )

            page.click('[data-page="estacionamentos"]')
            page.select_option("#entrada-veiculo", "1")
            page.select_option("#entrada-vaga", "1")
            page.select_option("#entrada-tarifa", "1")
            expect(page.locator('#entrada-vaga option[value="2"]')).to_have_count(0)
            expect(page.locator('#entrada-tarifa option[value="2"]')).to_have_count(0)
            expect(page.locator("#entrada-usuario")).to_have_value("7")
            page.click('#form-entrada button[type="submit"]')
            expect(page.locator("#lista-abertos button")).to_have_text(
                "Registrar saída"
            )
            expect(page.locator('#entrada-vaga option[value="1"]')).to_have_count(0)
            page.locator("#lista-abertos button").click()
            expect(page.locator("#alerta")).to_contain_text("Valor calculado")
            expect(page.locator('#entrada-vaga option[value="1"]')).to_have_count(1)

            page.click('[data-page="contratos"]')
            page.locator('#lista-contratos [data-edit][data-id="1"]').click()
            expect(page.locator("#ct-vaga")).to_have_value("2")
            expect(page.locator('#ct-tarifa option[value="1"]')).to_have_count(0)
            page.fill("#ct-valor", "210")
            page.click('#form-contratos button[type="submit"]')
            expect(page.locator("#lista-contratos")).to_contain_text("210,00")
            assert client.get("/contratos-mensais/1").json()["id_vaga"] == 2

            page.click("#btn-logout")
            expect(page.locator("#login-screen")).to_be_visible()
            page.fill("#login-email", "operador@example.com")
            page.fill("#login-senha", "Senha@123")
            page.click("#btn-login")
            expect(page.locator("#app-container")).to_be_visible()
            expect(page.locator('[data-page="usuarios"]')).to_be_hidden()
            page.click('[data-page="marcas"]')
            expect(page.locator("#form-marcas")).to_be_hidden()
            expect(page.locator("#lista-marcas")).to_contain_text("Marca teste")
            expect(page.locator("#lista-marcas [data-edit]")).to_have_count(0)
            page.reload()
            expect(page.locator("#app-container")).to_be_visible()
            expect(page.locator('[data-page="usuarios"]')).to_be_hidden()
            assert erros == []
            browser.close()
    finally:
        servidor.should_exit = True
        thread.join(timeout=10)
        sock.close()
