from datetime import datetime
from decimal import Decimal
from math import ceil

from fastapi import HTTPException
from sqlmodel import Session, select

from entidades.models import (
    Estacionamento,
    ModalidadeTarifa,
    StatusEstacionamento,
    StatusVaga,
    Tarifa,
    Usuario,
    Vaga,
    Veiculo,
)
from schemas.estacionamentos import EstacionamentoEntrada


def registrar_entrada(
    db: Session,
    dados: EstacionamentoEntrada,
    id_usuario: int,
) -> Estacionamento:
    veiculo = db.exec(
        select(Veiculo).where(Veiculo.id_veiculo == dados.id_veiculo).with_for_update()
    ).first()

    if veiculo is None or not veiculo.ativo:
        raise HTTPException(
            status_code=404,
            detail="Veículo não encontrado ou inativo",
        )

    vaga = db.exec(
        select(Vaga).where(Vaga.id_vaga == dados.id_vaga).with_for_update()
    ).first()

    if vaga is None or not vaga.ativo:
        raise HTTPException(
            status_code=404,
            detail="Vaga não encontrada ou inativa",
        )

    if vaga.status != StatusVaga.LIVRE:
        raise HTTPException(
            status_code=409,
            detail="A vaga não está livre",
        )

    if vaga.tipo_uso != "rotativa":
        raise HTTPException(
            status_code=400,
            detail="Esta vaga é destinada a mensalistas",
        )

    entrada_aberta = db.exec(
        select(Estacionamento).where(
            Estacionamento.id_veiculo == dados.id_veiculo,
            Estacionamento.status == StatusEstacionamento.ABERTO,
        )
    ).first()

    if entrada_aberta:
        raise HTTPException(
            status_code=409,
            detail="Este veículo já possui um estacionamento aberto",
        )

    entrada = datetime.now()
    tarifa = db.get(Tarifa, dados.id_tarifa) if dados.id_tarifa else None
    if tarifa is None or not tarifa.ativo:
        raise HTTPException(
            status_code=400,
            detail="Selecione uma tarifa ativa para registrar a entrada",
        )
    if tarifa.modalidade != ModalidadeTarifa.HORISTA or not tarifa.intervalo_minutos:
        raise HTTPException(
            status_code=400,
            detail="A entrada rotativa exige tarifa horista com intervalo válido",
        )
    if entrada < tarifa.data_inicio_vigencia or (
        tarifa.data_fim_vigencia is not None and entrada > tarifa.data_fim_vigencia
    ):
        raise HTTPException(
            status_code=400, detail="A tarifa não está vigente para esta entrada"
        )
    if dados.id_contrato is not None:
        raise HTTPException(
            status_code=400, detail="A entrada rotativa não utiliza contrato mensal"
        )

    estacionamento = Estacionamento(
        id_veiculo=dados.id_veiculo,
        id_vaga=dados.id_vaga,
        id_tarifa=dados.id_tarifa,
        id_contrato=dados.id_contrato,
        id_usuario_entrada=id_usuario,
        status=StatusEstacionamento.ABERTO,
        data_hora_entrada=entrada,
    )

    vaga.status = StatusVaga.OCUPADA

    db.add(estacionamento)
    db.add(vaga)
    db.commit()
    db.refresh(estacionamento)

    return estacionamento


def listar_abertos(db: Session) -> list[Estacionamento]:
    consulta = select(Estacionamento).where(
        Estacionamento.status == StatusEstacionamento.ABERTO
    )
    return list(db.exec(consulta).all())


def buscar_por_id(
    db: Session,
    id_estacionamento: int,
) -> Estacionamento | None:
    return db.get(Estacionamento, id_estacionamento)


def registrar_saida(
    db: Session,
    id_estacionamento: int,
    id_usuario: int,
) -> Estacionamento:
    # Busca o estacionamento
    estacionamento = db.exec(
        select(Estacionamento)
        .where(Estacionamento.id_estacionamento == id_estacionamento)
        .with_for_update()
    ).first()

    if estacionamento is None:
        raise HTTPException(
            status_code=404,
            detail="Estacionamento não encontrado",
        )

    if estacionamento.status != StatusEstacionamento.ABERTO:
        raise HTTPException(
            status_code=409,
            detail="Este estacionamento já foi finalizado ou cancelado",
        )

    # Confere o usuário responsável pela saída
    usuario = db.get(Usuario, id_usuario)

    if usuario is None or not usuario.ativo:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado ou inativo",
        )

    # Busca a vaga
    vaga = db.get(Vaga, estacionamento.id_vaga)

    if vaga is None:
        raise HTTPException(
            status_code=404,
            detail="Vaga não encontrada",
        )

    if vaga.status != StatusVaga.OCUPADA:
        raise HTTPException(
            status_code=409,
            detail="A vaga não está marcada como ocupada",
        )

    # A entrada precisa ter uma tarifa associada
    if estacionamento.id_tarifa is None:
        raise HTTPException(
            status_code=400,
            detail="O estacionamento não possui tarifa associada",
        )

    tarifa = db.get(Tarifa, estacionamento.id_tarifa)

    if tarifa is None:
        raise HTTPException(
            status_code=404,
            detail="Tarifa não encontrada",
        )

    # Confere modalidade, situação e vigência da tarifa
    entrada = estacionamento.data_hora_entrada

    if tarifa.modalidade != ModalidadeTarifa.HORISTA:
        raise HTTPException(
            status_code=400,
            detail="A saída automática por hora exige uma tarifa horista",
        )

    if entrada < tarifa.data_inicio_vigencia:
        raise HTTPException(
            status_code=400,
            detail="A tarifa ainda não estava vigente na entrada",
        )

    if tarifa.data_fim_vigencia is not None and entrada > tarifa.data_fim_vigencia:
        raise HTTPException(
            status_code=400,
            detail="A tarifa não estava vigente na entrada",
        )

    if tarifa.intervalo_minutos is None or tarifa.intervalo_minutos <= 0:
        raise HTTPException(
            status_code=400,
            detail="O intervalo da tarifa é inválido",
        )

    # Calcula a cobrança por intervalo iniciado
    saida = datetime.now().replace(tzinfo=None)
    segundos = max(
        0,
        (saida - entrada).total_seconds(),
    )

    segundos_por_intervalo = tarifa.intervalo_minutos * 60
    quantidade_intervalos = max(
        1,
        ceil(segundos / segundos_por_intervalo),
    )

    valor = (tarifa.valor * Decimal(quantidade_intervalos)).quantize(Decimal("0.01"))

    # Atualiza a saída e libera a vaga
    estacionamento.data_hora_saida = saida
    estacionamento.id_usuario_saida = id_usuario
    estacionamento.valor_calculado = valor
    estacionamento.status = StatusEstacionamento.FINALIZADO
    vaga.status = StatusVaga.LIVRE

    try:
        db.add(estacionamento)
        db.add(vaga)
        db.commit()
        db.refresh(estacionamento)
    except Exception:
        db.rollback()
        raise

    return estacionamento
