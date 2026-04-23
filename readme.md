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

# 🧩 3. Funcionalidades do Sistema

A aplicação evoluiu para além de um classificador, tornando-se uma **plataforma completa de análise de pavimentos**.

---

## 📷 Upload Único

Permite análise individual com:

- Classificação por múltiplos modelos
- Sistema de votação entre classificadores
- Identificação do modelo mais confiante
- Exibição de confiança (%)
- Comparação visual entre modelos
- Exportação do relatório em PDF

---

## 🗂️ Análise em Lote

Processamento de múltiplas imagens com alta performance.

### 🔹 Modos de entrada:
- Upload múltiplo (pequenos volumes)
- Upload via arquivo `.zip` (grandes volumes)

### 🔹 Recursos:
- Processamento de milhares de imagens
- Barra de progresso em tempo real
- Resumo automático do lote:
  - Total de imagens
  - Com rachaduras
  - Em bom estado
  - Inválidas
- Tabela resumida
- Galeria otimizada (limitada)
- Detalhamento parcial para performance

### 🔹 Otimizações:
- Limite de renderização de imagens
- Redução de uso de memória
- Processamento progressivo

---

## 📊 Dashboard de Análises

Painel interativo com visão global.

### 🔹 Métricas:
- Total de análises
- Com rachaduras
- Bom estado
- Confiança média
- Taxa de incerteza

### 🔹 Visualizações:
- Gráfico de distribuição
- Frequência por modelo
- Evolução temporal

### 🔹 Exportação:
- 📄 PDF
- 📊 Excel (compatível com Power BI)

---

## 🧠 Avaliação dos Modelos

Baseada em Cross Validation.

### 🔹 Métricas:
- Accuracy
- Precision
- Recall
- F1-score
- Specificity

### 🔹 Recursos:
- Comparação entre modelos
- Análise por fold
- Melhor modelo automático
- Matriz de confusão interativa

---

# 🏗️ 4. Arquitetura do Sistema

Arquitetura modular inspirada em Arquitetura em camadas:
```
src/
├── core/ # Machine Learning
├── services/ # Regras de negócio
├── ui/
│ ├── tabs/ # Cada aba separada
│ ├── components/
│ └── styles
├── utils/
```

### 🔹 Destaque
Separação por abas e serviços permite:
- escalabilidade
- manutenção facilitada
- evolução contínua

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
- Plotly

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

- Ensemble manual
- Votação entre modelos
- Modelo mais confiante

---

## 📈 Interpretação

- Alta precisão
- Robustez
- Boa generalização

---

# 🧪 7. Metodologia

## 📷 Features

- LBP (Local Binary Pattern)
- Haralick (GLCM)
- Estatísticas:
  - Média
  - Desvio padrão
  - Contraste
  - Homogeneidade

---

## 🤖 Modelos

- Random Forest
- Decision Tree
- KNN
- SVM

---

# 🚀 8. Diferenciais

✔ Sistema completo (não só modelo)  
✔ Processamento em lote otimizado  
✔ Interface interativa  
✔ Exportação de dados  
✔ Arquitetura modular  
✔ Pronto para integração com BI  

---

# 🔮 9. Trabalhos Futuros

- CNN
- Heatmap de explicabilidade
- ROC / AUC
- API com FastAPI
- Deploy em cloud

---

# ▶️ Como Executar

```bash
git clone https://github.com/kaoan-eduardo/IFPR.git
cd IFPR
pip install -r requirements.txt
streamlit run app.py
```