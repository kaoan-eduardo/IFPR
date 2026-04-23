from __future__ import annotations

from io import BytesIO

import pandas as pd


def _preparar_dataframe_para_excel(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajusta o DataFrame antes da exportação para Excel.
    O Excel não suporta datetimes com timezone.
    """
    df_export = df.copy()

    for coluna in df_export.columns:
        if pd.api.types.is_datetime64tz_dtype(df_export[coluna]):
            df_export[coluna] = df_export[coluna].dt.tz_localize(None)

    return df_export


def exportar_excel(df: pd.DataFrame, sheet_name: str = "Analises") -> bytes:
    """
    Exporta um DataFrame para Excel e retorna o conteúdo em bytes.
    """
    df_export = _preparar_dataframe_para_excel(df)

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_export.to_excel(writer, index=False, sheet_name=sheet_name)

    output.seek(0)
    return output.getvalue()