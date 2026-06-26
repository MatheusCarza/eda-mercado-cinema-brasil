# Análise Exploratória do Mercado de Cinema Brasileiro

Análise exploratória dos dados de bilheteria do mercado cinematográfico nacional, utilizando dados públicos da **ANCINE (Agência Nacional do Cinema)**, cobrindo o período de **janeiro de 2014 a junho de 2026**.

## Perguntas Investigadas

- **Impacto da pandemia de COVID-19:** Como e quando o mercado foi afetado? Qual a magnitude da queda?
- **Recuperação do mercado:** O público retornou aos patamares pré-pandemia? Em que ritmo?
- **Filmes premiados:** Qual o impacto de obras como *Ainda Estou Aqui* (indicado ao Oscar 2025) e *Agente Secreto* na bilheteria do cinema nacional?
- **Cinema nacional vs. estrangeiro:** Qual a participação de mercado do cinema brasileiro ao longo dos anos? Como ela evolui em momentos de destaque?
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

O diretório `data/` contém **150 arquivos CSV** (um por mês), com separador `;` e encoding UTF-8. Por serem arquivos grandes (~5 GB no total), a pasta `data/` está listada no `.gitignore` e **não é versionada** no repositório.

## Estrutura do Projeto

```
eda-mercado-cinema-brasil/
├── data/                   # CSVs da ANCINE (não versionados)
├── analise.ipynb           # Notebook principal com toda a análise
├── requirements.txt        # Dependências Python
├── .venv/                  # Ambiente virtual (não versionado)
├── .gitignore
└── README.md
```

## Como Executar

### 1. Clonar o repositório e entrar na pasta

```bash
git clone https://github.com/<seu-usuario>/eda-mercado-cinema-brasil.git
cd eda-mercado-cinema-brasil
```

### 2. Baixar os dados

Os dados da ANCINE estão disponíveis publicamente no portal:
**https://dados.gov.br/dados/conjuntos-dados/bilheteria-diaria-de-obras-cinematograficas**

Baixe os arquivos mensais de bilheteria diária por distribuidoras e coloque-os dentro da pasta `data/`.

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

Abra o arquivo `analise.ipynb` no navegador.

## Dependências Principais

| Biblioteca | Uso |
|------------|-----|
| `pandas` | Manipulação e agregação dos dados |
| `numpy` | Operações numéricas |
| `matplotlib` | Visualizações base |
| `seaborn` | Visualizações estatísticas |
| `jupyter` / `notebook` | Ambiente de análise interativo |

## Fonte dos Dados

**ANCINE — Agência Nacional do Cinema**
Portal Brasileiro de Dados Abertos: https://dados.gov.br

Os dados são públicos e disponibilizados sob licença aberta.

## Licença

Este projeto (código e análise) está disponível sob a licença **MIT**.
Os dados são de domínio público, fornecidos pela ANCINE via Portal Dados.gov.br.
