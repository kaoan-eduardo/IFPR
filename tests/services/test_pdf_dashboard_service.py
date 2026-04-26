from src.services.pdf_dashboard_service import gerar_pdf_dashboard


def test_gerar_pdf_dashboard_retorna_bytes():
    resultado = gerar_pdf_dashboard(
        total=10,
        rachado=6,
        bom=4,
        confianca_media=0.87,
        taxa_incerteza=12.5,
    )

    assert isinstance(resultado, bytes)
    assert len(resultado) > 0
    assert resultado.startswith(b"%PDF")