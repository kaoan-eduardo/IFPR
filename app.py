from __future__ import annotations

import streamlit as st

from src.config import APP_ICON, APP_LAYOUT, APP_TITLE
from src.ui.header import renderizar_header
from src.ui.styles import aplicar_estilos
from src.ui.tabs.tab_avaliacao_modelo import render_tab_avaliacao_modelo
from src.ui.tabs.tab_dashboard import render_tab_dashboard
from src.ui.tabs.tab_multiplas_imagens import render_tab_multiplas_imagens
from src.ui.tabs.tab_upload_unico import render_tab_upload_unico
from src.ui.tabs.tab_glossario import render_tab_glossario


def inicializar_session_state() -> None:
    estados_iniciais = {
        "resultado_unico": None,
        "ultima_imagem_unica": None,
        "resultado_lote": None,
        "ultimo_lote": None,
        "processando_unico": False,
        "processando_lote": False,
    }

    for chave, valor_inicial in estados_iniciais.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor_inicial


def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        layout=APP_LAYOUT,
        page_icon=APP_ICON,
    )

    inicializar_session_state()

    aplicar_estilos()
    renderizar_header()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📷 Upload único",
        "🗂️ Múltiplas imagens",
        "📚 Histórico",
        "✅ Avaliação do Modelo",
        "📖 Glossário",
    ])

    with tab1:
        render_tab_upload_unico()

    with tab2:
        render_tab_multiplas_imagens()

    with tab3:
        render_tab_dashboard()

    with tab4:
        render_tab_avaliacao_modelo()

    with tab5:
        render_tab_glossario()


if __name__ == "__main__":
    main()