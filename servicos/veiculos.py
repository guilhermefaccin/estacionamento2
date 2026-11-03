from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from entidades.models import Veiculo
from schemas.veiculos import VeiculoCriar, VeiculoAtualizar


def cadastrar_veiculo(dados: VeiculoCriar, db: Session) -> Veiculo:
    veiculo = Veiculo.model_validate(
        dados.model_dump(),
        update={"id_usuario_cadastro": 1}
    )

    db.add(veiculo)
    db.commit()
    db.refresh(veiculo)

    return veiculo


def listar_veiculos(db: Session) -> list[Veiculo]:
    comando = select(Veiculo).where(Veiculo.ativo.is_(True))
    return list(db.exec(comando).all())


def buscar_veiculo_por_id(
    id_veiculo: int,
    db: Session
) -> Veiculo | None:
    comando = select(Veiculo).where(
        Veiculo.id_veiculo == id_veiculo
    )
    return db.exec(comando).first()


def atualizar_veiculo(
    id_veiculo: int,
    dados: VeiculoAtualizar,
    db: Session
) -> Veiculo | None:
    veiculo = buscar_veiculo_por_id(id_veiculo, db)

    if veiculo is None or not veiculo.ativo:
        return None

    atualizacoes = dados.model_dump()

    for campo, valor in atualizacoes.items():
        setattr(veiculo, campo, valor)

    veiculo.id_usuario_alteracao = 1

    db.add(veiculo)
    db.commit()
    db.refresh(veiculo)

    return veiculo


def desativar_veiculo(
    id_veiculo: int,
    db: Session
) -> Veiculo | None:
    veiculo = buscar_veiculo_por_id(id_veiculo, db)

    if veiculo is None or not veiculo.ativo:
        return None

    veiculo.ativo = False
    veiculo.id_usuario_alteracao = 1

    db.add(veiculo)
    db.commit()
    db.refresh(veiculo)

    return veiculo
