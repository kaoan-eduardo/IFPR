from __future__ import annotations

from datetime import datetime
from io import BytesIO
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from src.utils.formatters import (
    nome_modelo_amigavel,
    obter_modelo_mais_confiante,
    resumir_votacao,
)


def gerar_pdf_analise(nome_arquivo: str, resultados: dict[str, Any]) -> BytesIO:
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    conteudo = []

    conteudo.append(Paragraph("Relatório de Análise de Pavimento", styles["Title"]))
    conteudo.append(Spacer(1, 12))

    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    conteudo.append(Paragraph(f"<b>Arquivo:</b> {nome_arquivo}", styles["Normal"]))
    conteudo.append(Paragraph(f"<b>Data da análise:</b> {data_atual}", styles["Normal"]))
    conteudo.append(Spacer(1, 12))

    if "erro" in resultados:
        conteudo.append(Paragraph("<b>Resultado:</b>", styles["Heading2"]))
        conteudo.append(Paragraph(resultados["erro"], styles["Normal"]))
        doc.build(conteudo)
        buffer.seek(0)
        return buffer

    resumo = resumir_votacao(resultados)
    melhor_modelo, info = obter_modelo_mais_confiante(resultados)

    conteudo.append(Paragraph("<b>Resultado Final:</b>", styles["Heading2"]))
    conteudo.append(Paragraph(resumo["texto_final"], styles["Normal"]))

    if resumo.get("observacao"):
        conteudo.append(Spacer(1, 6))
        conteudo.append(Paragraph(f"<b>Observação:</b> {resumo['observacao']}", styles["Normal"]))

    conteudo.append(Spacer(1, 12))

    conteudo.append(Paragraph("<b>Modelo mais confiante:</b>", styles["Heading2"]))
    conteudo.append(Paragraph(nome_modelo_amigavel(melhor_modelo), styles["Normal"]))
    conteudo.append(Paragraph(f"Classe: {info['classe']}", styles["Normal"]))
    conteudo.append(Paragraph(f"Confiança: {info['probabilidade']:.2%}", styles["Normal"]))
    conteudo.append(Spacer(1, 12))

    conteudo.append(Paragraph("<b>Detalhamento dos modelos:</b>", styles["Heading2"]))
    conteudo.append(Spacer(1, 8))

    for nome, resultado in resultados.items():
        conteudo.append(Paragraph(f"<b>{nome_modelo_amigavel(nome)}</b>", styles["Normal"]))
        conteudo.append(Paragraph(f"Classe: {resultado.get('classe', '-')}", styles["Normal"]))
        conteudo.append(
            Paragraph(
                f"Confiança: {float(resultado.get('probabilidade', 0.0)):.2%}",
                styles["Normal"],
            )
        )

        if resultado.get("erro"):
            conteudo.append(Paragraph(f"Erro: {resultado['erro']}", styles["Normal"]))

        conteudo.append(Spacer(1, 8))

    doc.build(conteudo)

    buffer.seek(0)
    return buffer