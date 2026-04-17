import plotly.graph_objects as go

from src.utils.formatters import nome_modelo_amigavel


def montar_grafico(resultados: dict):
    melhor_modelo = max(resultados.items(), key=lambda x: x[1]["probabilidade"])[0]

    labels = []
    valores = []
    cores = []

    for modelo, r in resultados.items():
        labels.append(nome_modelo_amigavel(modelo))
        valores.append(r["probabilidade"])

        if modelo == melhor_modelo:
            cores.append("#00E676")
        elif modelo == "random_forest":
            cores.append("#1B5E20")
        elif modelo == "decision_tree":
            cores.append("#4CAF50")
        elif modelo == "knn":
            cores.append("#2196F3")
        elif modelo == "svm":
            cores.append("#9C27B0")
        else:
            cores.append("#888888")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels,
        y=valores,
        marker_color=cores,
        text=[f"{v:.1%}" for v in valores],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Confiança: %{y:.2%}<extra></extra>"
    ))

    fig.update_layout(
        yaxis=dict(range=[0, 1], title="Confiança"),
        xaxis_tickangle=-25,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=10, r=10, t=20, b=40),
        height=360
    )

    return fig