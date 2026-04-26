from io import BytesIO

from src.services.pdf_service import gerar_pdf_analise


def test_gerar_pdf_analise_retorna_pdf_valido():
    resultados = {
        "random_forest": {
            "classe": "Pavimento em bom estado",
            "probabilidade": 0.91,
        },
        "svm": {
            "classe": "Pavimento com rachaduras detectadas",
            "probabilidade": 0.72,
        },
    }

    resultado = gerar_pdf_analise(
        nome_arquivo="teste.jpg",
        resultados=resultados,
    )

    assert isinstance(resultado, BytesIO)

    pdf_bytes = resultado.getvalue()

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b"%PDF")