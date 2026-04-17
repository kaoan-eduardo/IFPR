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

# 🏗️ 3. Arquitetura do Sistema

O projeto foi desenvolvido utilizando uma **arquitetura em camadas (Layered Architecture)**, inspirada em princípios de **Clean Architecture**, garantindo organização e escalabilidade:

```
src/
├── core/ # Lógica de Machine Learning
├── services/ # Orquestração
├── ui/ # Interface Streamlit
├── utils/ # Funções auxiliares
```

### 🔹 Core
- Extração de features (LBP, Haralick, estatísticas)
- Predição com modelos treinados

### 🔹 Services
- Intermediação entre interface e modelo

### 🔹 UI
- Upload de imagens
- Exibição de resultados
- Gráficos e comparações

### 🔹 Utils
- Formatação
- Votação entre modelos

---

# 🎨 4. Design do Software

Sistema focado em:
- Simplicidade
- Rapidez
- Clareza visual

---

# 💻 5. Desenvolvimento

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

# 📊 6. Avaliação do Modelo

## 🧠 Modelos Testados

| Modelo | Accuracy |
|--------|---------|
| Random Forest | **0.96** |
| KNN | 0.95 |
| SVM | 0.93 |
| Decision Tree | 0.92 |

---

## 🏆 Estratégia Final

- Uso de múltiplos modelos
- Votação entre classificadores
- Destaque do modelo mais confiante

---

## 📈 Interpretação

- Alta precisão
- Comparação entre algoritmos
- Interface intuitiva

---

# 🧪 7. Metodologia

## 📷 Extração de Features

- **LBP** → padrões locais
- **Haralick (GLCM)** → textura
- **Features estatísticas**:
  - Média
  - Desvio padrão
  - Contraste
  - Homogeneidade

---

## 🤖 Modelos Utilizados

- Random Forest
- Decision Tree
- KNN
- SVM

---

# 🚀 8. Trabalhos Futuros

- CNN
- Aumento do dataset
- Deploy em cloud
- Integração com sistemas rodoviários

---

# ▶️ Como Executar

```bash
git clone https://github.com/kaoan-eduardo/IFPR.git
cd IFPR
pip install -r requirements.txt
streamlit run app.py
```