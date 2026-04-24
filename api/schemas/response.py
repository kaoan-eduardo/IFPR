from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class AnaliseResponse(BaseModel):
    status: str
    id_analise: int
    arquivo: str
    hash_arquivo: str
    data_analise: str
    resultado_final: str
    observacao: str | None
    modelo_mais_confiante: str
    confianca: float
    modelos: dict[str, Any]


class AnaliseHistoricoResponse(BaseModel):
    id_analise: int
    arquivo: str
    hash_arquivo: str
    data_analise: str
    resultado_final: str
    observacao: str | None
    modelo_mais_confiante: str
    confianca: float
    modelos: dict[str, Any] | None