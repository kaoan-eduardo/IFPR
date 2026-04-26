import pandas as pd

from src.services.export_service import exportar_excel


def test_exportar_excel_retorna_bytes():
    df = pd.DataFrame([
        {
            "nome_arquivo": "teste.jpg",
            "resultado_final": "Pavimento em bom estado",
            "confianca": 0.95,
        }
    ])

    resultado = exportar_excel(df)

    assert isinstance(resultado, bytes)
    assert len(resultado) > 0