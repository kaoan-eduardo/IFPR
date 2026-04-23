from __future__ import annotations

import streamlit as st
import pandas as pd

from src.services.evaluation_service import carregar_dados_avaliacao
from src.ui.evaluation_charts import grafico_metricas, grafico_folds, heatmap_matriz


def _formatar_nome_modelo(modelo: str) -> str:
    mapa = {
        "random_forest": "Random Forest",
        "decision_tree": "Árvore de Decisão",
        "knn": "K-Nearest Neighbors",
        "svm": "SVM",
    }
    return mapa.get(str(modelo).strip().lower(), str(modelo))


def _padronizar_modelos(
    df_resumo: pd.DataFrame,
    df_folds: pd.DataFrame,
    df_matriz: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    for df in (df_resumo, df_folds, df_matriz):
        if "Modelo" in df.columns:
            df["Modelo"] = df["Modelo"].apply(_formatar_nome_modelo)

    return df_resumo, df_folds, df_matriz


def _formatar_tabela_resumo(df_resumo: pd.DataFrame) -> pd.DataFrame:
    df_formatado = df_resumo.copy()

    colunas_percentuais = [
        "Accuracy Média",
        "Accuracy Desvio",
        "Precision Média",
        "Precision Desvio",
        "Recall Média",
        "Recall Desvio",
        "F1-score Média",
        "F1-score Desvio",
        "Specificity Média",
        "Specificity Desvio",
    ]

    for coluna in colunas_percentuais:
        if coluna in df_formatado.columns:
            df_formatado[coluna] = df_formatado[coluna].apply(
                lambda x: f"{x:.2%}" if pd.notna(x) else "-"
            )

    return df_formatado


def _render_melhor_modelo(df_resumo: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">🏆 Melhor Modelo</div>', unsafe_allow_html=True)

    melhor = df_resumo.sort_values(by="Accuracy Média", ascending=False).iloc[0]

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown(f"""
        <div class="info-card" style="border-left: 6px solid #2E7D32;">
            <div>
                <div class="card-title">Modelo</div>
                <div class="card-value">{melhor['Modelo']}</div>
                <div class="card-sub">Melhor accuracy média</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown(f"""
        <div class="info-card" style="border-left: 6px solid #1565C0;">
            <div>
                <div class="card-title">Accuracy Média</div>
                <div class="card-value">{melhor['Accuracy Média']:.2%}</div>
                <div class="card-sub">Desempenho médio</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_c:
        st.markdown(f"""
        <div class="info-card" style="border-left: 6px solid #6A1B9A;">
            <div>
                <div class="card-title">F1-score Médio</div>
                <div class="card-value">{melhor['F1-score Média']:.2%}</div>
                <div class="card-sub">Equilíbrio entre precisão e recall</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_tabela_metricas(df_resumo: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">📋 Tabela de Métricas</div>', unsafe_allow_html=True)
    st.dataframe(_formatar_tabela_resumo(df_resumo), width="stretch")


def _render_comparacao_modelos(df_resumo: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">📊 Comparação entre Modelos</div>', unsafe_allow_html=True)
    st.plotly_chart(grafico_metricas(df_resumo), width="stretch")


def _render_folds(df_folds: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">📈 Desempenho por Fold</div>', unsafe_allow_html=True)

    metricas_disponiveis = [
        coluna
        for coluna in ["Accuracy", "Precision", "Recall", "F1-score", "Specificity"]
        if coluna in df_folds.columns
    ]

    metrica_escolhida = st.selectbox(
        "Selecione a métrica dos folds",
        metricas_disponiveis,
        key="select_metrica_folds",
    )

    st.plotly_chart(
        grafico_folds(df_folds, metrica_escolhida),
        width="stretch",
    )


def _render_matriz_confusao(df_matriz: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">🧩 Matriz de Confusão</div>', unsafe_allow_html=True)

    modelos_disponiveis = df_matriz["Modelo"].unique().tolist()
    modelo_sel = st.selectbox(
        "Selecione o modelo",
        modelos_disponiveis,
        key="select_matriz_modelo",
    )

    linha = df_matriz[df_matriz["Modelo"] == modelo_sel].iloc[0]

    tn = int(linha["TN (bom->bom)"])
    fp = int(linha["FP (bom->ruim)"])
    fn = int(linha["FN (ruim->bom)"])
    tp = int(linha["TP (ruim->ruim)"])

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div>
                <div class="metric-title">TN</div>
                <div class="metric-value">{tn}</div>
            </div>
            <div class="metric-sub">Bom → Bom</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div>
                <div class="metric-title">FP</div>
                <div class="metric-value">{fp}</div>
            </div>
            <div class="metric-sub">Bom → Rachado</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div>
                <div class="metric-title">FN</div>
                <div class="metric-value">{fn}</div>
            </div>
            <div class="metric-sub">Rachado → Bom</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div>
                <div class="metric-title">TP</div>
                <div class="metric-value">{tp}</div>
            </div>
            <div class="metric-sub">Rachado → Rachado</div>
        </div>
        """, unsafe_allow_html=True)

    st.plotly_chart(
        heatmap_matriz(
            tn=tn,
            fp=fp,
            fn=fn,
            tp=tp,
            titulo=f"Matriz de Confusão - {modelo_sel}",
        ),
        width="stretch",
    )


def render_tab_avaliacao_modelo() -> None:
    st.markdown('<div class="section-title">✅ Avaliação do Modelo</div>', unsafe_allow_html=True)

    df_resumo, df_folds, df_matriz = carregar_dados_avaliacao()

    if df_resumo is None or df_folds is None or df_matriz is None:
        st.warning("Arquivo de métricas não encontrado em results/metricas_cross_validation.xlsx")
        return

    df_resumo, df_folds, df_matriz = _padronizar_modelos(df_resumo, df_folds, df_matriz)

    _render_melhor_modelo(df_resumo)
    _render_tabela_metricas(df_resumo)
    _render_comparacao_modelos(df_resumo)
    _render_folds(df_folds)
    _render_matriz_confusao(df_matriz)