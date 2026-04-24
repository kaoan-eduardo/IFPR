from __future__ import annotations

import json

from fastapi import APIRouter, File, UploadFile

from api.application.use_cases.analisar_imagem import AnalisarImagemUseCase
from api.schemas.response import AnaliseHistoricoResponse, AnaliseResponse

from src.db.repository import listar_analises
from src.db.session import SessionLocal

router = APIRouter(prefix="/analise", tags=["Analise"])


@router.post("/imagem", response_model=AnaliseResponse)
async def analisar_imagem(file: UploadFile = File(...)):
    conteudo = await file.read()

    use_case = AnalisarImagemUseCase()
    resultado = use_case.executar(file.filename or "arquivo_sem_nome", conteudo)

    return resultado


@router.get("/historico", response_model=list[AnaliseHistoricoResponse])
def listar_historico():
    db = SessionLocal()

    try:
        analises = listar_analises(db)

        historico = []

        for analise in analises:
            modelos = None

            if analise.detalhes_modelos:
                try:
                    modelos = json.loads(analise.detalhes_modelos)
                except json.JSONDecodeError:
                    modelos = None

            historico.append(
                {
                    "id_analise": analise.id,
                    "arquivo": analise.nome_arquivo,
                    "hash_arquivo": analise.hash_arquivo,
                    "data_analise": analise.data_analise.strftime("%d/%m/%Y %H:%M:%S"),
                    "resultado_final": analise.resultado_final,
                    "observacao": analise.observacao,
                    "modelo_mais_confiante": analise.modelo_mais_confiante,
                    "confianca": analise.confianca,
                    "modelos": modelos,
                }
            )

        return historico

    finally:
        db.close()