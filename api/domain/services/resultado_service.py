from src.utils.formatters import (
    obter_modelo_mais_confiante,
    resumir_votacao,
)


class ResultadoService:

    def processar(self, resultados: dict):

        resumo = resumir_votacao(resultados)
        melhor_modelo, info = obter_modelo_mais_confiante(resultados)

        return {
            "resultado_final": resumo["texto_final"],
            "observacao": resumo.get("observacao"),
            "modelo_mais_confiante": melhor_modelo,
            "confianca": float(info["probabilidade"]),
            "modelos": resultados
        }