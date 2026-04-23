from __future__ import annotations

import hashlib
import json
from typing import Any

from src.db.repository import salvar_analise
from src.db.session import SessionLocal
from src.utils.formatters import (
    nome_modelo_amigavel,
    obter_modelo_mais_confiante,
    resumir_votacao,
)


def gerar_hash_bytes(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()


def registrar_analise(
    nome_arquivo: str,
    resultados: dict[str, Any],
    hash_arquivo: str,
) -> Any | None:
    """
    Salva no banco o resultado final de uma análise válida.
    Retorna a análise salva ou existente.
    """
    if "erro" in resultados:
        return None

    resumo = resumir_votacao(resultados)
    melhor_modelo, melhor_resultado = obter_modelo_mais_confiante(resultados)

    if melhor_modelo is None or melhor_resultado is None:
        return None

    db = SessionLocal()
    try:
        analise = salvar_analise(
            db=db,
            hash_arquivo=hash_arquivo,
            nome_arquivo=nome_arquivo,
            resultado_final=resumo["texto_final"],
            modelo_mais_confiante=nome_modelo_amigavel(melhor_modelo),
            confianca=float(melhor_resultado["probabilidade"]),
            observacao=resumo["observacao"],
            detalhes_modelos=json.dumps(resultados, ensure_ascii=False),
        )
        return analise
    finally:
        db.close()