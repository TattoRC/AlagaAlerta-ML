# Uso de IA nesta entrega

Seguindo o combinado da GS ("IA como copiloto"), aqui estão os prompts usados na parte de Machine Learning. A ferramenta foi o Claude (Anthropic), usado para pesquisar as fontes de dados, revisar o código e discutir as escolhas de modelo. A equipe revisou todas as decisões e sabe explicar cada linha do notebook e dos scripts.

| # | Prompt (resumido) | Para que foi usado | O que a equipe conferiu |
|---|---|---|---|
| 1 | "Leia o que está sendo pedido em IA no PDF da GS e faça só o que é pedido nessa matéria" | levantar os entregáveis e os 6 critérios de nota da disciplina | conferimos o enunciado slide por slide (inclusive o vídeo, que aparece no slide 31 e não no 33) |
| 2 | "O tema é o AlagaAlerta: sensor ultrassônico no ESP32, alertas por bairro, app com pontos de risco; o ML prevê risco de alagamento com chuva do INMET/CGE. O que dá para usar e o que não dá?" | separar o que tem dado real (chuva do INMET, alagamentos do CGE) do que é simulado (sensor no Wokwi, relatos do app) | regra da disciplina: dado simulado não é aceito |
| 3 | Pesquisa das fontes: formato dos arquivos do INMET, página de alagamentos do CGE, classificação "transitável/intransitável" | escrever `coleta/baixar_inmet.py` e `coleta/coletar_cge.py` | abrimos as páginas do CGE e os CSVs do INMET para conferir colunas e unidades |
| 4 | Escolha do modelo, da validação e das métricas para classe desbalanceada | justificativa do XGBoost, validação cruzada por ano, precisão média como métrica principal | rodamos o notebook do zero e conferimos os números do relatório com as saídas |

Decisões tomadas pela equipe ao longo do caminho:
- tirar a estação de Barueri (A755) por falta de dados em 2021, 2024 e 2025;
- tirar a umidade de Interlagos (A771), porque o sensor ficou travado em 100% em boa parte de 2021 a 2023;
- conferir o pico de 82 mm/h (24/01/2025) com os alagamentos do CGE daquele dia antes de manter o valor;
- dividir treino e teste por ano (2019-2023 / 2024-2025) em vez de sortear as linhas;
- não usar `scale_pos_weight`, para a probabilidade continuar com sentido de "chance".
