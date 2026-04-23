from __future__ import annotations

from io import BytesIO
from typing import Any

import streamlit as st
from PIL import Image, ImageOps

from src.utils.formatters import nome_modelo_amigavel


def _ler_bytes_arquivo(uploaded_file: Any) -> bytes:
    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)

    if hasattr(uploaded_file, "getvalue"):
        conteudo = uploaded_file.getvalue()
    elif hasattr(uploaded_file, "read"):
        conteudo = uploaded_file.read()
    else:
        raise ValueError("Arquivo enviado em formato inválido.")

    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)

    if not isinstance(conteudo, bytes):
        raise ValueError("Não foi possível ler o conteúdo do arquivo.")

    return conteudo


def preparar_thumbnail(uploaded_file: Any, tamanho: tuple[int, int] = (420, 240)) -> Image.Image:
    conteudo = _ler_bytes_arquivo(uploaded_file)

    imagem = Image.open(BytesIO(conteudo)).convert("RGB")
    thumb = ImageOps.fit(
        imagem,
        tamanho,
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )
    return thumb


def _exibir_detalhamento_base(
    resultados: dict[str, dict[str, Any]],
    *,
    classe_card: str,
    classe_title: str,
    classe_value: str,
    classe_sub: str,
    gap: str = "medium",
) -> None:
    col1, col2 = st.columns(2, gap=gap)

    for i, (modelo, info) in enumerate(resultados.items()):
        nome = nome_modelo_amigavel(modelo)
        container = col1 if i % 2 == 0 else col2

        classe = info.get("classe", "-")
        confianca = float(info.get("probabilidade", 0.0))
        erro = info.get("erro")

        with container:
            st.markdown(
                f"""
                <div class="{classe_card}">
                    <div class="{classe_title}">{nome}</div>
                    <div class="{classe_value}">{classe}</div>
                    <div class="{classe_sub}">Confiança: {confianca:.1%}</div>
                    {"<div class='" + classe_sub + "'>Erro: " + str(erro) + "</div>" if erro else ""}
                </div>
                """,
                unsafe_allow_html=True,
            )


def exibir_detalhamento(resultados: dict[str, dict[str, Any]]) -> None:
    _exibir_detalhamento_base(
        resultados,
        classe_card="detail-card",
        classe_title="card-title",
        classe_value="card-value",
        classe_sub="card-sub",
    )


def exibir_detalhamento_lote(resultados: dict[str, dict[str, Any]]) -> None:
    _exibir_detalhamento_base(
        resultados,
        classe_card="detail-card-lote",
        classe_title="card-title-lote",
        classe_value="card-value-lote",
        classe_sub="card-sub-lote",
        gap="small",
    )