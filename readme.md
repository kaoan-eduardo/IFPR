<p align="center">
  <img src="assets/logo_ifpr_icon.png" width="60"/>
  <b style="font-size: 28px;">IFPR Vision - Identificação de Fissuras em Pavimentos Rodoviários</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10--3.14-blue"/>
  <img src="https://img.shields.io/badge/Status-Em%20Desenvolvimento-orange"/>
  <img src="https://img.shields.io/badge/Machine%20Learning-Ativo-green"/>
  <img src="https://img.shields.io/badge/Interface-Streamlit-red"/>
  <img src="https://img.shields.io/badge/Testes-Pytest-blueviolet"/>
  <img src="https://img.shields.io/badge/Coverage-80%25+-brightgreen"/>
</p>

---

# 📌 1. Identificação

## 🎨 Identidade Visual

<p align="center">
  <img src="assets/logo_ifpr_dark.png" width="480"/>
</p>

Sistema de visão computacional aplicado à **detecção automática de fissuras em pavimentos rodoviários**, utilizando Machine Learning clássico e arquitetura escalável.

---

## 🌐 Redes

<p>
  <a href="https://github.com/kaoan-eduardo">GitHub</a> •
  <a href="https://www.linkedin.com/in/kaoan-matos-a2a797244/">LinkedIn</a>
</p>

---

## 👥 Equipe

| Nome | Papel | Responsabilidade |
|------|------|----------------|
| Kaoan Eduardo | Desenvolvedor | ML, backend, frontend, banco de dados, testes |

---

## 📅 Data
Abril de 2026

---

# 🧠 2. Visão do Sistema

Sistema inteligente capaz de:

✔ Detectar rachaduras em imagens de pavimento  
✔ Processar grandes volumes de imagens  
✔ Fornecer métricas e insights  
✔ Exportar resultados para análise externa  

---

## 🎯 Objetivo

Classificar imagens em:

- 🟥 Com rachaduras
- 🟩 Em bom estado

---

# 🧩 3. Funcionalidades

## 📷 Upload Único
- Ensemble de modelos
- Votação entre classificadores
- Modelo mais confiante
- Probabilidade (%)
- Comparação visual
- Exportação PDF

---

## 🗂️ Análise em Lote
- Upload múltiplo ou `.zip`
- Processamento de milhares de imagens
- Barra de progresso
- Resumo automático
- Galeria otimizada

---

## 📊 Dashboard
- Métricas globais
- Distribuição de resultados
- Frequência por modelo
- Evolução temporal

Exportação:
- PDF
- Excel (Power BI ready)

---

## 🧠 Avaliação dos Modelos
- Cross Validation (k-fold)
- Accuracy, Precision, Recall, F1
- Matriz de confusão
- Comparação entre modelos

---

# 🏗️ 4. Arquitetura

Arquitetura em camadas, focada em escalabilidade:

```bash
src/ 
├── core/            # Machine Learning (features, predição)
├── services/        # Regras de negócio 
├── db/              # Banco de dados (SQLAlchemy)
|── ui/              # Interface Streamlit
├── utils/           # Funções auxiliares
```

---

## 🔌 API (FastAPI)
Permite integração com:
- aplicações externas
- sistemas corporativos
- futuros apps mobile

---

## 🗄️ Banco de Dados

- PostgreSQL
- SQLAlchemy ORM

Tabela principal:
- `analises`
  - resultado
  - modelo mais confiante
  - confiança
  - detalhes dos modelos

---

# 🧪 5. Testes e Qualidade

## ✅ Testes automatizados

- Pytest
- Testes unitários e de integração
- Testes da API
- Testes do dashboard
- Teste de Carga com Locust

---

## 📊 Cobertura

- +80% coverage
- Relatórios via `coverage.py`

---

## 🔄 CI/CD

GitHub Actions:
- Execução automática de testes
- Geração de coverage

Codacy:
- Análise de qualidade de código
- Monitoramento contínuo

---

# 💻 6. Tecnologias

- Python
- Scikit-learn
- OpenCV
- Streamlit
- FastAPI
- PostgreSQL
- SQLAlchemy
- Plotly
- Pandas / NumPy

---

# 📊 7. Modelos

| Modelo | Accuracy |
|--------|---------|
| Random Forest | **0.96** |
| KNN | 0.95 |
| SVM | 0.93 |
| Decision Tree | 0.92 |

---

## 🏆 Estratégia

- Ensemble (votação)
- Modelo mais confiante
- Melhor robustez geral

---

# 🧠 8. Metodologia

## 📷 Features

- LBP (Local Binary Pattern)
- Haralick (GLCM)
- Estatísticas de textura

---

## 🤖 Modelos

- Random Forest
- SVM
- KNN
- Decision Tree

---

# 🚀 9. Diferenciais

✔ Arquitetura profissional  
✔ API integrada  
✔ Banco de dados real  
✔ Testes automatizados  
✔ Dashboard completo  
✔ Exportação avançada  
✔ Pipeline de dados estruturado  

---

# 🔮 10. Roadmap

- CNN (Deep Learning)
- Heatmaps (Explainability)
- ROC / AUC
- Deploy em cloud
- Autenticação de usuários
- Multi-tenant SaaS

---

# ▶️ 11. Como Executar

```bash
git clone https://github.com/kaoan-eduardo/IFPR.git
cd IFPR

python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### ▶️ Rodar aplicação

```bash
streamlit run app.py
```

### ▶️ Rodar API

```bash
uvicorn api.main:app --reload
```

### ▶️ Rodar testes

```bash
pytest
```


### ▶️ Coverage

```bash
coverage run -m pytest
coverage report -m
```

### ▶️ Teste de carga

```bash
locust
```

---

# 📌 Autor
Kaoan Eduardo Pigaiani de Matos
IFPR - Gestão de TI

---