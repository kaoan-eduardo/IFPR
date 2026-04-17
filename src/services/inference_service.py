from __future__ import annotations

import os
import tempfile

from src.core.predict import prever_imagem


def analisar_arquivo(uploaded_file) -> dict:
    """
    Recebe um arquivo enviado pelo Streamlit,
    salva temporariamente no disco, executa a predição
    e remove o arquivo após o processamento.

    Args:
        uploaded_file: arquivo vindo do Streamlit (st.file_uploader)

    Returns:
        dict com os resultados da predição
    """

    # pega extensão do arquivo (ex: .jpg, .png)
    sufixo = os.path.splitext(uploaded_file.name)[1] or ".jpg"

    # cria arquivo temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix=sufixo) as temp:
        temp.write(uploaded_file.getbuffer())
        caminho_temp = temp.name

    try:
        # chama o core da aplicação (predict)
        resultados = prever_imagem(caminho_temp)

    finally:
        # remove o arquivo temporário
        if os.path.exists(caminho_temp):
            os.remove(caminho_temp)

    return resultados