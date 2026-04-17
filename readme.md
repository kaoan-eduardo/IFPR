<p align="center">
  <img src="assets/logo_ifpr_icon.png" width="60"/>
  <b style="font-size: 28px;">IFPR - Identificação de Fissuras em Pavimentos Rodoviários</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10--3.14-blue"/>
  <img src="https://img.shields.io/badge/Status-Em%20Desenvolvimento-orange"/>
  <img src="https://img.shields.io/badge/Machine%20Learning-Ativo-green"/>
  <img src="https://img.shields.io/badge/Interface-Streamlit-red"/>
</p>

---

# 📌 1. Identificação

## 🎨 Identidade Visual

<p align="center">
  <img src="assets/logo_ifpr_dark.png" width="480"/>
</p>

A identidade visual do projeto representa a aplicação de visão computacional na análise de pavimentos.

---

## 🌐 Redes Sociais
<p>
  <a href="https://github.com/kaoan-eduardo">GitHub</a> •
  <a href="https://www.linkedin.com/in/kaoan-matos-a2a797244/">LinkedIn</a>
</p>

---

## 👥 Organização da Equipe

| Nome | Papel | Responsabilidade |
|------|------|----------------|
| Kaoan Eduardo | Desenvolvedor | Desenvolvimento do modelo, tratamento de dados, interface |

📢 Comunicação:
- Trello
- GitHub

---

## 📅 Data de criação
Abril de 2026

---

# 🧠 2. Concepção

## 📌 Visão Geral
Sistema inteligente capaz de identificar automaticamente rachaduras em pavimentos utilizando visão computacional e Machine Learning.

---

## 🎯 Objetivo
Classificar imagens como:
- Rachado
- Não rachado

---

## 📦 Escopo do Produto

### 🧾 Descrição do Produto
Aplicação em Python que:
- Recebe imagens
- Analisa usando ML
- Exibe os resultados dos modelos

---

### 🚀 Principais Entregas
- Dataset tratado
- Modelos treinados
- Pipeline com múltiplas features
- Interface em Streamlit

---

### ✅ Critérios de Aceite

**Qualitativos:**
- Interface funcional
- Classificação correta visualmente

**Quantitativos:**
- Acurácia mínima: 70%+

---

## ⚠️ Matriz de Riscos

| ID | Tipo | Descrição | Impacto | Probabilidade | Resposta |
|----|------|----------|--------|--------------|----------|
| R1 | Técnico | Dataset ruim | Alto | Médio | Limpeza |
| R2 | Técnico | Overfitting | Alto | Médio | Validação |
| R3 | Projeto | Tempo | Médio | Alto | Kanban |

---

# 🎨 3. Design do Software

Sistema focado em simplicidade e rapidez na análise.

---

# 💻 4. Desenvolvimento

## ⚙️ Processo
Kanban

---

## 🛠️ Tecnologias
- Python
- OpenCV
- Scikit-learn
- Streamlit
- NumPy
- Pandas

---

# 📊 5. Avaliação do Modelo

## 🧠 Modelos Testados

| Modelo | Accuracy |
|--------|---------|
| Random Forest | **0.96** |
| KNN | 0.95 |
| SVM | 0.93 |
| Decision Tree | 0.92 |

---

## 🏆 Estratégia Final

O sistema utiliza múltiplos modelos para análise comparativa das imagens.

Para cada imagem:
- Cada modelo gera sua própria predição
- O sistema contabiliza os votos entre as classes
- A interface apresenta a distribuição dos votos
- O modelo com maior confiança também é destacado

---

## 📈 Interpretação

- Alta precisão nos modelos avaliados
- Comparação entre diferentes algoritmos de classificação
- Visualização clara da votação entre classes
- Apoio à análise por meio do destaque do modelo mais confiante

---

# 🧪 6. Metodologia

## 📷 Extração de Features

A abordagem adotada combina descritores clássicos de textura com características estatísticas, visando melhorar a separação entre as classes analisadas.

- **LBP (Local Binary Pattern)**: captura padrões locais de textura
- **Haralick (GLCM)**: extrai características estatísticas baseadas na matriz de coocorrência
- **Features estatísticas adicionais**:
  - Média
  - Variância
  - Desvio padrão
  - Contraste
  - Homogeneidade

Essas features formam um vetor robusto de características para apoiar os algoritmos de classificação.

---

## 🤖 Modelos Utilizados

O sistema utiliza múltiplos algoritmos de Machine Learning:

- Random Forest
- Decision Tree
- K-Nearest Neighbors (KNN)
- Support Vector Machine (SVM)

---

## ⚙️ Estratégia de Classificação

A aplicação apresenta os resultados de múltiplos modelos de Machine Learning para uma mesma imagem.

A interface exibe:

- Os votos dos modelos entre **Rachado** e **Não Rachado**
- A comparação de confiança entre os modelos
- O modelo mais confiante como referência visual

---

# 🚀 7. Trabalhos Futuros

- Uso de CNN
- Aumento do dataset
- Deploy em cloud
- Integração com sistemas rodoviários

---

# ▶️ Como Executar

```bash
git clone https://github.com/kaoan-eduardo/PrivRepo.git
cd seu-projeto
pip install -r requirements.txt
streamlit run app.py
```