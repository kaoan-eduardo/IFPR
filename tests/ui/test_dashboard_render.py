from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

import pandas as pd

from conftest import patch_streamlit_basico
from src.ui.tabs import tab_dashboard


def test_dashboard_carregar_analises_fecha_db(monkeypatch):
    class DbFake:
        fechado = False

        def close(self):
            self.fechado = True

    db_fake = DbFake()

    monkeypatch.setattr(tab_dashboard, "SessionLocal", lambda: db_fake)
    monkeypatch.setattr(tab_dashboard, "listar_analises", lambda db: ["a", "b"])

    resultado = tab_dashboard._carregar_analises()

    assert resultado == ["a", "b"]
    assert db_fake.fechado is True


def test_dashboard_render_topo(monkeypatch):
    patch_streamlit_basico(monkeypatch, tab_dashboard)

    tab_dashboard._render_topo()


def test_dashboard_render_visao_geral(monkeypatch):
    patch_streamlit_basico(monkeypatch, tab_dashboard)

    metricas = {
        "total_analises": 10,
        "qtd_rachado": 4,
        "qtd_bom": 6,
        "perc_rachado": 40.0,
        "perc_bom": 60.0,
        "confianca_media": 0.85,
        "taxa_incerteza": 12.5,
    }

    tab_dashboard._render_visao_geral(metricas)


def test_dashboard_render_exportacao(monkeypatch):
    patch_streamlit_basico(monkeypatch, tab_dashboard)

    monkeypatch.setattr(tab_dashboard, "exportar_excel", lambda df: b"excel")
    monkeypatch.setattr(tab_dashboard, "gerar_pdf_dashboard", lambda **kwargs: b"%PDF")

    metricas = {
        "total_analises": 1,
        "qtd_rachado": 0,
        "qtd_bom": 1,
        "confianca_media": 0.9,
        "taxa_incerteza": 0.0,
    }

    tab_dashboard._render_exportacao_dashboard(pd.DataFrame({"a": [1]}), metricas)


def test_dashboard_sem_analises(monkeypatch):
    patch_streamlit_basico(monkeypatch, tab_dashboard)

    monkeypatch.setattr(tab_dashboard, "_carregar_analises", lambda: [])

    tab_dashboard.render_tab_dashboard()


def test_dashboard_com_json_invalido(monkeypatch):
    patch_streamlit_basico(monkeypatch, tab_dashboard)

    analises = [
        SimpleNamespace(
            id=1,
            nome_arquivo="img.jpg",
            resultado_final=tab_dashboard.RESULTADO_BOM,
            observacao=None,
            modelo_mais_confiante="rf",
            confianca=0.9,
            data_analise=datetime.now(),
            detalhes_modelos="INVALIDO",
        )
    ]

    monkeypatch.setattr(tab_dashboard, "_carregar_analises", lambda: analises)

    tab_dashboard.render_tab_dashboard()