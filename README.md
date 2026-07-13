# Análise Exploratória do Mercado de Cinema Brasileiro

EDA da bilheteria do cinema brasileiro com dados públicos da ANCINE, cobrindo janeiro de 2014 a junho de 2026 (2026 é parcial, só até junho).

## O que a análise investiga

- Como a pandemia afetou o mercado e qual foi a magnitude da queda
- Se o público voltou aos níveis pré-pandemia, e em que ritmo
- O impacto de *Ainda Estou Aqui* (primeiro filme brasileiro a ganhar o Oscar de Melhor Filme Internacional) e *O Agente Secreto* (Cannes 2025) na bilheteria nacional
- A participação do cinema nacional frente ao estrangeiro ao longo dos anos
- Padrões sazonais no consumo de cinema
- Como o público se distribui entre estados e municípios

## Dados

Os dados vêm do portal de dados abertos da ANCINE e registram a bilheteria diária por sala de cinema em todo o Brasil.

| Campo | Descrição |
|-------|-----------|
| `DATA_EXIBICAO` | Data da exibição (DD/MM/AAAA) |
| `TITULO_ORIGINAL` / `TITULO_BRASIL` | Título original e título no Brasil |
| `CPB_ROE` | Registro ANCINE — prefixo `B` = nacional, `E` = estrangeiro |
| `PAIS_OBRA` | País de origem da obra |
| `PUBLICO` | Público diário por sala |
| `NOME_SALA` | Nome da sala de cinema |
| `MUNICIPIO_SALA_COMPLEXO` / `UF_SALA_COMPLEXO` | Município e estado da sala |
| `RAZAO_SOCIAL_DISTRIBUIDORA` | Distribuidora responsável |

Os dados registram público (número de espectadores), não receita.

`data/` tem 150 CSVs, um por mês, separador `;`, encoding UTF-8. Como o total dá uns 4,5 GB, a pasta está no `.gitignore` e não é versionada.

## Estrutura

```
eda-mercado-cinema-brasil/
├── data/                        # CSVs da ANCINE (não versionados — ~4,5 GB)
├── notebooks/
│   └── analise.ipynb            # notebook principal
├── outputs/
│   ├── figures/                 # gráficos exportados (.png)
│   └── processados/             # dados agregados, reaproveitados pelo dashboard
├── app.py                       # dashboard Streamlit
├── requirements.txt
├── .venv/
├── .gitignore
└── README.md
```

## Seções do notebook

| Seção | Conteúdo |
|-------|----------|
| 0 | Setup, imports e configurações |
| 1 | Carregamento otimizado dos 150 CSVs (~20,9 milhões de linhas) |
| 2 | Limpeza e padronização dos dados |
| 3 | Visão geral do dataset |
| 4 | Evolução temporal do mercado (2014–2026) |
| 5 | Impacto da pandemia de COVID-19 |
| 6 | Recuperação pós-pandemia |
| 7 | Cinema nacional vs. estrangeiro |
| 8 | Filmes premiados (*Ainda Estou Aqui* e *O Agente Secreto*) |
| 9 | Distribuição geográfica por estado e município |
| 10 | Sazonalidade histórica |

## Como rodar

**1. Clone o repositório**

```bash
git clone https://github.com/MatheusCarza/eda-mercado-cinema-brasil.git
cd eda-mercado-cinema-brasil
```

**2. Baixe os dados**

Estão publicamente disponíveis em https://dados.gov.br/dados/conjuntos-dados/bilheteria-diaria-de-obras-cinematograficas — pegue os arquivos mensais de bilheteria diária por distribuidoras e coloque-os em `data/`.

**3. Ambiente virtual e dependências**

```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

**4. Abra o notebook**

```bash
jupyter notebook
```

Abra `notebooks/analise.ipynb` e rode tudo (Run All). O carregamento completo pode levar alguns minutos — o DataFrame ocupa de 1,5 a 2 GB em RAM com as otimizações aplicadas.

## Dashboard

`app.py` é um dashboard em Streamlit com filtros de ano, origem (nacional/estrangeiro) e estado, dividido em 6 abas: Visão Geral, Pandemia & Recuperação, Nacional vs. Estrangeiro, Filmes Premiados, Distribuição Geográfica e Sazonalidade.

Ele lê só os CSVs já agregados em `outputs/processados/` (gerados pelo notebook) — não precisa dos dados brutos pra rodar.

```bash
source .venv/bin/activate
streamlit run app.py
```

Abre em `http://localhost:8501`. Se faltar algum CSV em `outputs/processados/`, a aba correspondente avisa na barra lateral — nesse caso é só rodar o notebook inteiro de novo pra gerá-los.

## Dependências principais

| Biblioteca | Uso |
|------------|-----|
| `pandas` | Manipulação e agregação dos dados |
| `numpy` | Operações numéricas |
| `matplotlib` / `seaborn` | Visualizações no notebook |
| `jupyter` / `notebook` | Ambiente de análise |
| `streamlit` | Dashboard |
| `plotly` | Gráficos interativos do dashboard |

## Fonte dos dados

ANCINE — Agência Nacional do Cinema, via Portal Brasileiro de Dados Abertos (https://dados.gov.br). Dados públicos, licença aberta.

## Licença

MIT para o código e a análise. Os dados são de domínio público, fornecidos pela ANCINE.
