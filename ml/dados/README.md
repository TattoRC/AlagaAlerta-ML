# Dados usados no modelo

Todos os dados são **reais e públicos**, e nenhum foi simulado. Não há dado pessoal: o CGE publica só o endereço da via que alagou, e o INMET publica medições de estações meteorológicas.

Período: **01/01/2019 a 31/12/2025**.

```
dados/
├── README.md
└── brutos/
    ├── inmet/                  21 CSVs do INMET (3 estações x 7 anos), do jeito que vêm do portal
    ├── cge_alagamentos.csv     um ponto de alagamento por linha (coletado do site do CGE)
    ├── cge_dias.csv            todos os dias consultados no CGE e quantos pontos cada um teve
    └── cge_html/               cache das páginas baixadas (fora do git, ver .gitignore)
```

---

## 1. INMET: chuva, temperatura e umidade de hora em hora

- **Quem publica:** Instituto Nacional de Meteorologia (INMET)
- **Onde:** https://portal.inmet.gov.br/dadoshistoricos (um `.zip` por ano com todas as estações automáticas do país, em `https://portal.inmet.gov.br/uploads/dadoshistoricos/AAAA.zip`)
- **Baixado em:** 17/11/2026, com `coleta/baixar_inmet.py`

| Código | Estação | Região da capital | Latitude | Longitude | Altitude | Em operação desde | Usada no modelo? |
|---|---|---|---|---|---|---|---|
| A701 | São Paulo - Mirante de Santana | zona norte | -23,496 | -46,620 | 786 m | 25/07/2006 | sim |
| A771 | São Paulo - Interlagos | zona sul | -23,724 | -46,678 | 771 m | 14/03/2018 | sim |
| A755 | Barueri | oeste, fora da capital | -23,524 | -46,869 | 777 m | 29/03/2011 | **não** (ver abaixo) |

**Formato do arquivo:** 8 linhas de cabeçalho com os dados da estação, depois uma linha por hora. Separador `;`, vírgula decimal, codificação latin-1, data `AAAA/MM/DD` e hora em **UTC** (`0000 UTC`). Quando o sensor não mede, o valor vem como `-9999`.

**Colunas aproveitadas:**

| Coluna original | Nome no notebook | Unidade |
|---|---|---|
| PRECIPITAÇÃO TOTAL, HORÁRIO | `chuva` | mm na hora |
| TEMPERATURA DO AR - BULBO SECO, HORARIA | `temperatura` | °C |
| UMIDADE RELATIVA DO AR, HORARIA | `umidade` | % |

**Por que a A755 (Barueri) ficou de fora:** ela ficou sem medir chuva em boa parte do período. Faltam 95,3% das horas de 2021, 89,0% das de 2024 e 59,1% das de 2025. Como 2024 e 2025 são o conjunto de teste, o modelo dependeria de uma variável que quase não existe justamente na hora de ser avaliado. As outras duas estações têm no máximo 7,4% de horas sem chuva medida em qualquer ano (A701 em 2023).

**Umidade de Interlagos (A771) também ficou de fora:** o sensor ficou travado em exatamente 100% em 18,6% das horas de 2021, 39,7% de 2022 e 32,3% de 2023, e voltou ao normal em 2024. A chuva e a temperatura da A771 não têm esse problema e continuam no modelo.

**Tratamento no notebook:**
1. `-9999` vira valor faltando.
2. Hora convertida de UTC para o horário de São Paulo (`America/Sao_Paulo`, que já considera o horário de verão de jan-fev/2019).
3. Agregação por dia: total de chuva, maior chuva em 1 hora, maior chuva em 3 horas seguidas, temperatura máxima e umidade média.
4. Dia com menos de 20 horas de chuva medida fica com a chuva vazia, para não contar um total incompleto como se fosse real.

---

## 2. CGE: pontos de alagamento

- **Quem publica:** Centro de Gerenciamento de Emergências Climáticas (CGE), da Prefeitura de São Paulo
- **Onde:** https://www.cgesp.org/v3/alagamentos.jsp (consulta por data: `?dataBusca=DD/MM/AAAA&enviaBusca=Buscar`)
- **Baixado em:** 17/11/2026, com `coleta/coletar_cge.py`
- **Volume:** 2.557 dias consultados, 5.647 pontos de alagamento em 597 dias diferentes

O CGE não oferece API nem arquivo para download. O script consulta a página de alagamentos um dia por vez, guarda o HTML e extrai os pontos. O site bloqueia temporariamente (HTTP 403) quem faz muitas consultas seguidas, então o script espera 1,5 s entre uma página e outra e pausa alguns minutos se o bloqueio acontecer.

Segundo o próprio CGE, os pontos são registrados a partir do monitoramento da equipe do centro, que funciona 24 horas, junto com observadores locais: agentes da CET, funcionários das subprefeituras e da Defesa Civil.

**Colunas de `cge_alagamentos.csv`:**

| Coluna | Exemplo | Descrição |
|---|---|---|
| `data` | 2021-02-17 | dia da consulta no site (data do alagamento) |
| `regiao` | Zona Norte | uma das 6 regiões do CGE: Centro, Zona Norte, Zona Sul, Zona Leste, Zona Oeste, Zona Sudeste |
| `subprefeitura` | Vila Maria/ Vila Guilherme | subprefeitura do ponto |
| `inicio`, `fim` | 16:57, 17:50 | horário em que o alagamento começou e terminou |
| `local` | R. CHICO PONTES (VILA GUILHERME) | via, e às vezes o bairro entre parênteses |
| `sentido`, `referencia` | UNICO, AV GUILHERME | sentido da via e ponto de referência |
| `situacao` | Inativo Intransitável | classificação do CGE (abaixo) |

**Classificação usada pelo CGE** (página "Entenda a classificação dos pontos de alagamento"):
- *Transitável*: a água não toma todas as faixas, e os carros ainda passam.
- *Intransitável*: a água toma todas as faixas e o trânsito fica totalmente bloqueado.
- *Ativo / Inativo*: se o alagamento ainda existia ou já tinha terminado no momento da consulta.

**`cge_dias.csv`** tem uma linha para cada dia consultado, inclusive os dias sem nenhum alagamento. Com ele dá para ter certeza de que um dia sem pontos é um dia em que nada alagou, e não um dia que falhou no download.

**Conferência:** a página do CGE mostra o total de pontos de cada subprefeitura ("3 pts."). O script compara esse total com o número de pontos que conseguiu ler e avisa se não bater. Em toda a coleta, os totais bateram em todos os 2.557 dias. Houve só 4 linhas repetidas, removidas no notebook.

---

## 3. Tabela final (montada no notebook)

Uma linha por **dia × região** (6 regiões). Alvo: `alagou` = 1 se o CGE registrou pelo menos um ponto naquela região naquele dia.

| Variável | De onde vem |
|---|---|
| `chuva_dia_A701`, `chuva_dia_A771` | chuva total do dia em cada estação (mm) |
| `chuva_max_1h_*`, `chuva_max_3h_*` | maior chuva em 1 hora e em 3 horas seguidas, no dia (mm) |
| `temp_max_A701`, `temp_max_A771` | temperatura máxima do dia (°C) |
| `umidade_media_A701` | umidade relativa média do dia (%), só do Mirante |
| `chuva_maior_estacao` | o maior total do dia entre as duas estações |
| `chuva_ontem`, `chuva_3d_antes`, `chuva_7d_antes` | chuva dos dias anteriores (média das duas estações) |
| `mes` | mês do ano |
| `reg_*` | região do CGE em formato 0/1 |

---

## 4. Como baixar tudo de novo

```bash
pip install -r requirements.txt
python coleta/baixar_inmet.py 2019 2025       # ~700 MB de download, guarda só ~16 MB
python coleta/coletar_cge.py 2019-01-01 2025-12-31   # ~2.500 páginas, pouco mais de 1 hora
```

Os dois comandos rodam de dentro da pasta `ml/`.
