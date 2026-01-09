# Dashboard de Saúde Pública - Nascidos Vivos e Óbitos

Dashboard interativo para análise de dados de nascidos vivos e óbitos infantis por município e estado brasileiro.

## 📁 Estrutura do Projeto

```
RUBENS/
├── data/
│   ├── input/               # Planilhas de entrada
│   │   └── DR_Rubens.xlsx
│   └── output/              # JSONs processados
│       ├── nascidos_vivos/  # Dados de nascidos vivos por UF
│       │   ├── AC.json
│       │   ├── AL.json
│       │   └── ...
│       └── obitos/          # Dados de óbitos por UF
│           ├── AC.json
│           ├── AL.json
│           └── ...
├── src/
│   ├── converter_dados.py  # Script de extração dos dados
│   └── app.py              # Dashboard Streamlit
├── env/                    # Ambiente virtual Python
├── requirements.txt        # Dependências do projeto
├── README.md
└── converter_dados.py      # (arquivo antigo - pode remover)
```

## 🚀 Como Usar

### 1. Preparar o Ambiente

```bash
# Ativar o ambiente virtual
.\env\Scripts\activate

# Instalar dependências (se necessário)
pip install -r requirements.txt
```

### 2. Extrair Dados da Planilha

Primeiro, extraia os dados da planilha Excel para arquivos JSON:

```bash
python src\converter_dados.py
```

Este script irá:
- Ler a planilha `data/input/DR_Rubens.xlsx`
- Processar todas as abas de dados (NV e OB)
- Gerar arquivos JSON para cada UF em `data/output/`
- Exibir estatísticas do processamento

**Resultado esperado:** 
- ✅ 51 arquivos JSON gerados
- ✅ ~290.000 registros processados

### 3. Executar o Dashboard

```bash
streamlit run src\app.py
```

O dashboard abrirá automaticamente no navegador em `http://localhost:8501`

## 📊 Funcionalidades do Dashboard

### Filtros Disponíveis
- **Estado (UF):** Selecione o estado para análise
- **Tipo de Dado:** Escolha entre Nascidos Vivos ou Óbitos
- **Período:** Filtre por intervalo de anos
- **Municípios:** Compare municípios específicos

### Visualizações

#### 1. Evolução Temporal
- Gráfico de linha com evolução anual
- Comparação entre municípios selecionados
- Identificação de tendências

#### 2. Por Município
- Ranking dos Top 20 municípios
- Distribuição geográfica dos dados
- Gráfico de barras horizontal

#### 3. Ranking
- Top 10 municípios com maiores valores
- Estatísticas gerais (média, mediana, desvio padrão)
- Análise comparativa

#### 4. Dados Brutos
- Tabela completa com todos os registros filtrados
- Ordenação customizável
- Download em CSV

### Métricas Principais
- Total no período selecionado
- Total no último ano
- Média anual
- Número de municípios

## 🔧 Estrutura dos Dados

### Formato dos Arquivos JSON

Cada arquivo JSON contém registros no formato:

```json
[
  {
    "Municipio": "Nome do Município",
    "Ano": 2020,
    "Valor": 125,
    "UF": "SP",
    "Tipo": "Óbitos"
  },
  ...
]
```

### Campos

- **Municipio:** Nome do município
- **Ano:** Ano do registro (1996-2024)
- **Valor:** Quantidade de nascidos vivos ou óbitos
- **UF:** Sigla da Unidade Federativa
- **Tipo:** "Nascidos Vivos" ou "Óbitos"

## 📋 Requisitos

```
streamlit>=1.52.0
pandas>=2.3.0
plotly>=6.5.0
openpyxl>=3.1.0
```

## ⚠️ Observações

### Abas Ignoradas
O script ignora automaticamente:
- Abas com prefixo "CMI" (indicadores calculados)
- Abas sem dados estruturados
- Primeiras abas com gráficos

### Abas Problemáticas
Algumas abas podem não ser processadas:
- **SP NV:** Estrutura diferente
- **DF OB e DF NV:** Cabeçalho não encontrado

Essas abas precisam de verificação manual na planilha original.

## 🐛 Troubleshooting

### Erro: "Nenhum dado encontrado"
- Verifique se executou o `converter_dados.py` primeiro
- Confirme que a planilha está em `data/input/DR_Rubens.xlsx`

### Erro de encoding
- O script já configura UTF-8 automaticamente
- Se persistir, execute: `set PYTHONIOENCODING=utf-8`

### Performance lenta
- Os dados são cacheados automaticamente pelo Streamlit
- Primeira carga pode ser mais lenta
- Recarregamentos subsequentes são instantâneos

## 📝 Logs e Debug

Scripts de diagnóstico disponíveis em `src/`:
- `diagnostico.py` - Analisa estrutura da planilha
- `debug2.py` - Verifica tipos de colunas
- `debug3.py` - Debug da extração de anos

## 👨‍💻 Desenvolvimento

Para adicionar novos tipos de visualizações:
1. Edite `src/app.py`
2. Adicione novas tabs ou gráficos
3. Utilize os dados já filtrados em `df_filtrado`

## 📄 Licença

Projeto interno para análise de dados de saúde pública.

---

**Última atualização:** Janeiro 2026
