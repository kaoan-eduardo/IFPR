from src.db.base import Base
from src.db.models import Analise
from src.db.session import engine


def main():
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso.")


if __name__ == "__main__":
    main()