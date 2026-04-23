from __future__ import annotations

import io
import zipfile
from datetime import datetime
from typing import Any

import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from src.config import (
    ALLOWED_IMAGE_EXTENSIONS,
    INVALID_IMAGE_LABEL,
    LIMITE_DETALHAMENTO,
    LIMITE_GALERIA,
    LIMITE_GALERIA_COMPLETA,
)
from src.services.analysis_service import gerar_hash_bytes, registrar_analise
from src.services.inference_service import analisar_arquivo
from src.ui.components import exibir_detalhamento, preparar_thumbnail
from src.utils.formatters import (
    nome_modelo_amigavel,
    obter_modelo_mais_confiante,
    resumir_votacao,
)


RESULTADO_RACHADO = "Pavimento com rachaduras detectadas"
RESULTADO_BOM = "Pavimento em bom estado"


def _listar_arquivos_zip(upload_zip: Any) -> tuple[list[dict[str, Any]], str | None]:
    arquivos_validos: list[dict[str, Any]] = []

    try:
        with zipfile.ZipFile(io.BytesIO(upload_zip.read()), "r") as zf:
            for nome in zf.namelist():
                if nome.endswith("/"):
                    continue

                extensao = nome.split(".")[-1].lower() if "." in nome else ""
                if extensao in [ext.lower() for ext in ALLOWED_IMAGE_EXTENSIONS]:
                    with zf.open(nome) as arquivo_zip:
                        conteudo = arquivo_zip.read()

                    arquivos_validos.append({
                        "name": nome.split("/")[-1],
                        "full_name": nome,
                        "bytes": conteudo,
                        "size": len(conteudo),
                    })

        return arquivos_validos, None

    except zipfile.BadZipFile:
        return [], "Arquivo ZIP inválido ou corrompido."
    except Exception as exc:
        return [], f"Erro ao ler o ZIP: {exc}"


def _converter_arquivo_zip_para_buffer(arquivo_zip_dict: dict[str, Any]) -> io.BytesIO:
    buffer = io.BytesIO(arquivo_zip_dict["bytes"])
    buffer.name = arquivo_zip_dict["name"]
    return buffer


def _gerar_excel_lote(resultados_lote: list[dict[str, Any]]) -> io.BytesIO:
    df = pd.DataFrame([
        {
            "Arquivo": item["nome"],
            "Resultado Final": item["resultado_final"],
            "Modelo Mais Confiante": item["melhor_modelo"],
            "Classe": item["classe_melhor_modelo"],
            "Confiança (%)": round(item["confianca"] * 100, 2),
        }
        for item in resultados_lote
    ])

    resumo_df = pd.DataFrame([
        {"Métrica": "Total de imagens", "Valor": len(resultados_lote)},
        {"Métrica": "Com rachaduras", "Valor": sum(1 for item in resultados_lote if item["resultado_final"] == RESULTADO_RACHADO)},
        {"Métrica": "Em bom estado", "Valor": sum(1 for item in resultados_lote if item["resultado_final"] == RESULTADO_BOM)},
        {"Métrica": "Inválidas", "Valor": sum(1 for item in resultados_lote if item["resultado_final"] == INVALID_IMAGE_LABEL)},
        {"Métrica": "Gerado em", "Valor": datetime.now().strftime("%d/%m/%Y %H:%M:%S")},
    ])

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        resumo_df.to_excel(writer, sheet_name="Resumo", index=False)
        df.to_excel(writer, sheet_name="Analise Atual", index=False)

    buffer.seek(0)
    return buffer


def _gerar_pdf_lote(resultados_lote: list[dict[str, Any]]) -> io.BytesIO:
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    _, altura = letter

    total = len(resultados_lote)
    com_rachadura = sum(1 for item in resultados_lote if item["resultado_final"] == RESULTADO_RACHADO)
    bom_estado = sum(1 for item in resultados_lote if item["resultado_final"] == RESULTADO_BOM)
    invalidas = sum(1 for item in resultados_lote if item["resultado_final"] == INVALID_IMAGE_LABEL)

    y = altura - 40

    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(40, y, "Relatório da Análise Atual")
    y -= 24

    pdf.setFont("Helvetica", 10)
    pdf.drawString(40, y, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    y -= 18
    pdf.drawString(40, y, f"Total de imagens: {total}")
    y -= 14
    pdf.drawString(40, y, f"Com rachaduras: {com_rachadura}")
    y -= 14
    pdf.drawString(40, y, f"Em bom estado: {bom_estado}")
    y -= 14
    pdf.drawString(40, y, f"Inválidas: {invalidas}")
    y -= 24

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(40, y, "Resultados:")
    y -= 16

    pdf.setFont("Helvetica", 9)

    for i, item in enumerate(resultados_lote, start=1):
        linhas = [
            f"{i}. Arquivo: {item['nome']}",
            f"   Resultado: {item['resultado_final']}",
            f"   Modelo mais confiante: {item['melhor_modelo']}",
            f"   Classe: {item['classe_melhor_modelo']} | Confiança: {item['confianca']:.2%}",
        ]

        for linha in linhas:
            if y < 45:
                pdf.showPage()
                y = altura - 40
                pdf.setFont("Helvetica", 9)

            pdf.drawString(40, y, linha[:110])
            y -= 12

        y -= 5

    pdf.save()
    buffer.seek(0)
    return buffer


def _inicializar_estado_lote() -> None:
    if "resultado_lote" not in st.session_state:
        st.session_state.resultado_lote = None

    if "ultimo_lote" not in st.session_state:
        st.session_state.ultimo_lote = None


def _obter_identificador_lote(
    modo_envio: str,
    arquivos: list[Any] | None,
    arquivos_zip: list[dict[str, Any]] | None,
) -> tuple[Any, ...] | None:
    if modo_envio == "Upload múltiplo" and arquivos:
        return tuple((arquivo.name, arquivo.size) for arquivo in arquivos)

    if modo_envio == "Arquivo ZIP" and arquivos_zip:
        return tuple((arquivo["full_name"], arquivo["size"]) for arquivo in arquivos_zip)

    return None


def _montar_resultado_erro(arquivo_lote: Any, nome_arquivo: str) -> dict[str, Any]:
    return {
        "arquivo": arquivo_lote,
        "nome": nome_arquivo,
        "resultado_final": INVALID_IMAGE_LABEL,
        "melhor_modelo": "-",
        "classe_melhor_modelo": "-",
        "confianca": 0.0,
        "detalhamento_disponivel": False,
        "resultados_completos": None,
    }


def _montar_resultado_sucesso(
    arquivo_lote: Any,
    nome_arquivo: str,
    resultados: dict[str, Any],
    detalhamento_disponivel: bool,
    hash_arquivo: str,
) -> dict[str, Any]:
    resumo = resumir_votacao(resultados)
    melhor_modelo, melhor_resultado = obter_modelo_mais_confiante(resultados)

    registrar_analise(
        nome_arquivo=nome_arquivo,
        resultados=resultados,
        hash_arquivo=hash_arquivo,
    )

    return {
        "arquivo": arquivo_lote,
        "nome": nome_arquivo,
        "resultado_final": resumo["texto_final"],
        "melhor_modelo": nome_modelo_amigavel(melhor_modelo) if melhor_modelo else "-",
        "classe_melhor_modelo": melhor_resultado["classe"] if melhor_resultado else "-",
        "confianca": melhor_resultado["probabilidade"] if melhor_resultado else 0.0,
        "detalhamento_disponivel": detalhamento_disponivel,
        "resultados_completos": resultados if detalhamento_disponivel else None,
    }


def _processar_lote(
    modo_envio: str,
    arquivos: list[Any] | None,
    arquivos_zip: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    resultados_lote: list[dict[str, Any]] = []
    fonte_arquivos = arquivos if modo_envio == "Upload múltiplo" else arquivos_zip
    total_itens = len(fonte_arquivos) if fonte_arquivos else 0

    progress_bar = st.progress(0)
    status_text = st.empty()

    st.session_state.processando_lote = True

    try:
        with st.spinner("🔍 Analisando lote de imagens..."):
            for i, item in enumerate(fonte_arquivos or [], start=1):
                if modo_envio == "Upload múltiplo":
                    arquivo_lote = item
                    nome_arquivo = arquivo_lote.name
                    conteudo = arquivo_lote.getvalue()
                else:
                    arquivo_lote = _converter_arquivo_zip_para_buffer(item)
                    nome_arquivo = item["name"]
                    conteudo = item["bytes"]

                hash_arquivo = gerar_hash_bytes(conteudo)

                status_text.markdown(f"**Processando:** {i}/{total_itens} — `{nome_arquivo}`")

                resultados = analisar_arquivo(arquivo_lote)

                if "erro" in resultados:
                    resultados_lote.append(_montar_resultado_erro(arquivo_lote, nome_arquivo))
                else:
                    resultados_lote.append(
                        _montar_resultado_sucesso(
                            arquivo_lote=arquivo_lote,
                            nome_arquivo=nome_arquivo,
                            resultados=resultados,
                            detalhamento_disponivel=i <= LIMITE_DETALHAMENTO,
                            hash_arquivo=hash_arquivo,
                        )
                    )

                progress_bar.progress(i / total_itens)
    finally:
        status_text.empty()
        progress_bar.empty()
        st.session_state.processando_lote = False

    return resultados_lote


def _render_metricas_lote(resultados_lote: list[dict[str, Any]]) -> None:
    total = len(resultados_lote)
    com_rachadura = sum(1 for item in resultados_lote if item["resultado_final"] == RESULTADO_RACHADO)
    bom_estado = sum(1 for item in resultados_lote if item["resultado_final"] == RESULTADO_BOM)
    invalidas = sum(1 for item in resultados_lote if item["resultado_final"] == INVALID_IMAGE_LABEL)

    st.markdown('<div class="section-title">📋 Resumo do lote</div>', unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)

    for col, titulo, valor in [
        (m1, "Total de imagens", total),
        (m2, "Com rachaduras", com_rachadura),
        (m3, "Em bom estado", bom_estado),
        (m4, "Inválidas", invalidas),
    ]:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div>
                    <div class="metric-title">{titulo}</div>
                    <div class="metric-value">{valor}</div>
                </div>
                <div class="metric-sub">&nbsp;</div>
            </div>
            """, unsafe_allow_html=True)


def _render_tabela_lote(resultados_lote: list[dict[str, Any]]) -> None:
    st.markdown('<div class="section-title">📄 Tabela resumida do lote</div>', unsafe_allow_html=True)

    df_lote = pd.DataFrame([
        {
            "Arquivo": item["nome"],
            "Resultado Final": item["resultado_final"],
            "Modelo Mais Confiante": item["melhor_modelo"],
            "Classe": item["classe_melhor_modelo"],
            "Confiança": f"{item['confianca']:.1%}",
        }
        for item in resultados_lote
    ])

    st.dataframe(df_lote, width="stretch")


def _render_exportacao_lote(resultados_lote: list[dict[str, Any]]) -> None:
    st.markdown('<div class="section-title">📥 Exportação da análise</div>', unsafe_allow_html=True)

    col_export1, col_export2 = st.columns(2)

    with col_export1:
        st.download_button(
            label="📊 Exportar análise para Excel",
            data=_gerar_excel_lote(resultados_lote),
            file_name="analise_atual_lote.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_excel_lote",
            width="stretch",
        )

    with col_export2:
        st.download_button(
            label="📄 Exportar análise para PDF",
            data=_gerar_pdf_lote(resultados_lote),
            file_name="analise_atual_lote.pdf",
            mime="application/pdf",
            key="download_pdf_lote",
            width="stretch",
        )


def _render_galeria_lote(resultados_lote: list[dict[str, Any]]) -> None:
    itens_para_exibir = resultados_lote[:LIMITE_GALERIA]

    st.markdown('<div class="section-title">🖼️ Galeria de resultados</div>', unsafe_allow_html=True)

    if len(resultados_lote) > LIMITE_GALERIA:
        st.info(
            f"Exibindo apenas as primeiras {LIMITE_GALERIA} imagens de "
            f"{len(resultados_lote)} analisadas para manter a performance."
        )

    galerias = st.columns(3, gap="small")

    for i, item in enumerate(itens_para_exibir):
        coluna = galerias[i % 3]

        with coluna:
            thumb = preparar_thumbnail(item["arquivo"], tamanho=(420, 240))

            with st.container(border=True):
                st.markdown(f'<div class="file-name">{item["nome"]}</div>', unsafe_allow_html=True)
                st.image(thumb, width="stretch")

                if item["resultado_final"] == RESULTADO_RACHADO:
                    st.markdown('<div class="badge-bad">Com rachaduras</div>', unsafe_allow_html=True)
                elif item["resultado_final"] == RESULTADO_BOM:
                    st.markdown('<div class="badge-good">Bom estado</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="badge-invalid">Imagem inválida</div>', unsafe_allow_html=True)

                st.markdown(f"""
                <div class="mini-info">
                    <b>Modelo mais confiante:</b> {item['melhor_modelo']}<br>
                    <b>Classe:</b> {item['classe_melhor_modelo']}<br>
                    <b>Confiança:</b> {item['confianca']:.1%}
                </div>
                """, unsafe_allow_html=True)

                if item["detalhamento_disponivel"] and item["resultados_completos"] is not None:
                    with st.expander("Ver detalhamento"):
                        exibir_detalhamento(item["resultados_completos"])
                else:
                    st.caption("Detalhamento ocultado neste item para preservar a performance do sistema.")


def render_tab_multiplas_imagens() -> None:
    _inicializar_estado_lote()

    st.markdown('<div class="section-title">📦 Modo de envio</div>', unsafe_allow_html=True)

    modo_envio = st.radio(
        "Escolha como deseja enviar as imagens",
        ["Upload múltiplo", "Arquivo ZIP"],
        horizontal=True,
        key="modo_envio_lote",
    )

    arquivos = None
    arquivos_zip = None

    if modo_envio == "Upload múltiplo":
        arquivos = st.file_uploader(
            "📤 Enviar imagens",
            type=ALLOWED_IMAGE_EXTENSIONS,
            accept_multiple_files=True,
            key="upload_lote",
        )

        if arquivos:
            st.markdown(
                f'<div class="section-title">🗂️ {len(arquivos)} imagem(ns) selecionada(s)</div>',
                unsafe_allow_html=True,
            )

            if len(arquivos) > LIMITE_GALERIA_COMPLETA:
                st.warning(
                    f"⚠️ Lote grande detectado ({len(arquivos)} imagens). "
                    f"O sistema vai analisar todas, mas exibirá somente parte dos resultados na interface "
                    f"para evitar travamentos. Para lotes muito grandes, prefira usar arquivo ZIP."
                )
    else:
        upload_zip = st.file_uploader(
            "📦 Enviar arquivo ZIP com imagens",
            type=["zip"],
            accept_multiple_files=False,
            key="upload_zip_lote",
        )

        if upload_zip is not None:
            arquivos_zip, erro_zip = _listar_arquivos_zip(upload_zip)

            if erro_zip:
                st.error(erro_zip)
                arquivos_zip = None
            else:
                st.markdown(
                    f'<div class="section-title">🗂️ {len(arquivos_zip)} imagem(ns) encontrada(s) no ZIP</div>',
                    unsafe_allow_html=True,
                )

                if len(arquivos_zip) > LIMITE_GALERIA_COMPLETA:
                    st.warning(
                        f"⚠️ Lote grande detectado ({len(arquivos_zip)} imagens no ZIP). "
                        f"O sistema vai analisar todas, mas exibirá somente parte dos resultados na interface "
                        f"para preservar a performance."
                    )

    identificador_lote = _obter_identificador_lote(modo_envio, arquivos, arquivos_zip)

    if identificador_lote is None:
        return

    if st.session_state.ultimo_lote != identificador_lote:
        st.session_state.resultado_lote = None
        st.session_state.ultimo_lote = identificador_lote

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        clicar_lote = st.button(
            "🚀 Analisar lote",
            width="stretch",
            key="botao_lote",
            disabled=st.session_state.processando_lote,
        )

    if clicar_lote and not st.session_state.processando_lote:
        st.session_state.resultado_lote = _processar_lote(modo_envio, arquivos, arquivos_zip)

    if st.session_state.resultado_lote is None:
        st.info("👆 Clique em 'Analisar lote' para processar as imagens enviadas.")
        return

    resultados_lote = st.session_state.resultado_lote

    _render_metricas_lote(resultados_lote)
    _render_tabela_lote(resultados_lote)
    _render_exportacao_lote(resultados_lote)
    _render_galeria_lote(resultados_lote)