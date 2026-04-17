import streamlit as st


def aplicar_estilos() -> None:
    st.markdown("""
    <style>
    .block-container {
        max-width: 1180px;
        margin: auto;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at top left, rgba(60, 180, 120, 0.05), transparent 30%),
            radial-gradient(circle at top right, rgba(30, 144, 255, 0.04), transparent 28%),
            radial-gradient(circle at bottom, rgba(255, 215, 0, 0.03), transparent 25%);
    }

    .info-card {
        padding: 18px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.08);
        background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));
        box-shadow:
            0 8px 24px rgba(0,0,0,0.12),
            inset 0 1px 0 rgba(255,255,255,0.03);
        min-height: 190px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        margin-bottom: 12px;
    }

    .detail-card {
        padding: 15px;
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.08);
        background: linear-gradient(180deg, rgba(255,255,255,0.025), rgba(255,255,255,0.018));
        box-shadow: 0 6px 18px rgba(0,0,0,0.10);
        margin-bottom: 12px;
        min-height: 150px;
    }

    .detail-card-lote {
        padding: 12px;
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.08);
        background: linear-gradient(180deg, rgba(255,255,255,0.025), rgba(255,255,255,0.018));
        box-shadow: 0 4px 14px rgba(0,0,0,0.10);
        margin-bottom: 10px;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .metric-card {
        padding: 16px;
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.08);
        background: linear-gradient(180deg, rgba(255,255,255,0.025), rgba(255,255,255,0.018));
        box-shadow: 0 6px 18px rgba(0,0,0,0.10);
        margin-bottom: 12px;
    }

    .card-title {
        font-size: 13px;
        opacity: 0.72;
        margin-bottom: 8px;
        font-weight: 600;
    }

    .card-value {
        font-size: 22px;
        font-weight: 800;
        line-height: 1.22;
        margin-bottom: 8px;
        letter-spacing: -0.02em;
    }

    .card-sub {
        font-size: 13px;
        opacity: 0.82;
        line-height: 1.5;
    }

    .card-title-lote {
        font-size: 11px;
        opacity: 0.76;
        margin-bottom: 6px;
        font-weight: 700;
        line-height: 1.35;
        word-break: break-word;
    }

    .card-value-lote {
        font-size: 16px;
        font-weight: 800;
        line-height: 1.15;
        margin-bottom: 6px;
        letter-spacing: -0.01em;
        word-break: break-word;
    }

    .card-sub-lote {
        font-size: 11px;
        opacity: 0.84;
        line-height: 1.4;
        word-break: break-word;
    }

    .metric-title {
        font-size: 13px;
        opacity: 0.74;
        margin-bottom: 6px;
    }

    .metric-value {
        font-size: 24px;
        font-weight: 800;
        line-height: 1;
    }

    .thumb-box {
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 14px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.10);
    }

    .file-name {
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 8px;
        min-height: 20px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .badge-good,
    .badge-bad,
    .badge-invalid {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .badge-good {
        background-color: rgba(46, 125, 50, 0.15);
        border: 1px solid rgba(46, 125, 50, 0.35);
    }

    .badge-bad {
        background-color: rgba(198, 40, 40, 0.15);
        border: 1px solid rgba(198, 40, 40, 0.35);
    }

    .badge-invalid {
        background-color: rgba(255, 152, 0, 0.15);
        border: 1px solid rgba(255, 152, 0, 0.35);
    }

    .mini-info {
        font-size: 12px;
        opacity: 0.84;
        line-height: 1.5;
        margin-bottom: 8px;
        min-height: 78px;
    }

    .section-title {
        font-size: 1.3rem;
        font-weight: 800;
        margin-top: 8px;
        margin-bottom: 10px;
        letter-spacing: -0.02em;
    }

    [data-testid="stFileUploader"] {
        border-radius: 18px;
    }

    .stButton > button {
        border-radius: 14px !important;
        font-weight: 700 !important;
        min-height: 46px !important;
        box-shadow: 0 6px 18px rgba(0,0,0,0.10);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 12px 12px 0 0;
        padding-left: 16px;
        padding-right: 16px;
    }
    </style>
    """, unsafe_allow_html=True)