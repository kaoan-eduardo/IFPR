from __future__ import annotations

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from src.db.models import Analise


def buscar_analise_por_hash(db: Session, hash_arquivo: str) -> Analise | None:
    return db.query(Analise).filter(Analise.hash_arquivo == hash_arquivo).first()


def salvar_analise(
    db: Session,
    hash_arquivo: str,
    nome_arquivo: str,
    resultado_final: str,
    modelo_mais_confiante: str,
    confianca: float,
    observacao: str | None = None,
    detalhes_modelos: str | None = None,
) -> Analise:
    nova_analise = Analise(
        hash_arquivo=hash_arquivo,
        nome_arquivo=nome_arquivo,
        resultado_final=resultado_final,
        modelo_mais_confiante=modelo_mais_confiante,
        confianca=confianca,
        observacao=observacao,
        detalhes_modelos=detalhes_modelos,
    )

    try:
        db.add(nova_analise)
        db.commit()
        db.refresh(nova_analise)
        return nova_analise

    except SQLAlchemyError:
        db.rollback()
        raise


def listar_analises(db: Session) -> list[Analise]:
    return db.query(Analise).order_by(Analise.data_analise.desc()).all()