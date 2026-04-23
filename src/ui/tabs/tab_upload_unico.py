from __future__ import annotations

from typing import Any

import streamlit as st

from src.config import ALLOWED_IMAGE_EXTENSIONS
from src.services.analysis_service import gerar_hash_bytes, registrar_analise
from src.services.inference_service import analisar_arquivo
from src.services.pdf_service import gerar_pdf_analise
from src.ui.charts import montar_grafico
from src.ui.components import exibir_detalhamento
from src.utils.formatters import (
    nome_modelo_amigavel,
    obter_modelo_mais_confiante,
    resumir_votacao,
)


def _ler_bytes_arquivo(uploaded_file: Any) -> bytes:
    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)

    if hasattr(uploaded_file, "getvalue"):
        conteudo = uploaded_file.getvalue()
    else:
        conteudo = uploaded_file.read()

    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)

    return conteudo


def _resetar_resultado_se_nova_imagem(arquivo: Any) -> None:
    identificador_imagem = (arquivo.name, arquivo.size)

    if st.session_state.ultima_imagem_unica != identificador_imagem:
        st.session_state.resultado_unico = None
        st.session_state.ultima_imagem_unica = identificador_imagem


def _render_preview_imagem(arquivo: Any) -> None:
    st.markdown('<div class="section-title">🖼️ Imagem analisada</div>', unsafe_allow_html=True)
    st.markdown('<div class="thumb-box">', unsafe_allow_html=True)
    st.image(arquivo, width="stretch")
    st.markdown("</div>", unsafe_allow_html=True)


def _executar_analise(arquivo: Any) -> None:
    st.session_state.processando_unico = True

    try:
        conteudo = _ler_bytes_arquivo(arquivo)
        hash_arquivo = gerar_hash_bytes(conteudo)

        with st.spinner("🔍 Analisando imagem..."):
            st.session_state.resultado_unico = analisar_arquivo(arquivo)

            if (
                st.session_state.resultado_unico is not None
                and "erro" not in st.session_state.resultado_unico
            ):
                registrar_analise(
                    nome_arquivo=arquivo.name,
                    resultados=st.session_state.resultado_unico,
                    hash_arquivo=hash_arquivo,
                )
    finally:
        st.session_state.processando_unico = False


def _render_resultado_validado(arquivo: Any, resultados: dict[str, Any]) -> None:
    resumo = resumir_votacao(resultados)
    melhor_modelo, melhor_resultado = obter_modelo_mais_confiante(resultados)

    col_res, col_modelo = st.columns(2)

    with col_res:
        cor_borda = "#C62828" if resumo["classe_final"] == "Rachado" else "#2E7D32"
        st.markdown(f"""
        <div class="info-card" style="border-left: 6px solid {cor_borda};">
            <div>
                <div class="card-title">Resultado Final (votação)</div>
                <div class="card-value">{resumo['texto_final']}</div>
                <div class="card-sub">{resumo['observacao']}</div>
            </div>
            <div class="card-sub">
                Votos → Rachado: {resumo['votos_rachado']} | Não Rachado: {resumo['votos_nao_rachado']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_modelo:
        cor_borda = "#C62828" if melhor_resultado["classe"] == "Rachado" else "#2E7D32"
        st.markdown(f"""
        <div class="info-card" style="border-left: 6px solid {cor_borda};">
            <div>
                <div class="card-title">Modelo mais confiante</div>
                <div class="card-value">{nome_modelo_amigavel(melhor_modelo)}</div>
                <div class="card-sub">
                    Classe: {melhor_resultado['classe']}<br>
                    Confiança: {melhor_resultado['probabilidade']:.1%}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">📊 Comparação entre Modelos</div>', unsafe_allow_html=True)
    st.plotly_chart(montar_grafico(resultados), width="stretch")

    st.markdown('<div class="section-title">🔎 Detalhamento</div>', unsafe_allow_html=True)
    exibir_detalhamento(resultados)

    st.download_button(
        label="📄 Baixar relatório em PDF",
        data=gerar_pdf_analise(nome_arquivo=arquivo.name, resultados=resultados),
        file_name=f"analise_{arquivo.name}.pdf",
        mime="application/pdf",
        width="stretch",
        key="download_pdf_unico",
    )


def _render_resultado(arquivo: Any, resultados: dict[str, Any]) -> None:
    st.markdown('<div class="section-title">🧠 Resultado da Análise</div>', unsafe_allow_html=True)

    if "erro" in resultados:
        st.error("❌ Imagem inválida para análise")
        st.caption(resultados["erro"])
        return

    _render_resultado_validado(arquivo, resultados)


def render_tab_upload_unico() -> None:
    arquivo = st.file_uploader(
        "📤 Enviar imagem",
        type=ALLOWED_IMAGE_EXTENSIONS,
        key="upload_unico",
    )

    if arquivo is None:
        return

    _resetar_resultado_se_nova_imagem(arquivo)
    _render_preview_imagem(arquivo)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        clicar = st.button(
            "🚀 Analisar imagem",
            width="stretch",
            key="botao_unico",
            disabled=st.session_state.processando_unico,
        )

    if clicar and not st.session_state.processando_unico:
        _executar_analise(arquivo)

    if st.session_state.resultado_unico is None:
        st.info("👆 Clique em 'Analisar imagem' para processar a imagem.")
        return

    _render_resultado(arquivo, st.session_state.resultado_unico)