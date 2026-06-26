# Análise Exploratória do Mercado de Cinema Brasileiro

Análise exploratória dos dados de bilheteria do mercado cinematográfico nacional, utilizando dados públicos da **ANCINE (Agência Nacional do Cinema)**, cobrindo o período de **janeiro de 2014 a junho de 2026**.

> ⚠️ Os dados de 2026 são parciais — cobrem apenas de janeiro a junho.

## Perguntas Investigadas

- **Impacto da pandemia de COVID-19:** Como e quando o mercado foi afetado? Qual a magnitude da queda?
- **Recuperação do mercado:** O público retornou aos patamares pré-pandemia? Em que ritmo?
- **Filmes premiados:** Qual o impacto de *Ainda Estou Aqui* (1º filme brasileiro a vencer o Oscar de Melhor Filme Internacional) e *O Agente Secreto* (Cannes 2025 — Melhor Diretor e Melhor Ator) na bilheteria nacional?
- **Cinema nacional vs. estrangeiro:** Qual a participação de mercado do cinema brasileiro ao longo dos anos?
- **Sazonalidade:** Existem padrões sazonais consistentes no consumo de cinema?
- **Distribuição geográfica:** Como o público se distribui entre estados e regiões?

## Dados

Os dados são provenientes do **portal de dados abertos da ANCINE** e registram a bilheteria diária por sala de cinema em todo o Brasil.

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

> **Nota:** Os dados registram público (número de espectadores), não receita financeira.

O diretório `data/` contém **150 arquivos CSV** (um por mês), com separador `;` e encoding UTF-8. Por serem arquivos grandes (~4,5 GB no total), a pasta `data/` está listada no `.gitignore` e **não é versionada** no repositório.

## Estrutura do Projeto

```
eda-mercado-cinema-brasil/
├── data/                        # CSVs da ANCINE (não versionados — ~4,5 GB)
├── notebooks/
│   └── analise.ipynb            # Notebook principal com toda a análise
├── outputs/
│   ├── figures/                 # Gráficos exportados (.png)
│   └── processados/             # Dados agregados para reutilização (.csv)
├── requirements.txt             # Dependências Python
├── .venv/                       # Ambiente virtual (não versionado)
├── .gitignore
└── README.md
```

## Análises Realizadas no Notebook

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
| 8 | Análise dos filmes premiados (*Ainda Estou Aqui* e *O Agente Secreto*) |
| 9 | Distribuição geográfica por estado e município |
| 10 | Sazonalidade histórica do mercado |

## Como Executar

### 1. Clonar o repositório

```bash
git clone https://github.com/MatheusCarza/eda-mercado-cinema-brasil.git
cd eda-mercado-cinema-brasil
```

### 2. Baixar os dados

Os dados da ANCINE estão disponíveis publicamente:

**https://dados.gov.br/dados/conjuntos-dados/bilheteria-diaria-de-obras-cinematograficas**

Baixe os arquivos mensais de **bilheteria diária por distribuidoras** e coloque-os dentro da pasta `data/`.

### 3. Criar e ativar o ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# ou
.venv\Scripts\activate      # Windows
```

### 4. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 5. Abrir o Jupyter Notebook

```bash
jupyter notebook
```

Abra `notebooks/analise.ipynb` e execute **Run All**.

> O carregamento completo dos dados pode levar alguns minutos. O DataFrame ocupa aproximadamente 1,5–2 GB em RAM com as otimizações de memória aplicadas.

## Dependências Principais

| Biblioteca | Uso |
|------------|-----|
| `pandas` | Manipulação e agregação dos dados |
| `numpy` | Operações numéricas |
| `matplotlib` | Visualizações |
| `seaborn` | Visualizações estatísticas |
| `jupyter` / `notebook` | Ambiente de análise interativo |

## Fonte dos Dados

**ANCINE — Agência Nacional do Cinema**
Portal Brasileiro de Dados Abertos: https://dados.gov.br

Os dados são públicos e disponibilizados sob licença aberta.

## Licença

Este projeto (código e análise) está disponível sob a licença **MIT**.
Os dados são de domínio público, fornecidos pela ANCINE via Portal Dados.gov.br.
