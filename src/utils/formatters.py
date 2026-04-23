from __future__ import annotations

from typing import Any

from src.config import (
    CLASS_CRACKED,
    CLASS_NOT_CRACKED,
    MODEL_DISPLAY_NAMES,
)


def nome_modelo_amigavel(nome_modelo: str) -> str:
    """
    Retorna o nome amigável do modelo.
    """
    return MODEL_DISPLAY_NAMES.get(nome_modelo, nome_modelo)


def resumir_votacao(resultados: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """
    Realiza a votação entre os modelos válidos.
    Ignora modelos com erro.
    """
    votos = [
        resultado.get("classe")
        for resultado in resultados.values()
        if isinstance(resultado, dict)
        and "erro" not in resultado
        and resultado.get("classe") in {CLASS_CRACKED, CLASS_NOT_CRACKED}
    ]

    rachado = votos.count(CLASS_CRACKED)
    nao_rachado = votos.count(CLASS_NOT_CRACKED)

    if rachado > nao_rachado:
        classe_final = CLASS_CRACKED
        texto_final = "Pavimento com rachaduras detectadas"
        observacao = "Recomenda-se inspeção ou manutenção."
    else:
        classe_final = CLASS_NOT_CRACKED
        texto_final = "Pavimento em bom estado"
        observacao = "Nenhuma anomalia significativa detectada."

    return {
        "classe_final": classe_final,
        "texto_final": texto_final,
        "votos_rachado": rachado,
        "votos_nao_rachado": nao_rachado,
        "observacao": observacao,
    }


def obter_modelo_mais_confiante(
    resultados: dict[str, dict[str, Any]]
) -> tuple[str | None, dict[str, Any] | None]:
    """
    Retorna o modelo válido com maior confiança.
    Ignora modelos com erro.
    """
    resultados_validos = {
        nome: dados
        for nome, dados in resultados.items()
        if isinstance(dados, dict)
        and "erro" not in dados
        and "probabilidade" in dados
    }

    if not resultados_validos:
        return None, None

    return max(
        resultados_validos.items(),
        key=lambda item: float(item[1].get("probabilidade", 0.0)),
    )