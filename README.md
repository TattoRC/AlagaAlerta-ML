# AlagaAlerta · Inteligência Artificial & Machine Learning

Global Solution 2026.2 CitizenTech · FIAP · Engenharia de Software, 3º ano

| Integrante | RM |
|---|---|
| Renato Luiz Cordão | 556403 |
| Vitor Victorino Couto | 554965 |
| Victoria Moura | 555474 |
| Fabricio Bettarello | 554638 |
| Enzo Miletta | 98677 |

## Ficha da CitizenTech

| | |
|---|---|
| **Nome** | AlagaAlerta |
| **Cidade** | São Paulo, nas 6 regiões usadas pelo CGE |
| **Cidadão beneficiado** | quem mora ou passa por ruas que alagam em dia de chuva |
| **Problema, em uma frase** | o morador só descobre que a rua alagou quando a água já chegou nele |
| **Como funciona** | sensor ultrassônico no ESP32 mede o nível da água em bueiros e córregos; o backend gera alertas por bairro; o app mostra os pontos de risco e recebe relatos dos moradores |
| **Parte de ML (este repositório)** | modelo XGBoost que estima o risco de alagamento em cada região a partir da chuva medida pelo INMET, treinado com os alagamentos registrados pelo CGE de 2019 a 2025 |
| **Indicador de impacto** | % dos alagamentos avisados com antecedência e % de alertas que se confirmam. No teste (2024-2025): 77% avisados, com 20% menos alarmes falsos que uma regra de chuva fixa |
| **ODS** | 11 (meta 11.5) e 13 (meta 13.1) |

## O que tem aqui

| Arquivo | Conteúdo |
|---|---|
| [`ml/RELATORIO_ML.md`](ml/RELATORIO_ML.md) | relatório, do problema à conclusão |
| [`ml/alagaalerta_ml.ipynb`](ml/alagaalerta_ml.ipynb) | notebook executado: dados, preparação, treino, busca de hiperparâmetros e resultados |
| [`ml/dados/README.md`](ml/dados/README.md) | fontes, links, período e descrição dos dados |
| [`ml/coleta/`](ml/coleta/) | scripts que baixam os dados do INMET e do CGE |
| [`ml/figuras/`](ml/figuras/) | gráficos gerados pelo notebook |
| [`ml/requirements.txt`](ml/requirements.txt) | bibliotecas e versões |
| [`ml/prompts.md`](ml/prompts.md) | registro do uso de IA, como pede a GS |

## Como rodar

```bash
cd ml
python -m venv .venv
.venv\Scripts\activate        # no Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
jupyter nbconvert --to notebook --execute --inplace alagaalerta_ml.ipynb
```

Os dados já estão na pasta `ml/dados/brutos/`, então não precisa baixar nada para rodar o notebook. Para baixar tudo de novo direto das fontes, veja [`ml/dados/README.md`](ml/dados/README.md).
