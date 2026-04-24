from __future__ import annotations

import streamlit as st


def render_tab_glossario() -> None:
    st.markdown("## 📖 Glossário do Sistema")

    st.markdown("""
    Esta seção apresenta os principais conceitos e métricas utilizadas na avaliação
    dos modelos de Machine Learning aplicados na detecção de fissuras em pavimentos.
    """)

    # ===============================
    # CONCEITOS GERAIS
    # ===============================

    with st.expander("🧠 Machine Learning"):
        st.markdown("""
        Área da Inteligência Artificial que permite que algoritmos aprendam padrões
        a partir de dados. Neste projeto, é utilizada para classificar imagens de
        pavimentos como "Bom" ou "Rachado".
        """)

    with st.expander("📊 Cross Validation (Validação Cruzada)"):
        st.markdown("""
        Técnica utilizada para avaliar o modelo de forma mais robusta.

        O dataset é dividido em várias partes (folds), e o modelo é treinado e testado
        várias vezes, garantindo que os resultados não dependam de uma única divisão
        de dados.
        """)

    with st.expander("🔢 Fold"):
        st.markdown("""
        Cada divisão do dataset na validação cruzada.

        Exemplo: em uma validação com 10 folds, o modelo será treinado e testado
        10 vezes, cada vez usando uma parte diferente dos dados como teste.
        """)

    # ===============================
    # MÉTRICAS PRINCIPAIS
    # ===============================

    with st.expander("📈 Accuracy (Acurácia)"):
        st.markdown("""
        Mede a proporção total de previsões corretas.

        Fórmula:
        (TP + TN) / (TP + TN + FP + FN)

        Onde:
        - TP: Verdadeiro Positivo
        - TN: Verdadeiro Negativo
        - FP: Falso Positivo
        - FN: Falso Negativo

        É uma métrica geral, mas pode ser enganosa em datasets desbalanceados.
        """)

    with st.expander("🎯 Precision (Precisão)"):
        st.markdown("""
        Mede quantas previsões positivas estão corretas.

        Fórmula:
        TP / (TP + FP)

        Interpretação:
        Entre todas as imagens classificadas como "Rachado",
        quantas realmente são rachadas.
        """)

    with st.expander("🔁 Recall (Sensibilidade)"):
        st.markdown("""
        Mede a capacidade do modelo de encontrar todos os casos positivos.

        Fórmula:
        TP / (TP + FN)

        Interpretação:
        Entre todas as imagens realmente rachadas,
        quantas o modelo conseguiu identificar.
        """)

    with st.expander("⚖️ F1-score"):
        st.markdown("""
        Média harmônica entre Precision e Recall.

        Fórmula:
        2 * (Precision * Recall) / (Precision + Recall)

        Interpretação:
        Mede o equilíbrio entre precisão e recall.
        Muito útil quando há desbalanceamento entre classes.
        """)

    with st.expander("🛡️ Specificity (Especificidade)"):
        st.markdown("""
        Mede a capacidade do modelo de identificar corretamente os casos negativos.

        Fórmula:
        TN / (TN + FP)

        Interpretação:
        Entre todas as imagens "Boas", quantas foram corretamente classificadas.
        """)

    # ===============================
    # ESTATÍSTICA
    # ===============================

    with st.expander("📊 Média"):
        st.markdown("""
        Valor médio das métricas ao longo dos folds da validação cruzada.

        Representa o desempenho geral do modelo.
        """)

    with st.expander("📉 Desvio Padrão"):
        st.markdown("""
        Mede a variação das métricas entre os folds.

        - Baixo desvio → modelo estável
        - Alto desvio → modelo inconsistente

        É essencial para avaliar a confiabilidade do modelo.
        """)

    # ===============================
    # MATRIZ DE CONFUSÃO
    # ===============================

    with st.expander("🧩 Matriz de Confusão"):
        st.markdown("""
        Tabela que mostra os acertos e erros do modelo.

        É composta por:
        """)

        st.markdown("""
        - **TP (True Positive)**: Rachado → Rachado  
        - **TN (True Negative)**: Bom → Bom  
        - **FP (False Positive)**: Bom → Rachado  
        - **FN (False Negative)**: Rachado → Bom  
        """)

        st.markdown("""
        Interpretação:
        - FP: erro crítico (alarme falso)
        - FN: erro crítico (falha em detectar rachadura)
        """)

    # ===============================
    # MODELOS
    # ===============================

    with st.expander("🌳 Random Forest"):
        st.markdown("""
        Modelo baseado em várias árvores de decisão.
        Cada árvore vota, e o resultado final é definido por maioria.
        """)

    with st.expander("🌲 Árvore de Decisão"):
        st.markdown("""
        Modelo baseado em regras simples de decisão.
        Fácil de interpretar, mas pode sofrer overfitting.
        """)

    with st.expander("📍 K-Nearest Neighbors (KNN)"):
        st.markdown("""
        Classifica uma imagem com base nos exemplos mais próximos no espaço de features.
        """)

    with st.expander("📈 SVM (Support Vector Machine)"):
        st.markdown("""
        Modelo que tenta separar as classes usando um hiperplano ótimo.
        Muito eficiente para dados bem definidos.
        """)