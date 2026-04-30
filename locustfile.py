from pathlib import Path

from locust import HttpUser, task, between


CAMINHO_IMAGEM = Path("data/raw/dataset/ruim/cracked_190_03_01.png")


class UsuarioCarga(HttpUser):
    wait_time = between(1, 3)

    @task
    def analisar_imagem(self):
        with CAMINHO_IMAGEM.open("rb") as img:
            response = self.client.post(
                "/analise/imagem",
                files={
                    "file": (
                        "cracked_190_03_01.png",
                        img,
                        "image/png",
                    )
                },
            )

        print(response.status_code, response.text[:300])