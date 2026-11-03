
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pathlib import Path
from fastapi.responses import FileResponse
from banco.sessao import obter_sessao
from rotas.vagas import router as vagas_router
from schemas.usuario import (
    UsuarioCriar,
    UsuarioResposta,
    UsuarioAtualizar,
)
from servicos.usuario import (
    cadastrar_usuario,
    listar_usuarios,
    buscar_usuario_por_id,
    atualizar_usuario,
    desativar_usuario,
)
from entidades.models import Usuario
from fastapi import Depends, HTTPException, status
from schemas.autenticacao import AlterarSenhaRequest
from servicos.seguranca import verificar_senha, gerar_hash_senha
from entidades import models
from rotas.clientes import router as clientes_router
from rotas.veiculos import router as veiculos_router
from rotas.marcas import router as marcas_router
from rotas.tarifas import router as tarifas_router
from rotas.contratos_mensais import router as contratos_mensais_router
from rotas.estacionamentos import router as estacionamentos_router
from fastapi.middleware.cors import CORSMiddleware
from schemas.autenticacao import LoginRequest, LoginResposta
from servicos.autenticacao import (
    autenticar_usuario,
    criar_token_acesso,
    exigir_admin,
)
from fastapi.staticfiles import StaticFiles


app = FastAPI(
    title="Sistema de Estacionamento",
    description="API para gerenciamento de estacionamento horista e mensalista.",
    version="1.0.0",
)

app.include_router(clientes_router)
app.include_router(veiculos_router)
app.include_router(marcas_router)
app.include_router(vagas_router)
app.include_router(tarifas_router)
app.include_router(contratos_mensais_router)
app.include_router(estacionamentos_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent


@app.get("/app", include_in_schema=False)
def pagina_inicial():
    return FileResponse(BASE_DIR / "frontend" / "index.html")

@app.get("/", include_in_schema=False)
def pagina_inicial():
    return FileResponse(BASE_DIR / "frontend" / "index.html")


@app.get("/status")
def status():
    return {
        "status": "online"
    }

app.mount(
    "/frontend",
    StaticFiles(directory=BASE_DIR / "frontend"),
    name="frontend"
)
##################################

@app.patch("/admin/alterar-senha", status_code=200)
def alterar_senha_admin(
    dados: AlterarSenhaRequest,
    usuario: Usuario = Depends(exigir_admin),
    db: Session = Depends(obter_sessao)
):
    # Confere a senha atual
    if not verificar_senha(dados.senha_atual, usuario.senha):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A senha atual está incorreta."
        )

    # Confere se as novas senhas são iguais
    if dados.nova_senha != dados.confirmar_nova_senha:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A confirmação da nova senha não corresponde."
        )

    # Gera o hash da nova senha
    usuario.senha = gerar_hash_senha(dados.nova_senha)

    db.add(usuario)
    db.commit()

    return {
        "mensagem": "Senha alterada com sucesso."
    }

####################

@app.post("/usuarios", response_model=UsuarioResposta, status_code=201)
def criar_usuario(
    dados: UsuarioCriar,
    db: Session = Depends(obter_sessao),
    usuario_logado: models.Usuario = Depends(exigir_admin),
):
    try:
        return cadastrar_usuario(dados, db)

    except IntegrityError as e:
        db.rollback()
        print(f"Erro de integridade ao cadastrar usuario: {e}")
        raise HTTPException(
            status_code=409,
            detail="Conflito de integridade no banco de dados. Verifique o terminal.",
        )

    except SQLAlchemyError as e:
        db.rollback()
        print(f"Erro de banco de dados: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao cadastrar usuario no banco de dados.",
        )
@app.get("/usuarios", response_model=list[UsuarioResposta])
def obter_usuarios(
    db: Session = Depends(obter_sessao),
    usuario_logado: models.Usuario = Depends(exigir_admin),
):
    return listar_usuarios(db)

@app.get("/usuarios/{id_usuario}", response_model=UsuarioResposta)
def obter_usuario(
    id_usuario: int,
    db: Session = Depends(obter_sessao),
):
    usuario = buscar_usuario_por_id(id_usuario, db)

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado.",
        )   

    return usuario

@app.put("/usuarios/{id_usuario}", response_model=UsuarioResposta)
def editar_usuario(
    id_usuario: int,
    dados: UsuarioAtualizar,
    db: Session = Depends(obter_sessao),
    usuario_logado: models.Usuario = Depends(exigir_admin),
):
    try:
        usuario = atualizar_usuario(id_usuario, dados, db)

        if usuario is None:
            raise HTTPException(
                status_code=404,
                detail="Usuário não encontrado.",
            )

        return usuario

    except IntegrityError as e:
        db.rollback()
        print(f"Erro de integridade ao atualizar usuario: {e}")
        raise HTTPException(
            status_code=409,
            detail="CPF já cadastrado ou conflito de integridade.",
        )

    except SQLAlchemyError as e:
        db.rollback()
        print(f"Erro de banco de dados ao atualizar usuario: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao atualizar usuario no banco de dados.",
        )


@app.patch("/usuarios/{id_usuario}/desativar", response_model=UsuarioResposta)
def rota_desativar_usuario(
    id_usuario: int,
    db: Session = Depends(obter_sessao),
    usuario_logado: models.Usuario = Depends(exigir_admin),
):
    usuario = desativar_usuario(id_usuario, db)

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado.",
        )

    return usuario

@app.post("/login", response_model=LoginResposta)
def login(
    dados: LoginRequest,
    db: Session = Depends(obter_sessao)
    
):
    usuario = autenticar_usuario(
        email=str(dados.email),
        senha=dados.senha,
        db=db
    )

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha incorretos."
        )

    token = criar_token_acesso(usuario)

    return LoginResposta(
        access_token=token,
        token_type="bearer"
    )