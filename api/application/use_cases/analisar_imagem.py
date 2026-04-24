from __future__ import annotations

import hashlib
import json
from datetime import datetime

from api.domain.services.resultado_service import ResultadoService
from api.infrastructure.image.image_service import ImageService
from api.infrastructure.ml.model_service import ModelService

from src.db.repository import salvar_analise
from src.db.session import SessionLocal


class AnalisarImagemUseCase:
    def __init__(self) -> None:
        self.image_service = ImageService()
        self.model_service = ModelService()
        self.resultado_service = ResultadoService()

    def executar(self, nome_arquivo: str, conteudo: bytes) -> dict:
        hash_arquivo = hashlib.sha256(conteudo).hexdigest()

        imagem = self.image_service.carregar(conteudo)
        resultados_modelos = self.model_service.prever(imagem)

        resultado_consolidado = self.resultado_service.processar(resultados_modelos)

        db = SessionLocal()

        try:
            nova_analise = salvar_analise(
                db=db,
                hash_arquivo=hash_arquivo,
                nome_arquivo=nome_arquivo,
                resultado_final=resultado_consolidado["resultado_final"],
                modelo_mais_confiante=resultado_consolidado["modelo_mais_confiante"],
                confianca=resultado_consolidado["confianca"],
                observacao=resultado_consolidado.get("observacao"),
                detalhes_modelos=json.dumps(
                    resultado_consolidado["modelos"],
                    ensure_ascii=False,
                ),
            )

            return {
                "status": "sucesso",
                "id_analise": nova_analise.id,
                "arquivo": nome_arquivo,
                "hash_arquivo": hash_arquivo,
                "data_analise": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                **resultado_consolidado,
            }

        finally:
            db.close()