from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


BRAZIL_TIMEZONE = ZoneInfo("America/Sao_Paulo")


def agora_brasil() -> datetime:
    return datetime.now(BRAZIL_TIMEZONE)


class Analise(Base):
    __tablename__ = "analises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    hash_arquivo: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)

    nome_arquivo: Mapped[str] = mapped_column(String(255), nullable=False)
    data_analise: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=agora_brasil,
        nullable=False,
    )
    resultado_final: Mapped[str] = mapped_column(String(100), nullable=False)
    modelo_mais_confiante: Mapped[str] = mapped_column(String(100), nullable=False)
    confianca: Mapped[float] = mapped_column(Float, nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    detalhes_modelos: Mapped[str | None] = mapped_column(Text, nullable=True)