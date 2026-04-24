from __future__ import annotations

import json
import logging
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from src.db.repository import listar_analises
from src.db.session import SessionLocal
from src.services.export_service import exportar_excel
from src.services.pdf_dashboard_service import gerar_pdf_dashboard
from src.services.pdf_service import gerar_pdf_analise
from src.ui.components import exibir_detalhamento
from src.utils.formatters import nome_modelo_amigavel


logger = logging.getLogger(__name__)

RESULTADO_RACHADO = "Pavimento com rachaduras detectadas"
RESULTADO_BOM = "Pavimento em bom estado"
LIMIAR_BAIXA_CONFIANCA = 0.60


def _carregar_analises() -> list[Any]:
    db = SessionLocal()
    try:
        return listar_analises(db)
    finally:
        db.close()


def _montar_dataframe_analises(analises: list[Any]) -> pd.DataFrame:
    registros = [
        {
            "id": analise.id,
            "nome_arquivo": analise.nome_arquivo,
            "data_analise": analise.data_analise,
            "resultado_final": analise.resultado_final,
            "modelo_mais_confiante": analise.modelo_mais_confiante,
            "modelo_mais_confiante_nome": nome_modelo_amigavel(analise.modelo_mais_confiante),
            "confianca": analise.confianca,
            "observacao": analise.observacao,
            "detalhes_modelos": analise.detalhes_modelos,
        }
        for analise in analises
    ]

    df = pd.DataFrame(registros)
    df["data_analise"] = pd.to_datetime(df["data_analise"])
    df["dia"] = df["data_analise"].dt.strftime("%d/%m/%Y")
    return df


def _extrair_probabilidades_modelos(df: pd.DataFrame) -> pd.DataFrame:
    linhas_modelos: list[dict[str, Any]] = []

    for _, row in df.iterrows():
        detalhes_json = row.get("detalhes_modelos")

        if not detalhes_json:
            continue

        try:
            detalhes = json.loads(detalhes_json)
        except json.JSONDecodeError as erro:
            logger.warning("JSON inválido em detalhes_modelos: %s", erro)
            continue
        except TypeError as erro:
            logger.warning("Tipo inválido em detalhes_modelos: %s", erro)
            continue

        if not isinstance(detalhes, dict):
            logger.warning("detalhes_modelos não é um dicionário válido.")
            continue

        for nome_modelo, info in detalhes.items():
            if not isinstance(info, dict):
                continue

            if "erro" in info:
                continue

            probabilidade = info.get("probabilidade")

            if probabilidade is None:
                continue

            try:
                confianca = float(probabilidade)
            except (TypeError, ValueError) as erro:
                logger.warning(
                    "Probabilidade inválida para o modelo %s: %s",
                    nome_modelo,
                    erro,
                )
                continue

            linhas_modelos.append(
                {
                    "Modelo": nome_modelo_amigavel(nome_modelo),
                    "Confianca": confianca,
                }
            )

    if not linhas_modelos:
        return pd.DataFrame(columns=["Modelo", "Confianca"])

    return pd.DataFrame(linhas_modelos)


def _calcular_metricas_dashboard(df: pd.DataFrame) -> dict[str, float | int]:
    total_analises = len(df)
    qtd_rachado = int((df["resultado_final"] == RESULTADO_RACHADO).sum())
    qtd_bom = int((df["resultado_final"] == RESULTADO_BOM).sum())

    perc_rachado = (qtd_rachado / total_analises * 100) if total_analises else 0.0
    perc_bom = (qtd_bom / total_analises * 100) if total_analises else 0.0

    df_probabilidades = _extrair_probabilidades_modelos(df)

    if df_probabilidades.empty:
        confianca_media = 0.0
        taxa_incerteza = 0.0
    else:
        confianca_media = float(df_probabilidades["Confianca"].mean())
        qtd_baixa_confianca = int(
            (df_probabilidades["Confianca"] < LIMIAR_BAIXA_CONFIANCA).sum()
        )
        taxa_incerteza = qtd_baixa_confianca / len(df_probabilidades) * 100

    return {
        "total_analises": total_analises,
        "qtd_rachado": qtd_rachado,
        "qtd_bom": qtd_bom,
        "perc_rachado": perc_rachado,
        "perc_bom": perc_bom,
        "confianca_media": confianca_media,
        "taxa_incerteza": taxa_incerteza,
    }


def _extrair_confianca_media_todos_modelos(df: pd.DataFrame) -> pd.DataFrame:
    df_modelos = _extrair_probabilidades_modelos(df)

    if df_modelos.empty:
        return pd.DataFrame(columns=["Modelo", "Confianca"])

    return (
        df_modelos.groupby("Modelo", as_index=False)["Confianca"]
        .mean()
        .sort_values("Confianca", ascending=False)
    )


def _render_topo() -> None:
    topo1, topo2 = st.columns([4, 1])

    with topo1:
        st.markdown(
            '<div class="section-title">📚 Dashboard de Análises</div>',
            unsafe_allow_html=True,
        )

    with topo2:
        if st.button(
            "🔄 Atualizar dashboard",
            width="stretch",
            key="botao_atualizar_dashboard",
        ):
            st.rerun()


def _render_metric_card(titulo: str, valor: str | int, subtitulo: str = "&nbsp;") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div>
                <div class="metric-title">{titulo}</div>
                <div class="metric-value">{valor}</div>
            </div>
            <div class="metric-sub">{subtitulo}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_visao_geral(metricas: dict[str, float | int]) -> None:
    st.markdown(
        '<div class="section-title">📊 Visão Geral</div>',
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        _render_metric_card("Total de análises", metricas["total_analises"])

    with m2:
        _render_metric_card(
            "Com rachaduras",
            metricas["qtd_rachado"],
            f"{metricas['perc_rachado']:.1f}%",
        )

    with m3:
        _render_metric_card(
            "Bom estado",
            metricas["qtd_bom"],
            f"{metricas['perc_bom']:.1f}%",
        )

    with m4:
        _render_metric_card(
            "Confiança média",
            f"{metricas['confianca_media']:.1%}",
        )

    with m5:
        _render_metric_card(
            "Taxa de incerteza",
            f"{metricas['taxa_incerteza']:.1f}%",
            f"Confiança &lt; {LIMIAR_BAIXA_CONFIANCA:.0%}",
        )


def _render_exportacao_dashboard(
    df: pd.DataFrame,
    metricas: dict[str, float | int],
) -> None:
    st.markdown(
        '<div class="section-title">📦 Exportação do Dashboard</div>',
        unsafe_allow_html=True,
    )

    col_export1, col_export2 = st.columns(2)

    with col_export1:
        st.download_button(
            label="📊 Exportar dashboard para Excel",
            data=exportar_excel(df),
            file_name="dashboard_analises.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
            key="download_dashboard_excel",
        )

    with col_export2:
        st.download_button(
            label="📄 Exportar dashboard para PDF",
            data=gerar_pdf_dashboard(
                total=int(metricas["total_analises"]),
                rachado=int(metricas["qtd_rachado"]),
                bom=int(metricas["qtd_bom"]),
                confianca_media=float(metricas["confianca_media"]),
                taxa_incerteza=float(metricas["taxa_incerteza"]),
            ),
            file_name="dashboard_analises.pdf",
            mime="application/pdf",
            width="stretch",
            key="download_dashboard_pdf",
        )


def _render_indicadores_visuais(
    df: pd.DataFrame,
    metricas: dict[str, float | int],
) -> None:
    st.markdown(
        '<div class="section-title">📈 Indicadores Visuais</div>',
        unsafe_allow_html=True,
    )

    g1, g2 = st.columns(2)

    with g1:
        df_resultados = pd.DataFrame(
            {
                "Resultado": ["Com rachaduras", "Bom estado"],
                "Percentual": [
                    metricas["qtd_rachado"] / metricas["total_analises"]
                    if metricas["total_analises"]
                    else 0,
                    metricas["qtd_bom"] / metricas["total_analises"]
                    if metricas["total_analises"]
                    else 0,
                ],
            }
        )

        max_valor_esquerda = float(df_resultados["Percentual"].max())
        limite_superior_esquerda = min(1.2, max_valor_esquerda + 0.10)

        fig_resultados = px.bar(
            df_resultados,
            x="Resultado",
            y="Percentual",
            text="Percentual",
        )

        fig_resultados.update_traces(
            texttemplate="%{text:.1%}",
            textposition="outside",
        )

        fig_resultados.update_layout(
            xaxis_title="Resultado",
            yaxis_title="Percentual",
            yaxis=dict(range=[0, limite_superior_esquerda], tickformat=".0%"),
            margin=dict(l=10, r=10, t=30, b=40),
            height=360,
        )

        st.plotly_chart(fig_resultados, width="stretch")

    with g2:
        df_media_modelos = _extrair_confianca_media_todos_modelos(df)

        if df_media_modelos.empty:
            st.info("Não há dados suficientes para calcular a confiança média dos modelos.")
        else:
            max_valor_direita = float(df_media_modelos["Confianca"].max())
            limite_superior_direita = min(1.2, max_valor_direita + 0.10)

            fig_modelos = px.bar(
                df_media_modelos,
                x="Modelo",
                y="Confianca",
                text="Confianca",
            )

            fig_modelos.update_traces(
                texttemplate="%{text:.1%}",
                textposition="outside",
            )

            fig_modelos.update_layout(
                xaxis_title="Modelo",
                yaxis_title="Confiança média",
                yaxis=dict(range=[0, limite_superior_direita], tickformat=".0%"),
                margin=dict(l=10, r=10, t=30, b=40),
                height=360,
            )

            st.plotly_chart(fig_modelos, width="stretch")

    df_tempo = df.groupby("dia").size().reset_index(name="Quantidade")

    fig_tempo = px.line(
        df_tempo,
        x="dia",
        y="Quantidade",
        markers=True,
    )

    fig_tempo.update_layout(
        xaxis_title="Data",
        yaxis_title="Número de análises",
        margin=dict(l=10, r=10, t=30, b=40),
        height=360,
    )

    st.plotly_chart(fig_tempo, width="stretch")


def _render_historico_detalhado(analises: list[Any]) -> None:
    st.markdown(
        '<div class="section-title">🗂️ Histórico Detalhado</div>',
        unsafe_allow_html=True,
    )

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
                unsafe_allow_html=True,
            )
            st.markdown(badge_html, unsafe_allow_html=True)

            col1, col2, col3 = st.columns([2.2, 1.3, 1.2])

            with col1:
                st.markdown(
                    f'<div class="card-value">{analise.resultado_final}</div>',
                    unsafe_allow_html=True,
                )

                if analise.observacao:
                    st.markdown(
                        f'<div class="card-sub">{analise.observacao}</div>',
                        unsafe_allow_html=True,
                    )

            with col2:
                st.markdown(
                    f"""
                    <div class="card-sub">
                        <b>Modelo:</b><br>
                        {nome_modelo_amigavel(analise.modelo_mais_confiante)}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col3:
                st.markdown(
                    f"""
                    <div class="card-sub">
                        <b>Confiança:</b><br>
                        {analise.confianca:.1%}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            data_formatada = analise.data_analise.strftime("%d/%m/%Y %H:%M")

            st.markdown(
                f'<div class="card-sub"><b>Data:</b> {data_formatada}</div>',
                unsafe_allow_html=True,
            )

            if analise.detalhes_modelos:
                try:
                    detalhes = json.loads(analise.detalhes_modelos)
                except json.JSONDecodeError as erro:
                    logger.warning(
                        "JSON inválido no histórico da análise %s: %s",
                        analise.id,
                        erro,
                    )
                    st.warning("Não foi possível carregar os detalhes desta análise.")
                    continue
                except TypeError as erro:
                    logger.warning(
                        "Tipo inválido nos detalhes da análise %s: %s",
                        analise.id,
                        erro,
                    )
                    st.warning("Não foi possível carregar os detalhes desta análise.")
                    continue

                if not isinstance(detalhes, dict):
                    logger.warning(
                        "Detalhes da análise %s não estão em formato de dicionário.",
                        analise.id,
                    )
                    st.warning("Não foi possível carregar os detalhes desta análise.")
                    continue

                st.download_button(
                    label="📄 Baixar relatório em PDF",
                    data=gerar_pdf_analise(
                        nome_arquivo=analise.nome_arquivo,
                        resultados=detalhes,
                    ),
                    file_name=f"analise_{analise.nome_arquivo}.pdf",
                    mime="application/pdf",
                    width="stretch",
                    key=f"download_pdf_hist_{analise.id}",
                )

                with st.expander("Ver modelos analisados"):
                    exibir_detalhamento(detalhes)


def render_tab_dashboard() -> None:
    _render_topo()

    analises = _carregar_analises()

    if not analises:
        st.info("Nenhuma análise encontrada ainda.")
        return

    df = _montar_dataframe_analises(analises)
    metricas = _calcular_metricas_dashboard(df)

    _render_visao_geral(metricas)
    _render_exportacao_dashboard(df, metricas)
    _render_indicadores_visuais(df, metricas)
    _render_historico_detalhado(analises)