from __future__ import annotations

import os
import tempfile
from typing import Any

from src.core.predict import prever_imagem


def _obter_bytes_arquivo(uploaded_file: Any) -> bytes:
    """
    Lê o conteúdo do arquivo enviado, suportando:
    - objetos do Streamlit UploadedFile
    - io.BytesIO
    - buffers com .read()
    """
    if hasattr(uploaded_file, "getbuffer"):
        return bytes(uploaded_file.getbuffer())

    if hasattr(uploaded_file, "read"):
        conteudo = uploaded_file.read()
        if isinstance(conteudo, bytes):
            return conteudo

    raise ValueError("Arquivo enviado em formato inválido ou não suportado.")


def analisar_arquivo(uploaded_file: Any) -> dict[str, Any]:
    """
    Recebe um arquivo enviado pelo Streamlit ou um buffer em memória,
    salva temporariamente no disco, executa a predição
    e remove o arquivo após o processamento.
    """
    nome_arquivo = getattr(uploaded_file, "name", "imagem.jpg")
    sufixo = os.path.splitext(nome_arquivo)[1] or ".jpg"

    conteudo = _obter_bytes_arquivo(uploaded_file)

    with tempfile.NamedTemporaryFile(delete=False, suffix=sufixo) as temp:
        temp.write(conteudo)
        caminho_temp = temp.name

    try:
        resultados = prever_imagem(caminho_temp)
    finally:
        if os.path.exists(caminho_temp):
            os.remove(caminho_temp)

    return resultados