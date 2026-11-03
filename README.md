# ParkControl

Sistema de estacionamento com FastAPI, SQLModel e interface HTML/CSS/JavaScript.
Requer Python 3.10 ou superior.

## Executar no Windows (PowerShell)

Na pasta `estacionamento2`:

```powershell
python -m venv .venv
python -m pip --python .venv install -r requirements.txt
.\.venv\Scripts\python.exe criar_admin.py
.\.venv\Scripts\python.exe iniciar.py
```

Abra **http://127.0.0.1:8080** e entre com os dados do administrador criado.
A documentação da API fica em **http://127.0.0.1:8080/docs**.
A interface deve ser acessada pelo servidor; não abra `index.html` diretamente.
O servidor e a interface usam a mesma origem, inclusive quando a porta é alterada.
Mantenha o terminal do servidor aberto durante o uso. No VS Code, a configuração
**Iniciar e abrir ParkControl** inicia a API antes de abrir o navegador.
Se a API já estiver ativa na porta 8080, `iniciar.py` reutiliza essa instância.
Para outra porta, execute `iniciar.py --port 8081` e abra a URL correspondente.
Para desenvolvimento com recarga automática, use
`python -m uvicorn main:app --reload --port 8080` com o ambiente virtual ativado.

Se `venv` falhar na etapa `ensurepip`, execute `python -m venv --without-pip .venv`
e use o comando de instalação acima, que utiliza o pip do Python principal.

Sem `.env`, as tabelas são criadas automaticamente em `estacionamento.db`, na raiz
do projeto. A chave JWT local é gerada em `.jwt_secret` e reutilizada nos próximos
inícios. Esses arquivos e o `.env` são ignorados pelo Git. Não há senha padrão.

## MySQL existente

```powershell
python -m pip --python .venv install -r requirements-mysql.txt
Copy-Item .env.example .env
```

Preencha `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`,
`MYSQL_DATABASE` e `JWT_SECRET_KEY`. Gere uma chave com:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Para usar túnel SSH, preencha também `SSH_HOST`, `SSH_PORT`, `SSH_USER` e
`SSH_PASSWORD`. Sem `SSH_HOST`, a conexão MySQL é direta. O banco MySQL deve
possuir as tabelas correspondentes aos modelos; a inicialização automática de
tabelas se aplica ao SQLite. Não há migrações automáticas em bancos existentes.

`DATABASE_URL`, quando definida, tem prioridade sobre os campos `MYSQL_*`.
Para MySQL por URL, use o driver `mysql+mysqlconnector` e codifique caracteres
especiais das credenciais na URL.

## Fluxo de uso

1. Cadastre clientes, marcas e veículos.
2. Cadastre vagas rotativas e uma tarifa horista com intervalo em minutos.
3. Em **Entrada e saída**, registre a entrada e depois finalize a saída.
   A cobrança considera cada intervalo iniciado, com mínimo de um intervalo.
4. Para mensalistas, cadastre uma tarifa mensalista e vagas do tipo mensalista.
   Um contrato ativo reserva a vaga; transferir ou encerrar o contrato libera a
   vaga anterior. Contratos sem vaga definida também são aceitos.

As rotas operacionais exigem login. Apenas administradores gerenciam usuários e
alteram marcas. A auditoria utiliza o usuário do token, sem aceitar um ID
informado pelo navegador. A troca de senha administrativa está disponível em
`PATCH /admin/alterar-senha` na documentação da API.

## Organização e verificações

- `main.py`: aplicação, arquivos estáticos e registro das rotas.
- `configuracao.py` e `banco/`: configurações, conexões e sessões.
- `entidades/`, `schemas/`, `rotas/` e `servicos/`: modelos, validação, API e regras.
- `frontend/`: interface; `tests/`: testes de integração com banco em memória.

```powershell
python -m pip --python .venv install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
```

Os testes não modificam os dados do banco local nem do MySQL.

Para testar também a interface, com Microsoft Edge instalado:

```powershell
python -m pip --python .venv install -r requirements-browser.txt
.\.venv\Scripts\python.exe -m pytest -q -m browser
```
