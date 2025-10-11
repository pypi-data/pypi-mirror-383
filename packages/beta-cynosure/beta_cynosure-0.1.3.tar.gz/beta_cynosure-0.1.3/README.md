# beta-Cynosure  
Biblioteca Python para extração e análise de dados financeiros públicos da CVM (Comissão de Valores Mobiliários).  

Permite baixar, limpar e consolidar DFP (demonstrações anuais), ITR (trimestrais) e FRE (estrutura acionária) de companhias abertas brasileiras.

---

## Funcionalidade
- Baixa os arquivos diretamente do portal dados.cvm.gov.br  
- Processa automaticamente:
  - DFP: dados anuais  
  - ITR: dados trimestrais  
  - FRE: número total de ações e ações em circulação  
- Retorna tudo como DataFrames Pandas prontos para uso  
- Permite consultas por:
  - Um único ano (ex: `2024`)  
  - Intervalo de anos (ex: `"2020-2024"`)  
  - Empresa específica (ex: `["PETR"]`)  
  - Grupo de empresas (ex: `["PETR", "VALE", "ITAU"]`)

---

## Instalação
```bash
pip install beta-cynosure
```

## Exemplo de uso básico
```
from beta_cynosure import get_dfp, get_itr, get_fre, get_all

# DFP: demonstrações anuais (um ou mais anos)
dfp = get_dfp("2023-2024", ["PETR"])
print(dfp.head())

# ITR: dados trimestrais
itr = get_itr(2024, ["PETR", "VALE"])

# FRE: estrutura acionária
fre = get_fre(2023, ["ITAU"])

# Todos de uma vez
data = get_all("2023-2024", ["PETR", "VALE"])
print(data["dfp"].shape, data["itr"].shape, data["fre"].shape)
```
## Estrutura dos DataFrames

| Tipo | Descrição                                               |
| ---- | ------------------------------------------------------- |
| DFP  | Demonstrações financeiras anuais (Balanço, DRE, etc.)   |
| ITR  | Informações trimestrais (dados resumidos por trimestre) |
| FRE  | Quantidade total de ações e ações em circulação         |

## Exemplo de análise

Somar o "Ativo Total" de 2023 e 2024
```
target = dfp[dfp["DS_CONTA"] == "Ativo Total"]
by_year = target.groupby("YEAR")["VL_CONTA"].sum()
soma = by_year.get(2023, 0) + by_year.get(2024, 0)
print("Ativo Total (2023 + 2024):", soma)
```
---

## Exportação de dados
Os resultados obtidos pelas funções `get_dfp`, `get_itr`, `get_fre` ou `get_all` podem ser exportados facilmente em **CSV** ou **JSON** usando o módulo `export`.

```
from beta_cynosure import get_all, save

# Busca dados da Petrobras entre 2023 e 2024
data = get_all("2023-2024", ["PETR"])

# Exporta em formato JSON
save(data, prefix="PETR", period="2023-2024", format="json")

# Ou exporta em formato CSV
save(data, prefix="PETR", period="2023-2024", format="csv")
```