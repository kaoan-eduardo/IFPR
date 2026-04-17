import json

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import ALLOWED_IMAGE_EXTENSIONS, APP_ICON, APP_LAYOUT, APP_TITLE
from src.db.repository import listar_analises
from src.db.session import SessionLocal
from src.services.analysis_service import registrar_analise
from src.services.inference_service import analisar_arquivo
from src.ui.charts import montar_grafico
from src.ui.components import exibir_detalhamento, preparar_thumbnail
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
tab1, tab2, tab3 = st.tabs(["📷 Upload único", "🗂️ Múltiplas imagens", "📚 Histórico"])

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

                if (
                    st.session_state.resultado_unico is not None
                    and "erro" not in st.session_state.resultado_unico
                ):
                    registrar_analise(
                        nome_arquivo=arquivo.name,
                        resultados=st.session_state.resultado_unico
                    )

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

                        # salva cada análise válida do lote no banco
                        registrar_analise(
                            nome_arquivo=arquivo_lote.name,
                            resultados=resultados
                        )

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
                                exibir_detalhamento(item["resultados_completos"])

# ===============================
# ABA 3 - HISTÓRICO / DASHBOARD
# ===============================
with tab3:
    topo1, topo2 = st.columns([4, 1])

    with topo1:
        st.markdown('<div class="section-title">📚 Dashboard de Análises</div>', unsafe_allow_html=True)

    with topo2:
        if st.button("🔄 Atualizar dashboard", width="stretch", key="botao_atualizar_dashboard"):
            st.rerun()

    db = SessionLocal()

    try:
        analises = listar_analises(db)
    finally:
        db.close()

    if not analises:
        st.info("Nenhuma análise encontrada ainda.")
    else:
        registros = []

        for analise in analises:
            registros.append({
                "id": analise.id,
                "nome_arquivo": analise.nome_arquivo,
                "data_analise": analise.data_analise,
                "resultado_final": analise.resultado_final,
                "modelo_mais_confiante": analise.modelo_mais_confiante,
                "modelo_mais_confiante_nome": nome_modelo_amigavel(analise.modelo_mais_confiante),
                "confianca": analise.confianca,
                "observacao": analise.observacao,
                "detalhes_modelos": analise.detalhes_modelos,
            })

        df = pd.DataFrame(registros)

        df["data_analise"] = pd.to_datetime(df["data_analise"])
        df["dia"] = df["data_analise"].dt.strftime("%d/%m/%Y")

        total_analises = len(df)
        qtd_rachado = (df["resultado_final"] == "Pavimento com rachaduras detectadas").sum()
        qtd_bom = (df["resultado_final"] == "Pavimento em bom estado").sum()

        perc_rachado = (qtd_rachado / total_analises * 100) if total_analises else 0
        perc_bom = (qtd_bom / total_analises * 100) if total_analises else 0

        confianca_media = df["confianca"].mean() if total_analises else 0
        confianca_baixa = (df["confianca"] < 0.60).sum()
        taxa_incerteza = (confianca_baixa / total_analises * 100) if total_analises else 0

        st.markdown('<div class="section-title">📊 Visão Geral</div>', unsafe_allow_html=True)

        m1, m2, m3, m4, m5 = st.columns(5)

        with m1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total de análises</div>
                <div class="metric-value">{total_analises}</div>
            </div>
            """, unsafe_allow_html=True)

        with m2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Com rachaduras</div>
                <div class="metric-value">{qtd_rachado}</div>
                <div class="card-sub">{perc_rachado:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with m3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Bom estado</div>
                <div class="metric-value">{qtd_bom}</div>
                <div class="card-sub">{perc_bom:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with m4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Confiança média</div>
                <div class="metric-value">{confianca_media:.1%}</div>
            </div>
            """, unsafe_allow_html=True)

        with m5:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Taxa de incerteza</div>
                <div class="metric-value">{taxa_incerteza:.1f}%</div>
                <div class="card-sub">Confiança &lt; 60%</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="section-title">📈 Indicadores Visuais</div>', unsafe_allow_html=True)

        g1, g2 = st.columns(2)

        with g1:
            df_resultados = pd.DataFrame({
                "Categoria": ["Com rachaduras", "Bom estado"],
                "Quantidade": [qtd_rachado, qtd_bom]
            })

            fig_pizza = px.pie(
                df_resultados,
                names="Categoria",
                values="Quantidade",
                hole=0.45
            )
            fig_pizza.update_layout(
                margin=dict(l=10, r=10, t=30, b=10),
                height=360
            )
            st.plotly_chart(fig_pizza, width="stretch")

        with g2:
            df_modelos = (
                df["modelo_mais_confiante_nome"]
                .value_counts()
                .reset_index()
            )
            df_modelos.columns = ["Modelo", "Quantidade"]

            fig_modelos = px.bar(
                df_modelos,
                x="Modelo",
                y="Quantidade",
                text="Quantidade"
            )
            fig_modelos.update_layout(
                xaxis_title="Modelo mais confiante",
                yaxis_title="Quantidade",
                margin=dict(l=10, r=10, t=30, b=40),
                height=360
            )
            st.plotly_chart(fig_modelos, width="stretch")

        df_tempo = (
            df.groupby("dia")
            .size()
            .reset_index(name="Quantidade")
        )

        fig_tempo = px.line(
            df_tempo,
            x="dia",
            y="Quantidade",
            markers=True
        )
        fig_tempo.update_layout(
            xaxis_title="Data",
            yaxis_title="Número de análises",
            margin=dict(l=10, r=10, t=30, b=40),
            height=360
        )
        st.plotly_chart(fig_tempo, width="stretch")

        st.markdown('<div class="section-title">🗂️ Histórico Detalhado</div>', unsafe_allow_html=True)

        for analise in analises:
            eh_rachado = "rachaduras" in analise.resultado_final.lower()

            badge_html = (
                '<div class="badge-bad">Com rachaduras</div>'
                if eh_rachado
                else '<div class="badge-good">Bom estado</div>'
            )

            with st.container(border=True):
                st.markdown(
                    f'<div class="file-name">{analise.nome_arquivo}</div>',
                    unsafe_allow_html=True
                )

                st.markdown(badge_html, unsafe_allow_html=True)

                col1, col2, col3 = st.columns([2.2, 1.3, 1.2])

                with col1:
                    st.markdown(
                        f'<div class="card-value">{analise.resultado_final}</div>',
                        unsafe_allow_html=True
                    )

                    if analise.observacao:
                        st.markdown(
                            f'<div class="card-sub">{analise.observacao}</div>',
                            unsafe_allow_html=True
                        )

                with col2:
                    st.markdown(
                        f"""
                        <div class="card-sub">
                            <b>Modelo:</b><br>
                            {nome_modelo_amigavel(analise.modelo_mais_confiante)}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col3:
                    st.markdown(
                        f"""
                        <div class="card-sub">
                            <b>Confiança:</b><br>
                            {analise.confianca:.1%}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                data_formatada = analise.data_analise.strftime("%d/%m/%Y %H:%M")

                st.markdown(
                    f'<div class="card-sub"><b>Data:</b> {data_formatada}</div>',
                    unsafe_allow_html=True
                )

                if analise.detalhes_modelos:
                    with st.expander("Ver modelos analisados"):
                        try:
                            detalhes = json.loads(analise.detalhes_modelos)

                            for nome_modelo, info in detalhes.items():
                                st.markdown(
                                    f"""
                                    <div class="detail-card">
                                        <div class="card-title">{nome_modelo_amigavel(nome_modelo)}</div>
                                        <div class="card-sub">
                                            <b>Classe:</b> {info.get("classe", "-")}<br>
                                            <b>Confiança:</b> {info.get("probabilidade", 0):.1%}
                                        </div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                        except Exception:
                            st.warning("Erro ao carregar os detalhes dos modelos.")

                st.markdown("")