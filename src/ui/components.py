from io import BytesIO

import streamlit as st
from PIL import Image, ImageOps

from src.utils.formatters import nome_modelo_amigavel


def preparar_thumbnail(uploaded_file, tamanho=(420, 240)):
    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)

    conteudo = uploaded_file.read()

    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)

    imagem = Image.open(BytesIO(conteudo)).convert("RGB")
    thumb = ImageOps.fit(
        imagem,
        tamanho,
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5)
    )
    return thumb


def exibir_detalhamento(resultados: dict) -> None:
    col1, col2 = st.columns(2)

    for i, (modelo, r) in enumerate(resultados.items()):
        nome = nome_modelo_amigavel(modelo)
        container = col1 if i % 2 == 0 else col2

        with container:
            st.markdown(f"""
            <div class="detail-card">
                <div class="card-title">{nome}</div>
                <div class="card-value">{r['classe']}</div>
                <div class="card-sub">Confiança: {r['probabilidade']:.1%}</div>
            </div>
            """, unsafe_allow_html=True)


def exibir_detalhamento_lote(resultados: dict) -> None:
    """
    Versão compacta para usar dentro do expander do lote.
    """
    col1, col2 = st.columns(2, gap="small")

    for i, (modelo, r) in enumerate(resultados.items()):
        nome = nome_modelo_amigavel(modelo)
        container = col1 if i % 2 == 0 else col2

        with container:
            st.markdown(f"""
            <div class="detail-card-lote">
                <div class="card-title-lote">{nome}</div>
                <div class="card-value-lote">{r['classe']}</div>
                <div class="card-sub-lote">Confiança: {r['probabilidade']:.1%}</div>
            </div>
            """, unsafe_allow_html=True)