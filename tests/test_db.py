from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from src.db.base import Base
from src.db.models import Analise, agora_brasil
from src.db.repository import (
    buscar_analise_por_hash,
    listar_analises,
    salvar_analise,
)


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_agora_brasil_retorna_datetime_com_timezone():
    resultado = agora_brasil()

    assert isinstance(resultado, datetime)
    assert resultado.tzinfo is not None
    assert resultado.tzinfo == ZoneInfo("America/Sao_Paulo")


def test_model_analise_possui_nome_da_tabela_correto():
    assert Analise.__tablename__ == "analises"


def test_salvar_analise_persiste_registro_no_banco(db_session: Session):
    analise = salvar_analise(
        db=db_session,
        hash_arquivo="abc123",
        nome_arquivo="imagem_teste.jpg",
        resultado_final="Pavimento em bom estado",
        modelo_mais_confiante="random_forest",
        confianca=0.91,
        observacao="Teste automatizado",
        detalhes_modelos='{"random_forest": 0.91}',
    )

    assert analise.id is not None
    assert analise.hash_arquivo == "abc123"
    assert analise.nome_arquivo == "imagem_teste.jpg"
    assert analise.resultado_final == "Pavimento em bom estado"
    assert analise.modelo_mais_confiante == "random_forest"
    assert analise.confianca == 0.91
    assert analise.observacao == "Teste automatizado"
    assert analise.detalhes_modelos == '{"random_forest": 0.91}'


def test_buscar_analise_por_hash_retorna_registro_existente(db_session: Session):
    salvar_analise(
        db=db_session,
        hash_arquivo="hash_existente",
        nome_arquivo="imagem.jpg",
        resultado_final="Pavimento com rachaduras detectadas",
        modelo_mais_confiante="svm",
        confianca=0.82,
    )

    resultado = buscar_analise_por_hash(db_session, "hash_existente")

    assert resultado is not None
    assert resultado.hash_arquivo == "hash_existente"
    assert resultado.modelo_mais_confiante == "svm"


def test_buscar_analise_por_hash_retorna_none_quando_nao_existe(db_session: Session):
    resultado = buscar_analise_por_hash(db_session, "hash_inexistente")

    assert resultado is None


def test_listar_analises_retorna_registros_ordenados_por_data_desc(db_session: Session):
    primeira = salvar_analise(
        db=db_session,
        hash_arquivo="hash_1",
        nome_arquivo="primeira.jpg",
        resultado_final="Pavimento em bom estado",
        modelo_mais_confiante="random_forest",
        confianca=0.75,
    )

    segunda = salvar_analise(
        db=db_session,
        hash_arquivo="hash_2",
        nome_arquivo="segunda.jpg",
        resultado_final="Pavimento com rachaduras detectadas",
        modelo_mais_confiante="svm",
        confianca=0.95,
    )

    primeira.data_analise = datetime(2026, 1, 1, 10, 0, 0)
    segunda.data_analise = datetime(2026, 1, 2, 10, 0, 0)

    db_session.commit()

    resultados = listar_analises(db_session)

    assert len(resultados) == 2
    assert resultados[0].hash_arquivo == "hash_2"
    assert resultados[1].hash_arquivo == "hash_1"


def test_salvar_analise_faz_rollback_quando_ocorre_erro(monkeypatch, db_session: Session):
    rollback_chamado = False

    def commit_com_erro():
        raise SQLAlchemyError("Erro simulado no commit")

    def rollback_mock():
        nonlocal rollback_chamado
        rollback_chamado = True

    monkeypatch.setattr(db_session, "commit", commit_com_erro)
    monkeypatch.setattr(db_session, "rollback", rollback_mock)

    with pytest.raises(SQLAlchemyError):
        salvar_analise(
            db=db_session,
            hash_arquivo="hash_erro",
            nome_arquivo="erro.jpg",
            resultado_final="Erro",
            modelo_mais_confiante="random_forest",
            confianca=0.0,
        )

    assert rollback_chamado is True


def test_sessionlocal_esta_configurado_corretamente():
    from src.db.session import SessionLocal

    assert SessionLocal.kw["autoflush"] is False
    assert SessionLocal.kw["autocommit"] is False
    assert SessionLocal.kw["expire_on_commit"] is False


def test_create_tables_main_cria_tabelas_e_exibe_mensagem(monkeypatch, capsys):
    from src.db import create_tables

    create_all_chamado = False

    def create_all_mock(bind):
        nonlocal create_all_chamado
        create_all_chamado = True
        assert bind is create_tables.engine

    monkeypatch.setattr(create_tables.Base.metadata, "create_all", create_all_mock)

    create_tables.main()

    saida = capsys.readouterr()

    assert create_all_chamado is True
    assert "Tabelas criadas com sucesso." in saida.out