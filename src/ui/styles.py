import streamlit as st

def aplicar_estilos():
    st.markdown("""
    <style>

    /* =========================
       BASE
    ========================= */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .section-title {
        font-size: 1.6rem;
        font-weight: 700;
        margin-top: 30px;
        margin-bottom: 12px;
    }

    /* =========================
       CARDS PRINCIPAIS
    ========================= */
    .info-card {
        padding: 18px;
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.08);
        background: linear-gradient(180deg, rgba(255,255,255,0.025), rgba(255,255,255,0.018));
        box-shadow: 0 6px 18px rgba(0,0,0,0.10);
        margin-bottom: 14px;
    }

    .card-title {
        font-size: 0.85rem;
        opacity: 0.75;
        margin-bottom: 6px;
    }

    .card-value {
        font-size: 1.5rem;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .card-sub {
        font-size: 0.9rem;
        opacity: 0.8;
    }

    /* =========================
       CARDS DE MÉTRICAS (FIXADO)
    ========================= */
    .metric-card {
        padding: 16px;
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.08);
        background: linear-gradient(180deg, rgba(255,255,255,0.025), rgba(255,255,255,0.018));
        box-shadow: 0 6px 18px rgba(0,0,0,0.10);
        margin-bottom: 12px;

        min-height: 130px; /* 🔥 força tamanho igual */
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .metric-title {
        font-size: 13px;
        opacity: 0.75;
        margin-bottom: 6px;
        min-height: 18px;
    }

    .metric-value {
        font-size: 26px;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 6px;
    }

    .metric-sub {
        font-size: 13px;
        opacity: 0.8;
        min-height: 18px; /* 🔥 garante alinhamento */
    }

    /* =========================
       BADGES
    ========================= */
    .badge-good {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
        background: rgba(46, 125, 50, 0.15);
        color: #81C784;
        border: 1px solid rgba(46,125,50,0.4);
        margin-bottom: 10px;
    }

    .badge-bad {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
        background: rgba(198, 40, 40, 0.15);
        color: #EF5350;
        border: 1px solid rgba(198,40,40,0.4);
        margin-bottom: 10px;
    }

    .badge-invalid {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
        background: rgba(120,120,120,0.2);
        color: #ccc;
        border: 1px solid rgba(120,120,120,0.3);
        margin-bottom: 10px;
    }

    /* =========================
       MINI INFO (LOTE)
    ========================= */
    .mini-info {
        font-size: 13px;
        margin-top: 8px;
        opacity: 0.85;
        line-height: 1.4;
    }

    /* =========================
       DETALHAMENTO MODELOS
    ========================= */
    .detail-card {
        padding: 12px;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.05);
        background: rgba(255,255,255,0.02);
        margin-bottom: 10px;
    }

    /* =========================
       NOME DO ARQUIVO
    ========================= */
    .file-name {
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 6px;
        opacity: 0.85;
    }

    /* =========================
       THUMB
    ========================= */
    .thumb-box {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 14px;
    }

    </style>
    """, unsafe_allow_html=True)