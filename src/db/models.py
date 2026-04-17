from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


def agora_brasil():
    return datetime.now(ZoneInfo("America/Sao_Paulo"))


class Analise(Base):
    __tablename__ = "analises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome_arquivo: Mapped[str] = mapped_column(String(255), nullable=False)
    data_analise: Mapped[datetime] = mapped_column(DateTime, default=agora_brasil, nullable=False)
    resultado_final: Mapped[str] = mapped_column(String(100), nullable=False)
    modelo_mais_confiante: Mapped[str] = mapped_column(String(100), nullable=False)
    confianca: Mapped[float] = mapped_column(Float, nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    detalhes_modelos: Mapped[str | None] = mapped_column(Text, nullable=True)