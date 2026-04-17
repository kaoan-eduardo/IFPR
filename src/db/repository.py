from sqlalchemy.orm import Session

from src.db.models import Analise


def salvar_analise(
    db: Session,
    nome_arquivo: str,
    resultado_final: str,
    modelo_mais_confiante: str,
    confianca: float,
    observacao: str | None = None,
    detalhes_modelos: str | None = None,
) -> Analise:
    nova_analise = Analise(
        nome_arquivo=nome_arquivo,
        resultado_final=resultado_final,
        modelo_mais_confiante=modelo_mais_confiante,
        confianca=confianca,
        observacao=observacao,
        detalhes_modelos=detalhes_modelos,
    )

    db.add(nova_analise)
    db.commit()
    db.refresh(nova_analise)

    return nova_analise


def listar_analises(db: Session) -> list[Analise]:
    return db.query(Analise).order_by(Analise.data_analise.desc()).all()