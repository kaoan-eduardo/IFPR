from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.utils.formatters import (
    nome_modelo_amigavel,
    obter_modelo_mais_confiante,
    resumir_votacao,
)


LOGO_PATH = Path("assets/logo.jpg")


def _criar_header(conteudo: list, titulo: str) -> None:
    styles = getSampleStyleSheet()

    if LOGO_PATH.exists():
        logo = Image(str(LOGO_PATH))
        logo.drawHeight = 2.4 * cm
        logo.drawWidth = 2.4 * cm
    else:
        logo = ""

    titulo_pdf = Paragraph(f"<b>{titulo}</b>", styles["Title"])

    tabela_header = Table(
        [[logo, titulo_pdf]],
        colWidths=[3.2 * cm, 12.8 * cm],
    )

    tabela_header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (0, 0), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    conteudo.append(tabela_header)

    linha = Table([[""]], colWidths=[16 * cm])
    linha.setStyle(
        TableStyle(
            [
                ("LINEBELOW", (0, 0), (-1, -1), 1.2, colors.HexColor("#1B4332")),
            ]
        )
    )

    conteudo.append(linha)
    conteudo.append(Spacer(1, 18))


def _criar_tabela(dados: list[list[str]], col_widths: list[float]) -> Table:
    tabela = Table(dados, colWidths=col_widths)

    tabela.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B4332")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8F8F8")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    return tabela


def gerar_pdf_analise(nome_arquivo: str, resultados: dict[str, Any]) -> BytesIO:
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    conteudo = []

    _criar_header(conteudo, "Relatório de Análise de Pavimento")

    data_atual = datetime.now().strftime("%d/%m/%Y")
    hora_atual = datetime.now().strftime("%H:%M:%S")

    dados_identificacao = [
        ["Campo", "Informação"],
        ["Arquivo analisado", nome_arquivo],
        ["Data do relatório", data_atual],
        ["Hora do relatório", hora_atual],
    ]

    conteudo.append(Paragraph("Identificação do Relatório", styles["Heading2"]))
    conteudo.append(_criar_tabela(dados_identificacao, [5 * cm, 11 * cm]))
    conteudo.append(Spacer(1, 16))

    if "erro" in resultados:
        dados_erro = [
            ["Campo", "Informação"],
            ["Resultado", resultados["erro"]],
        ]

        conteudo.append(Paragraph("Resultado", styles["Heading2"]))
        conteudo.append(_criar_tabela(dados_erro, [5 * cm, 11 * cm]))

        doc.build(conteudo)
        buffer.seek(0)
        return buffer

    resumo = resumir_votacao(resultados)
    melhor_modelo, info = obter_modelo_mais_confiante(resultados)

    dados_resultado = [
        ["Campo", "Informação"],
        ["Resultado final", resumo["texto_final"]],
        ["Observação", resumo.get("observacao") or "-"],
        ["Modelo mais confiante", nome_modelo_amigavel(melhor_modelo)],
        ["Classe indicada", str(info["classe"])],
        ["Confiança", f"{info['probabilidade']:.2%}"],
    ]

    conteudo.append(Paragraph("Resumo da Análise", styles["Heading2"]))
    conteudo.append(_criar_tabela(dados_resultado, [5 * cm, 11 * cm]))
    conteudo.append(Spacer(1, 16))

    dados_modelos = [["Modelo", "Classe", "Confiança"]]

    for nome, resultado in resultados.items():
        dados_modelos.append(
            [
                nome_modelo_amigavel(nome),
                str(resultado.get("classe", "-")),
                f"{float(resultado.get('probabilidade', 0.0)):.2%}",
            ]
        )

    conteudo.append(Paragraph("Detalhamento dos Modelos", styles["Heading2"]))
    conteudo.append(_criar_tabela(dados_modelos, [7 * cm, 4.5 * cm, 4.5 * cm]))
    conteudo.append(Spacer(1, 20))

    conteudo.append(
        Paragraph(
            "Relatório gerado automaticamente pelo sistema de identificação de fissuras em pavimentos rodoviários.",
            styles["Italic"],
        )
    )

    doc.build(conteudo)

    buffer.seek(0)
    return buffer