from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def gerar_pdf_dashboard(
    total: int,
    rachado: int,
    bom: int,
    confianca_media: float,
    taxa_incerteza: float,
) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    _, altura = A4
    y = altura - 50

    pdf.setTitle("Relatório de Inspeção de Pavimento")

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y, "Relatório de Inspeção de Pavimento")

    y -= 40
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, f"Total de análises: {total}")

    y -= 25
    pdf.drawString(50, y, f"Com rachaduras: {rachado}")

    y -= 25
    pdf.drawString(50, y, f"Em bom estado: {bom}")

    y -= 25
    pdf.drawString(50, y, f"Confiança média: {confianca_media:.1%}")

    y -= 25
    pdf.drawString(50, y, f"Taxa de incerteza: {taxa_incerteza:.1f}%")

    y -= 40
    pdf.setFont("Helvetica-Oblique", 10)
    pdf.drawString(50, y, "Relatório gerado automaticamente pelo sistema.")

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return buffer.getvalue()