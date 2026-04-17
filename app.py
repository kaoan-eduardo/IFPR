import streamlit as st

from src.config import ALLOWED_IMAGE_EXTENSIONS, APP_ICON, APP_LAYOUT, APP_TITLE
from src.services.inference_service import analisar_arquivo
from src.ui.charts import montar_grafico
from src.ui.components import (
    exibir_detalhamento,
    exibir_detalhamento_lote,
    preparar_thumbnail,
)
from src.ui.header import renderizar_header
from src.ui.styles import aplicar_estilos
from src.utils.formatters import (
    nome_modelo_amigavel,
    obter_modelo_mais_confiante,
    resumir_votacao,
)

# ===============================
# CONFIG
# ===============================
st.set_page_config(
    page_title=APP_TITLE,
    layout=APP_LAYOUT,
    page_icon=APP_ICON
)

# ===============================
# SESSION STATE
# ===============================
if "resultado_unico" not in st.session_state:
    st.session_state.resultado_unico = None

if "ultima_imagem_unica" not in st.session_state:
    st.session_state.ultima_imagem_unica = None

if "resultado_lote" not in st.session_state:
    st.session_state.resultado_lote = None

if "ultimo_lote" not in st.session_state:
    st.session_state.ultimo_lote = None

# ===============================
# UI BASE
# ===============================
aplicar_estilos()
renderizar_header()

# ===============================
# TABS
# ===============================
tab1, tab2 = st.tabs(["📷 Upload único", "🗂️ Múltiplas imagens"])

# ===============================
# ABA 1 - UPLOAD ÚNICO
# ===============================
with tab1:
    arquivo = st.file_uploader(
        "📤 Enviar imagem",
        type=ALLOWED_IMAGE_EXTENSIONS,
        key="upload_unico"
    )

    if arquivo is not None:
        identificador_imagem = (arquivo.name, arquivo.size)

        if st.session_state.ultima_imagem_unica != identificador_imagem:
            st.session_state.resultado_unico = None
            st.session_state.ultima_imagem_unica = identificador_imagem

        st.markdown('<div class="section-title">🖼️ Imagem analisada</div>', unsafe_allow_html=True)
        st.markdown('<div class="thumb-box">', unsafe_allow_html=True)
        st.image(arquivo, width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            clicar = st.button("🚀 Analisar imagem", width="stretch", key="botao_unico")

        if clicar:
            with st.spinner("🔍 Analisando imagem..."):
                st.session_state.resultado_unico = analisar_arquivo(arquivo)

        if st.session_state.resultado_unico is None:
            st.info("👆 Clique em 'Analisar imagem' para processar a imagem.")

        if st.session_state.resultado_unico is not None:
            resultados = st.session_state.resultado_unico

            st.markdown('<div class="section-title">🧠 Resultado da Análise</div>', unsafe_allow_html=True)

            if "erro" in resultados:
                st.error("❌ Imagem inválida para análise")
                st.caption(resultados["erro"])
            else:
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
                fig = montar_grafico(resultados)
                st.plotly_chart(fig, width="stretch")

                st.markdown('<div class="section-title">🔎 Detalhamento</div>', unsafe_allow_html=True)
                exibir_detalhamento(resultados)

# ===============================
# ABA 2 - MÚLTIPLAS IMAGENS
# ===============================
with tab2:
    arquivos = st.file_uploader(
        "📤 Enviar imagens",
        type=ALLOWED_IMAGE_EXTENSIONS,
        accept_multiple_files=True,
        key="upload_lote"
    )

    if arquivos:
        identificador_lote = tuple((a.name, a.size) for a in arquivos)

        if st.session_state.ultimo_lote != identificador_lote:
            st.session_state.resultado_lote = None
            st.session_state.ultimo_lote = identificador_lote

        st.markdown(
            f'<div class="section-title">🗂️ {len(arquivos)} imagem(ns) selecionada(s)</div>',
            unsafe_allow_html=True
        )

        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            clicar_lote = st.button("🚀 Analisar lote", width="stretch", key="botao_lote")

        if clicar_lote:
            resultados_lote = []

            with st.spinner("🔍 Analisando lote de imagens..."):
                for arquivo_lote in arquivos:
                    resultados = analisar_arquivo(arquivo_lote)

                    if "erro" in resultados:
                        resultados_lote.append({
                            "arquivo": arquivo_lote,
                            "nome": arquivo_lote.name,
                            "resultado_final": "Imagem inválida",
                            "melhor_modelo": "-",
                            "classe_melhor_modelo": "-",
                            "confianca": 0.0,
                            "resultados_completos": resultados
                        })
                    else:
                        resumo = resumir_votacao(resultados)
                        melhor_modelo, melhor_resultado = obter_modelo_mais_confiante(resultados)

                        resultados_lote.append({
                            "arquivo": arquivo_lote,
                            "nome": arquivo_lote.name,
                            "resultado_final": resumo["texto_final"],
                            "melhor_modelo": nome_modelo_amigavel(melhor_modelo),
                            "classe_melhor_modelo": melhor_resultado["classe"],
                            "confianca": melhor_resultado["probabilidade"],
                            "resultados_completos": resultados
                        })

            st.session_state.resultado_lote = resultados_lote

        if st.session_state.resultado_lote is None:
            st.info("👆 Clique em 'Analisar lote' para processar as imagens enviadas.")

        if st.session_state.resultado_lote is not None:
            resultados_lote = st.session_state.resultado_lote

            total = len(resultados_lote)
            com_rachadura = sum(
                1 for item in resultados_lote
                if item["resultado_final"] == "Pavimento com rachaduras detectadas"
            )
            bom_estado = sum(
                1 for item in resultados_lote
                if item["resultado_final"] == "Pavimento em bom estado"
            )
            invalidas = sum(
                1 for item in resultados_lote
                if item["resultado_final"] == "Imagem inválida"
            )

            st.markdown('<div class="section-title">📋 Resumo do lote</div>', unsafe_allow_html=True)

            m1, m2, m3, m4 = st.columns(4)

            with m1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Total de imagens</div>
                    <div class="metric-value">{total}</div>
                </div>
                """, unsafe_allow_html=True)

            with m2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Com rachaduras</div>
                    <div class="metric-value">{com_rachadura}</div>
                </div>
                """, unsafe_allow_html=True)

            with m3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Em bom estado</div>
                    <div class="metric-value">{bom_estado}</div>
                </div>
                """, unsafe_allow_html=True)

            with m4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Inválidas</div>
                    <div class="metric-value">{invalidas}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('<div class="section-title">🖼️ Galeria de resultados</div>', unsafe_allow_html=True)
            galerias = st.columns(3, gap="small")

            for i, item in enumerate(resultados_lote):
                coluna = galerias[i % 3]

                with coluna:
                    thumb = preparar_thumbnail(item["arquivo"], tamanho=(420, 240))

                    with st.container(border=True):
                        st.markdown(f'<div class="file-name">{item["nome"]}</div>', unsafe_allow_html=True)
                        st.image(thumb, width="stretch")

                        if item["resultado_final"] == "Pavimento com rachaduras detectadas":
                            st.markdown('<div class="badge-bad">Com rachaduras</div>', unsafe_allow_html=True)
                        elif item["resultado_final"] == "Pavimento em bom estado":
                            st.markdown('<div class="badge-good">Bom estado</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="badge-invalid">Imagem inválida</div>', unsafe_allow_html=True)

                        st.markdown(f"""
                        <div class="mini-info">
                            <b>Modelo mais confiante:</b> {item['melhor_modelo']}<br>
                            <b>Classe:</b> {item['classe_melhor_modelo']}<br>
                            <b>Confiança:</b> {item['confianca']:.1%}
                        </div>
                        """, unsafe_allow_html=True)

                        with st.expander("Ver detalhamento"):
                            if "erro" in item["resultados_completos"]:
                                st.error("❌ Imagem inválida para análise")
                                st.caption(item["resultados_completos"]["erro"])
                            else:
                                exibir_detalhamento_lote(item["resultados_completos"])