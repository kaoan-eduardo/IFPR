from __future__ import annotations

import io
import json
import zipfile
from datetime import datetime
from types import SimpleNamespace

import pandas as pd

from src.ui.tabs import (
    tab_avaliacao_modelo,
    tab_dashboard,
    tab_multiplas_imagens,
    tab_upload_unico,
)


def test_formatar_nome_modelo_avaliacao():
    assert tab_avaliacao_modelo._formatar_nome_modelo("random_forest") == "Random Forest"
    assert tab_avaliacao_modelo._formatar_nome_modelo("decision_tree") == "Árvore de Decisão"
    assert tab_avaliacao_modelo._formatar_nome_modelo("modelo_x") == "modelo_x"


def test_padronizar_modelos_altera_coluna_modelo():
    df_resumo = pd.DataFrame({"Modelo": ["random_forest"]})
    df_folds = pd.DataFrame({"Modelo": ["svm"]})
    df_matriz = pd.DataFrame({"Modelo": ["knn"]})

    r, f, m = tab_avaliacao_modelo._padronizar_modelos(df_resumo, df_folds, df_matriz)

    assert r.loc[0, "Modelo"] == "Random Forest"
    assert f.loc[0, "Modelo"] == "SVM"
    assert m.loc[0, "Modelo"] == "K-Nearest Neighbors"


def test_formatar_tabela_resumo_converte_percentuais():
    df = pd.DataFrame(
        {
            "Modelo": ["Random Forest"],
            "Accuracy Média": [0.91234],
            "Precision Média": [0.8],
            "Recall Média": [None],
        }
    )

    resultado = tab_avaliacao_modelo._formatar_tabela_resumo(df)

    assert resultado.loc[0, "Accuracy Média"] == "91.23%"
    assert resultado.loc[0, "Precision Média"] == "80.00%"
    assert resultado.loc[0, "Recall Média"] == "-"


def test_montar_dataframe_analises():
    analises = [
        SimpleNamespace(
            id=1,
            nome_arquivo="img.jpg",
            data_analise=datetime(2026, 1, 2, 10, 30),
            resultado_final="Pavimento em bom estado",
            modelo_mais_confiante="random_forest",
            confianca=0.91,
            observacao="ok",
            detalhes_modelos=None,
        )
    ]

    df = tab_dashboard._montar_dataframe_analises(analises)

    assert len(df) == 1
    assert df.loc[0, "nome_arquivo"] == "img.jpg"
    assert df.loc[0, "modelo_mais_confiante_nome"] == "🌲 Random Forest"
    assert df.loc[0, "dia"] == "02/01/2026"


def test_extrair_probabilidades_modelos_ignora_json_invalido():
    df = pd.DataFrame(
        {
            "detalhes_modelos": [
                "{json inválido",
                None,
                json.dumps({"svm": {"erro": "falhou"}}),
            ]
        }
    )

    resultado = tab_dashboard._extrair_probabilidades_modelos(df)

    assert resultado.empty
    assert list(resultado.columns) == ["Modelo", "Confianca"]


def test_extrair_probabilidades_modelos_retorna_dataframe():
    detalhes = {
        "random_forest": {"probabilidade": 0.9},
        "svm": {"probabilidade": 0.7},
        "knn": {"erro": "falhou"},
    }

    df = pd.DataFrame({"detalhes_modelos": [json.dumps(detalhes)]})

    resultado = tab_dashboard._extrair_probabilidades_modelos(df)

    assert len(resultado) == 2
    assert set(resultado["Modelo"]) == {"🌲 Random Forest", "📈 SVM"}
    assert resultado["Confianca"].tolist() == [0.9, 0.7]


def test_calcular_metricas_dashboard():
    detalhes = {
        "random_forest": {"probabilidade": 0.9},
        "svm": {"probabilidade": 0.5},
    }

    df = pd.DataFrame(
        {
            "resultado_final": [
                tab_dashboard.RESULTADO_RACHADO,
                tab_dashboard.RESULTADO_BOM,
            ],
            "detalhes_modelos": [
                json.dumps(detalhes),
                json.dumps(detalhes),
            ],
        }
    )

    metricas = tab_dashboard._calcular_metricas_dashboard(df)

    assert metricas["total_analises"] == 2
    assert metricas["qtd_rachado"] == 1
    assert metricas["qtd_bom"] == 1
    assert metricas["perc_rachado"] == 50.0
    assert metricas["perc_bom"] == 50.0
    assert metricas["confianca_media"] == 0.7
    assert metricas["taxa_incerteza"] == 50.0


def test_extrair_confianca_media_todos_modelos():
    detalhes = {
        "random_forest": {"probabilidade": 0.9},
        "svm": {"probabilidade": 0.7},
    }

    df = pd.DataFrame({"detalhes_modelos": [json.dumps(detalhes)]})

    resultado = tab_dashboard._extrair_confianca_media_todos_modelos(df)

    assert len(resultado) == 2
    assert resultado.iloc[0]["Confianca"] == 0.9


def test_listar_arquivos_zip_retorna_imagens_validas():
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("pasta/imagem.jpg", b"fake")
        zf.writestr("pasta/texto.txt", b"texto")

    buffer.seek(0)

    arquivos, erro = tab_multiplas_imagens._listar_arquivos_zip(buffer)

    assert erro is None
    assert len(arquivos) == 1
    assert arquivos[0]["name"] == "imagem.jpg"
    assert arquivos[0]["full_name"] == "pasta/imagem.jpg"


def test_listar_arquivos_zip_retorna_erro_para_zip_invalido():
    buffer = io.BytesIO(b"nao eh zip")

    arquivos, erro = tab_multiplas_imagens._listar_arquivos_zip(buffer)

    assert arquivos == []
    assert erro == "Arquivo ZIP inválido ou corrompido."


def test_converter_arquivo_zip_para_buffer():
    arquivo_dict = {
        "name": "teste.jpg",
        "bytes": b"abc",
    }

    buffer = tab_multiplas_imagens._converter_arquivo_zip_para_buffer(arquivo_dict)

    assert buffer.getvalue() == b"abc"
    assert buffer.name == "teste.jpg"


def test_gerar_excel_lote_retorna_bytesio():
    resultados = [
        {
            "nome": "img.jpg",
            "resultado_final": tab_multiplas_imagens.RESULTADO_BOM,
            "melhor_modelo": "Random Forest",
            "classe_melhor_modelo": "Não Rachado",
            "confianca": 0.91,
        }
    ]

    arquivo = tab_multiplas_imagens._gerar_excel_lote(resultados)

    assert isinstance(arquivo, io.BytesIO)
    assert arquivo.getbuffer().nbytes > 0


def test_gerar_pdf_lote_retorna_bytesio():
    resultados = [
        {
            "nome": "img.jpg",
            "resultado_final": tab_multiplas_imagens.RESULTADO_BOM,
            "melhor_modelo": "Random Forest",
            "classe_melhor_modelo": "Não Rachado",
            "confianca": 0.91,
        }
    ]

    arquivo = tab_multiplas_imagens._gerar_pdf_lote(resultados)

    assert isinstance(arquivo, io.BytesIO)
    assert arquivo.getvalue().startswith(b"%PDF")


def test_montar_resultado_erro_lote():
    resultado = tab_multiplas_imagens._montar_resultado_erro("arquivo", "img.jpg")

    assert resultado["arquivo"] == "arquivo"
    assert resultado["nome"] == "img.jpg"
    assert resultado["resultado_final"] == "Imagem inválida"
    assert resultado["detalhamento_disponivel"] is False


def test_ler_bytes_arquivo_upload_unico():
    arquivo = io.BytesIO(b"abc")
    arquivo.name = "teste.jpg"

    resultado = tab_upload_unico._ler_bytes_arquivo(arquivo)

    assert resultado == b"abc"
    assert arquivo.tell() == 0