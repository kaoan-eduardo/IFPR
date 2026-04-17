import base64
from pathlib import Path

import streamlit as st

from src.config import LOGO_PATH


def carregar_logo_base64() -> str | None:
    caminho_logo = Path(LOGO_PATH)

    if not caminho_logo.exists():
        return None

    with open(caminho_logo, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def renderizar_header() -> None:
    logo_b64 = carregar_logo_base64()

    # ================= CSS =================
    st.markdown("""
    <style>
    .header-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 8px;
        line-height: 1.15;
        letter-spacing: -0.01em;
    }

    .header-subtitle {
        font-size: 0.95rem;
        opacity: 0.82;
        line-height: 1.55;
        margin-bottom: 8px;
    }

    .header-badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 600;
        border: 1px solid rgba(255,255,255,0.10);
        background-color: rgba(255,255,255,0.05);
        white-space: nowrap;
        margin-right: 8px;
        margin-top: 4px;
    }

    .header-divider {
        margin-bottom: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ================= LAYOUT =================
    col1, col2 = st.columns([1, 2.2], vertical_alignment="center")

    # ===== LOGO =====
    with col1:
        if logo_b64:
            st.image(f"data:image/png;base64,{logo_b64}", width=220)
        else:
            st.markdown("## 🛣️")

    # ===== TEXTO =====
    with col2:
        st.markdown(
            '<div class="header-title">IFPR — Identificação de Fissuras em Pavimentos Rodoviários</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="header-subtitle">Sistema inteligente para análise automatizada de fissuras em pavimentos, utilizando técnicas de visão computacional e aprendizado de máquina.</div>',
            unsafe_allow_html=True
        )

        # ===== BADGES INLINE (CORRETO) =====
        st.markdown(
            '<span class="header-badge">Visão Computacional</span>'
            '<span class="header-badge">Machine Learning</span>'
            '<span class="header-badge">Pavimentos Rodoviários</span>',
            unsafe_allow_html=True
        )

    # ===== ESPAÇAMENTO FINAL =====
    st.markdown('<div class="header-divider"></div>', unsafe_allow_html=True)