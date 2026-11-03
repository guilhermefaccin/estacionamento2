from fastapi import HTTPException
from sqlmodel import Session, select

from entidades.models import Usuario
from schemas.usuario import UsuarioAtualizar, UsuarioCriar
from servicos.seguranca import gerar_hash_senha


def cadastrar_usuario(dados: UsuarioCriar, db: Session):
    validar_email(str(dados.email), db)
    usuario = Usuario(
        nome=dados.nome,
        cpf=dados.cpf,
        email=str(dados.email),
        senha=gerar_hash_senha(dados.senha),
        perfil="USUARIO",
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return usuario


def listar_usuarios(db: Session) -> list[Usuario]:
    comando = select(Usuario).where(Usuario.ativo.is_(True))
    usuarios = db.exec(comando).all()
    return list(usuarios)


def buscar_usuario_por_id(id_usuario: int, db: Session) -> Usuario | None:
    comando = select(Usuario).where(Usuario.id_usuario == id_usuario)

    return db.exec(comando).first()


def atualizar_usuario(
    id_usuario: int, dados: UsuarioAtualizar, db: Session
) -> Usuario | None:
    usuario = buscar_usuario_por_id(id_usuario, db)

    if usuario is None:
        return None

    validar_email(str(dados.email), db, id_usuario)

    usuario.nome = dados.nome
    usuario.cpf = dados.cpf
    usuario.email = str(dados.email)

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return usuario


def desativar_usuario(id_usuario: int, db: Session) -> Usuario | None:
    usuario = buscar_usuario_por_id(id_usuario, db)

    if usuario is None:
        return None

    usuario.ativo = False

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return usuario


def validar_email(email: str, db: Session, id_usuario: int = 0):
    existente = db.exec(
        select(Usuario).where(
            Usuario.email == email,
            Usuario.id_usuario != id_usuario,
        )
    ).first()
    if existente:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
