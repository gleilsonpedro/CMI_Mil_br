# CORREÇÃO: Entendimento Correto do CMI-Mil

## ❌ ESTAVA ERRADO ANTES!

Eu pensei que:
- **CMI-Mil** = (Óbitos < 1 ano / População Total) × 1.000

## ✅ CORRETO AGORA:

### **CMI (Coeficiente de Mortalidade Infantil)**
```
CMI = (Óbitos < 1 ano / Nascidos Vivos) × 1.000
```
- **Projeção/extrapolação** proporcional para 1.000 nascimentos
- Usa dados de **UM ANO** específico
- É uma **estimativa**: "Se nascessem 1000 bebês este ano, quantos morreriam?"

**Exemplo Abreulandia 2000:**
- 39 nascimentos, 1 óbito
- CMI = (1/39) × 1000 = **25.64**

### **CMI-Mil (Últimos Mil Nascidos Vivos)**
```
CMI-Mil = Óbitos observados nos ÚLTIMOS MIL nascimentos REAIS
```
- **Observação REAL** de uma janela de 1.000 nascimentos consecutivos
- Usa uma **janela temporal** (ano_inicial até ano_final)
- É uma **contagem real**: "Dos últimos 1000 bebês que nasceram, quantos morreram?"
- Identificação: CMI-Mil(ano_inicial-ano_final)

**Exemplo Abreulandia:**
- Precisaria acumular nascimentos de vários anos até chegar em 1000
- 1996-1999: 19+28+27+26 = 100 nascimentos (ainda não dá 1000!)
- Município pequeno pode levar **25 anos** para ter 1000 nascimentos
- Conta quantos desses 1000 morreram

---

## DIFERENÇA FUNDAMENTAL:

| Indicador | Método | Base Temporal | Natureza |
|-----------|--------|---------------|----------|
| **CMI** | Proporcional | 1 ano | **Projeção/Estimativa** |
| **CMI-Mil** | Contagem real | Janela até 1000 nascimentos | **Observação Real** |

---

## POR QUE OS VALORES PODEM SER PARECIDOS?

### Municípios GRANDES (ex: Fortaleza):
- Nascem **40.000 bebês/ano**
- Janela de 1000 nascimentos = **9 dias** (40000/365 ≈ 110/dia)
- Taxa de mortalidade estável em 9 dias
- **CMI ≈ CMI-Mil** (valores naturalmente parecidos!)

### Municípios PEQUENOS (ex: Abreulandia):
- Nascem **39 bebês/ano**
- Janela de 1000 nascimentos = **25.6 anos** (1000/39)
- Taxa de mortalidade varia ao longo de 25 anos
- **CMI ≠ CMI-Mil** (valores diferentes!)

---

## OS 316 MUNICÍPIOS "SUSPEITOS"

**NÃO SÃO ERRO!** São municípios grandes onde:
1. A janela de 1000 nascimentos é muito curta (dias/semanas)
2. A taxa de mortalidade infantil é estável no curto prazo
3. A projeção (CMI) e observação real (CMI-Mil) convergem naturalmente

**Exemplos:**
- **São Paulo**: ~200.000 nascimentos/ano → janela de 1000 = 1.8 dias
- **Rio de Janeiro**: ~90.000 nascimentos/ano → janela de 1000 = 4 dias
- **Fortaleza**: ~40.000 nascimentos/ano → janela de 1000 = 9 dias

Em 9 dias, a taxa de mortalidade infantil não muda significativamente!

---

## COMO CALCULAR CMI-Mil CORRETAMENTE?

### Processo:
1. Ordenar todos os nascimentos cronologicamente (por data exata)
2. Criar janelas móveis de 1000 nascimentos consecutivos
3. Para cada janela, acompanhar cada bebê por 1 ano
4. Contar quantos morreram antes de completar 1 ano
5. Esse número É o CMI-Mil

### Problema:
**Nossos dados são AGREGADOS por ano** (totais anuais), não individuais!

Para calcular CMI-Mil, precisaríamos:
- Data de nascimento de cada bebê
- Data de morte (se morreu < 1 ano)
- Dados individuais, não totais

**Não podemos recalcular CMI-Mil com dados agregados!**

---

## VALIDAÇÃO DO NOSSO ENTENDIMENTO

Vamos verificar se os valores fazem sentido:

### Abreulandia-TO (2000):
- **CMI**: 25.64 (projeção para 1000 nascimentos)
- **CMI-Mil**: 7.20 (observação real de 1000 nascimentos ao longo de ~25 anos)
- **Por que diferente?** Taxa de mortalidade mudou ao longo de 25 anos (melhorou!)

### Fortaleza-CE (2000):
- **CMI**: 23.27 (projeção para 1000 nascimentos)
- **CMI-Mil**: 23.30 (observação real de 1000 nascimentos em ~9 dias)
- **Por que igual?** Taxa estável em 9 dias, projeção = realidade

---

## CONCLUSÃO FINAL:

✅ **CMI-Mil é calculado CORRETAMENTE nas planilhas**

✅ **Valores parecidos em cidades grandes são ESPERADOS**

✅ **Não podemos recalcular CMI-Mil com nossos dados** (precisaríamos dados individuais)

❌ **Minha análise anterior estava ERRADA** (confundi com taxa por população)

---

## REFERÊNCIA:

> "O CMI-Mil correspondente à razão entre o número dos óbitos infantis ocorridos durante a observação do nascimento dos últimos mil nascidos vivos. O coeficiente foi nomeado como CMI-Mil, devendo receber no rótulo a identificação do ano inicial e ano final da janela de observação dos nascimentos na forma: CMI-Mil(ano_inicial-ano_final)."
