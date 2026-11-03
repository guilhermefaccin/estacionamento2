from fastapi import HTTPException
from sqlmodel import Session, select

from entidades.models import Cliente, Marca, Veiculo
from schemas.veiculos import VeiculoAtualizar, VeiculoCriar


def cadastrar_veiculo(dados: VeiculoCriar, db: Session, id_usuario: int) -> Veiculo:
    validar_referencias(dados, db)
    veiculo = Veiculo.model_validate(
        dados.model_dump(), update={"id_usuario_cadastro": id_usuario}
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
    db: Session,
) -> Veiculo | None:
    comando = select(Veiculo).where(Veiculo.id_veiculo == id_veiculo)
    return db.exec(comando).first()


def atualizar_veiculo(
    id_veiculo: int,
    dados: VeiculoAtualizar,
    db: Session,
    id_usuario: int,
) -> Veiculo | None:
    veiculo = buscar_veiculo_por_id(id_veiculo, db)

    if veiculo is None or not veiculo.ativo:
        return None

    validar_referencias(dados, db)

    atualizacoes = dados.model_dump()

    for campo, valor in atualizacoes.items():
        setattr(veiculo, campo, valor)

    veiculo.id_usuario_alteracao = id_usuario

    db.add(veiculo)
    db.commit()
    db.refresh(veiculo)

    return veiculo


def validar_referencias(dados, db: Session):
    for modelo, identificador in ((Cliente, dados.id_cliente), (Marca, dados.id_marca)):
        registro = db.get(modelo, identificador)
        if registro is None or not registro.ativo:
            raise HTTPException(
                status_code=404, detail="Cliente ou marca não encontrado ou inativo"
            )


def desativar_veiculo(
    id_veiculo: int,
    db: Session,
    id_usuario: int,
) -> Veiculo | None:
    veiculo = buscar_veiculo_por_id(id_veiculo, db)

    if veiculo is None or not veiculo.ativo:
        return None

    veiculo.ativo = False
    veiculo.id_usuario_alteracao = id_usuario

    db.add(veiculo)
    db.commit()
    db.refresh(veiculo)

    return veiculo
