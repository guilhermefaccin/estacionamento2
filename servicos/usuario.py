
from sqlmodel import Session, select

from entidades.models import Usuario
from schemas.usuario import UsuarioCriar, UsuarioAtualizar
from servicos.seguranca import gerar_hash_senha


def cadastrar_usuario(dados: UsuarioCriar, db: Session):
    usuario = Usuario(
        nome=dados.nome,
        cpf=dados.cpf,
        email=str(dados.email),
        senha=gerar_hash_senha(dados.senha),
        perfil="USUARIO"
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return usuario


def listar_usuarios(db: Session) -> list[Usuario]:
    comando = select(Usuario).where(Usuario.ativo == True)
    usuarios = db.exec(comando).all()
    return list(usuarios)


def buscar_usuario_por_id(
    id_usuario: int,
    db: Session
) -> Usuario | None:
    comando = select(Usuario).where(
        Usuario.id_usuario == id_usuario
    )

    return db.exec(comando).first()


def atualizar_usuario(
    id_usuario: int,
    dados: UsuarioAtualizar,
    db: Session
) -> Usuario | None:
    usuario = buscar_usuario_por_id(id_usuario, db)

    if usuario is None:
        return None

    usuario.nome = dados.nome
    usuario.cpf = dados.cpf
    usuario.email = str(dados.email)

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return usuario


def desativar_usuario(
    id_usuario: int,
    db: Session
) -> Usuario | None:
    usuario = buscar_usuario_por_id(id_usuario, db)

    if usuario is None:
        return None

    usuario.ativo = False

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return usuario
