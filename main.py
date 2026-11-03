"""Entrada da aplicação e registro das rotas."""

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from banco.sessao import inicializar_banco
from configuracao import BASE_DIR
from rotas import (
    autenticacao,
    clientes,
    contratos_mensais,
    estacionamentos,
    marcas,
    tarifas,
    usuarios,
    vagas,
    veiculos,
)
from servicos.autenticacao import obter_usuario_logado

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    inicializar_banco()
    yield


app = FastAPI(
    title="Sistema de Estacionamento",
    description="API para gerenciamento de estacionamento horista e mensalista.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(autenticacao.router)
for modulo in (
    clientes,
    contratos_mensais,
    estacionamentos,
    marcas,
    tarifas,
    usuarios,
    vagas,
    veiculos,
):
    app.include_router(modulo.router, dependencies=[Depends(obter_usuario_logado)])


@app.exception_handler(IntegrityError)
async def tratar_integridade(request: Request, erro: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={"detail": "Registro duplicado ou referência inválida."},
    )


@app.exception_handler(SQLAlchemyError)
async def tratar_erro_banco(request: Request, erro: SQLAlchemyError):
    logger.error("Erro de banco em %s", request.url.path, exc_info=erro)
    return JSONResponse(
        status_code=500,
        content={"detail": "Não foi possível concluir a operação no banco de dados."},
    )


@app.get("/app", include_in_schema=False)
@app.get("/", include_in_schema=False)
def pagina_inicial():
    return FileResponse(BASE_DIR / "frontend" / "index.html")


@app.get("/status")
def verificar_status():
    return {"status": "online"}


app.mount("/frontend", StaticFiles(directory=BASE_DIR / "frontend"), name="frontend")
