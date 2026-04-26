from __future__ import annotations

from src.utils import formatters


def test_nome_modelo_amigavel_retorna_nome_conhecido():
    assert formatters.nome_modelo_amigavel("random_forest") == "🌲 Random Forest"


def test_nome_modelo_amigavel_retorna_original_quando_desconhecido():
    assert formatters.nome_modelo_amigavel("modelo_x") == "modelo_x"


def test_resumir_votacao_retorna_rachado_quando_maioria_rachado():
    resultados = {
        "m1": {"classe": "Rachado"},
        "m2": {"classe": "Rachado"},
        "m3": {"classe": "Não Rachado"},
    }

    resumo = formatters.resumir_votacao(resultados)

    assert resumo["classe_final"] == "Rachado"
    assert resumo["texto_final"] == "Pavimento com rachaduras detectadas"
    assert resumo["votos_rachado"] == 2
    assert resumo["votos_nao_rachado"] == 1


def test_resumir_votacao_ignora_modelos_com_erro():
    resultados = {
        "m1": {"classe": "Não Rachado"},
        "m2": {"erro": "falhou"},
    }

    resumo = formatters.resumir_votacao(resultados)

    assert resumo["classe_final"] == "Não Rachado"
    assert resumo["votos_rachado"] == 0
    assert resumo["votos_nao_rachado"] == 1


def test_obter_modelo_mais_confiante_retorna_maior_probabilidade():
    resultados = {
        "m1": {"classe": "Rachado", "probabilidade": 0.7},
        "m2": {"classe": "Não Rachado", "probabilidade": 0.9},
        "m3": {"erro": "falhou"},
    }

    nome, dados = formatters.obter_modelo_mais_confiante(resultados)

    assert nome == "m2"
    assert dados["probabilidade"] == 0.9


def test_obter_modelo_mais_confiante_retorna_none_sem_validos():
    nome, dados = formatters.obter_modelo_mais_confiante({"m1": {"erro": "falhou"}})

    assert nome is None
    assert dados is None