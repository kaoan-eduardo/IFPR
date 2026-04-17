import json

from src.db.repository import salvar_analise
from src.db.session import SessionLocal
from src.utils.formatters import obter_modelo_mais_confiante, resumir_votacao


def registrar_analise(nome_arquivo: str, resultados: dict):
    """
    Salva no banco o resultado final de uma análise.
    """
    if "erro" in resultados:
        return None

    resumo = resumir_votacao(resultados)
    melhor_modelo, melhor_resultado = obter_modelo_mais_confiante(resultados)

    db = SessionLocal()
    try:
        analise = salvar_analise(
            db=db,
            nome_arquivo=nome_arquivo,
            resultado_final=resumo["texto_final"],
            modelo_mais_confiante=melhor_modelo,
            confianca=melhor_resultado["probabilidade"],
            observacao=resumo["observacao"],
            detalhes_modelos=json.dumps(resultados, ensure_ascii=False),
        )
        return analise
    finally:
        db.close()